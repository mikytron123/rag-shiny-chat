import io
from pydantic import BaseModel, Field
from typing import AsyncGenerator
from langchain_ollama import OllamaLLM
from litestar import Litestar, post, get
from litestar.response import Stream
from litestar.datastructures import State
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from utils import get_num_tokens
from redistore import RedisStore
from shared.api_models import LlmCompletionSchema, ModelSchema
from litestar.serialization import encode_json
from litestar.contrib.opentelemetry import OpenTelemetryConfig, OpenTelemetryPlugin
from litestar.exceptions import HTTPException
from constants import system_prompt, collection_name, alpha, k
from langchain_weaviate.vectorstores import WeaviateVectorStore
import ollama
import traceback
import weaviate
from teiembedding import TextEmbeddingsInference
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from langfuse.callback import CallbackHandler
from appconfig import config
from weaviatestore import WeaviateStore

OLLAMA_HOST = config.ollama_host
OLLAMA_PORT = config.ollama_port
WEAVIATE_HOST = config.weaviate_host
WEAVIATE_PORT = config.weaviate_port
TEI_HOST = config.tei_host
TEI_PORT = config.tei_port
LANGFUSE_HOST = config.langfuse_host
LANGFUSE_PORT = config.langfuse_port
REDIS_HOST = config.redis_host
REDIS_PORT = config.redis_port

resource = Resource(attributes={SERVICE_NAME: "ragproject"})


reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint="http://alloy:4318/v1/metrics")
)

meterProvider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(meterProvider)

meter = metrics.get_meter("ragproject.backend")

# HTTPXClientInstrumentor(tracer_provider=traceProvider).instrument()


application_name = "ragproject"
otlp_endpoint = "http://alloy:4318"
metrics_dist = {
    "genai_requests": meter.create_counter(
        name="genai.total.requests",
        description="Number of requests to GenAI",
        unit="1",
    ),
    "genai_prompt_tokens": meter.create_counter(
        name="genai.usage.input.tokens",
        description="Number of prompt tokens processed.",
        unit="1",
    ),
    "genai_completion_tokens": meter.create_counter(
        name="genai.usage.completion.tokens",
        description="Number of completion tokens processed.",
        unit="1",
    ),
    "genai_total_tokens": meter.create_counter(
        name="genai.usage.total.tokens",
        description="Number of total tokens processed.",
        unit="1",
    ),
    "db_requests": meter.create_counter(
        name="db.total.requests",
        description="Number of requests to VectorDBs",
        unit="1",
    ),
    "cache_requests": meter.create_counter(
        name="cache.total.requests",
        description="Number of requests to Cache",
        unit="1"
    )
}

langfuse_handler = CallbackHandler(
    public_key=config.langfuse_project_public_key,
    secret_key=config.langfuse_project_secret_key,
    host=f"http://{LANGFUSE_HOST}:{LANGFUSE_PORT}",
)


class Parameters(BaseModel):
    model: str
    temperature: float = Field(..., ge=0)
    prompt: str


def on_startup(app: Litestar):
    db_client = weaviate.connect_to_local(host=WEAVIATE_HOST, port=(WEAVIATE_PORT))
    tei_url = f"http://{TEI_HOST}:{TEI_PORT}"
    tei_client = TextEmbeddingsInference(url=tei_url, normalize=True)

    app.state.db_client = WeaviateStore(
        weaviate_client=db_client, tei_client=tei_client
    )
    app.state.ollama_client = ollama.Client(host=f"http://{OLLAMA_HOST}:{OLLAMA_PORT}")
    app.state.redis_client = RedisStore(host=REDIS_HOST, port=REDIS_PORT)


def on_shutdown(app: Litestar):
    client: WeaviateStore = app.state.db_client
    client.close()


def create_chain(data: Parameters):
    """ Creates langchain rag chain
    """
    client = weaviate.connect_to_local(host=WEAVIATE_HOST, port=(WEAVIATE_PORT))
    tei_url = f"http://{TEI_HOST}:{TEI_PORT}"
    embeddings = TextEmbeddingsInference(url=tei_url, normalize=True)
    
    db = WeaviateVectorStore(
        client=client, index_name=collection_name, text_key="text", embedding=embeddings
    )
    query_embedding = embeddings.embed_query(data.prompt)
    retriever = db.as_retriever(
        search_kwargs=dict(alpha=alpha, k=k, vector=query_embedding)
    )
    
    llm = OllamaLLM(
        base_url=f"http://{OLLAMA_HOST}:{OLLAMA_PORT}",
        model=data.model,
        temperature=data.temperature,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    chain = create_retrieval_chain(retriever, question_answer_chain)
    return chain


async def llm_generator(
    state: State, data: Parameters
) -> AsyncGenerator[bytes, None]:
    vec_db_client: WeaviateStore = state.db_client
    result = vec_db_client.search_vector_cache(data.prompt)
    redis_client: RedisStore = state.redis_client

    if len(result) == 0:
        vec_db_client.insert_vector_cache(data.prompt)
    else:
        cached_data = redis_client.retrieve_data(result[0])

        metrics_dist["cache_requests"].add(1)
        completion: str = cached_data.completion
        link_list: list[str] = cached_data.links

        # for token in completion.split():
        #     yield encode_json({"completion": token})
        yield encode_json({"completion": completion})
        yield encode_json({"links": link_list})

        return

    chain = create_chain(data)
    link_dict = {}
    metrics_dist["genai_requests"].add(
        1,
    )
    metrics_dist["db_requests"].add(1)

    num_input_tokens = get_num_tokens(state.ollama_client, data.model, data.prompt)
    metrics_dist["genai_prompt_tokens"].add(num_input_tokens)

    num_output_tokens = 0
    completion = ""
    string_buffer = io.StringIO()
    async for chunk in chain.astream(
        {"input": data.prompt}, config={"callbacks": [langfuse_handler]}
    ):
        if "answer" in chunk:
            yield encode_json({"completion": chunk["answer"]})
            num_output_tokens += 1
            string_buffer.write(chunk["answer"])
        elif "context" in chunk:
            link_dict = {
                "links": list({doc.metadata["link"] for doc in chunk["context"]})
            }

    metrics_dist["genai_completion_tokens"].add(num_output_tokens)
    metrics_dist["genai_total_tokens"].add(num_input_tokens + num_output_tokens)
    metrics_dist["db_requests"].add(1)

    completion = string_buffer.getvalue()
    redis_value = {"completion": completion} | link_dict
    redis_client.store_data(data.prompt, redis_value)

    yield encode_json(link_dict)


@post("/llm/stream")
async def post_llm_stream(state: State, data: Parameters) -> Stream:
    return Stream(llm_generator(state, data))


@get("models")
async def get_models(state: State) -> ModelSchema:
    client: ollama.Client = state.ollama_client
    models_req = client.list()
    choices = [dd.model for dd in models_req.models if dd.model is not None]
    return ModelSchema(models=choices)


@post("/llm/invoke")
async def post_llm(state: State, data: Parameters) -> LlmCompletionSchema:
    try:
        vec_db_client: WeaviateStore = state.db_client
        result = vec_db_client.search_vector_cache(data.prompt)
        redis_client: RedisStore = state.redis_client

        if len(result) == 0:
            vec_db_client.insert_vector_cache(data.prompt)
        else:
            cached_data = redis_client.retrieve_data(result[0])
            metrics_dist["cache_requests"].add(1)
            return cached_data

        num_input_tokens = get_num_tokens(state.ollama_client, data.model, data.prompt)
        chain = create_chain(data)
        ans = chain.invoke(
            {"input": data.prompt}, config={"callbacks": [langfuse_handler]}
        )

        num_output_tokens = get_num_tokens(
            state.ollama_client, data.model, ans["answer"]
        )

        metrics_dist["genai_requests"].add(
            1,
        )

        metrics_dist["genai_prompt_tokens"].add(num_input_tokens)
        metrics_dist["genai_completion_tokens"].add(num_output_tokens)

        metrics_dist["genai_total_tokens"].add(num_input_tokens + num_output_tokens)
        metrics_dist["db_requests"].add(1)
        links_list = list({doc.metadata["link"] for doc in ans["context"]})

        redis_value = {"completion": ans["answer"], "links": links_list}
        redis_client.store_data(input_string=data.prompt, value=redis_value)

        return LlmCompletionSchema(completion=ans["answer"], links=links_list)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


open_telemetry_config = OpenTelemetryConfig(
    meter_provider=meterProvider
    # tracer_provider=traceProvider, meter_provider=meterProvider
)
app = Litestar(
    [get_models, post_llm, post_llm_stream],
    on_startup=[on_startup],
    on_shutdown=[on_shutdown],
    plugins=[OpenTelemetryPlugin(open_telemetry_config)],
)
