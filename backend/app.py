from dataclasses import dataclass
from typing import AsyncGenerator


from langchain_community.llms import Ollama
from litestar import Litestar, post, get
from litestar.response import Stream
from litestar.datastructures import State
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from utils import get_num_tokens
from shared.api_models import LlmCompletionSchema, ModelSchema
from litestar.serialization import encode_json
from litestar.contrib.opentelemetry import OpenTelemetryConfig, OpenTelemetryPlugin
from constants import system_prompt, collection_name, alpha, k
from langchain_weaviate.vectorstores import WeaviateVectorStore
import os
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


OLLAMA_HOST = os.getenv("OLLAMA_HOST", default="localhost")
OLLAMA_PORT = os.getenv("OLLAMA_PORT")
WEAVIATE_HOST = os.getenv("WEAVIATE_HOST", default="localhost")
WEAVIATE_PORT = os.getenv("WEAVIATE_PORT")
TEI_HOST = os.getenv("TEI_HOST", default="localhost")
TEI_PORT = os.getenv("TEI_PORT")
LANGFUSE_PORT = os.getenv("LANGFUSE_PORT")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST")

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
}

langfuse_handler = CallbackHandler(
    public_key=os.getenv("LANGFUSE_PROJECT_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_PROJECT_SECRET_KEY"),
    host=f"http://{LANGFUSE_HOST}:{LANGFUSE_PORT}",
)


@dataclass
class Parameters:
    model: str
    temperature: float
    prompt: str


def on_startup(app: Litestar):
    app.state.db_client = weaviate.connect_to_local(
        host=WEAVIATE_HOST, port=int(WEAVIATE_PORT)
    )
    app.state.ollama_client = ollama.Client(host=f"http://{OLLAMA_HOST}:{OLLAMA_PORT}")


def on_shutdown(app: Litestar):
    client = app.state.client
    client.close()


def create_chain(state: State, data: Parameters):
    client = state.db_client
    tei_url = f"http://{TEI_HOST}:{TEI_PORT}"
    embeddings = TextEmbeddingsInference(url=tei_url, normalize=True)
    db = WeaviateVectorStore(
        client=client, index_name=collection_name, text_key="text", embedding=embeddings
    )
    query_embedding = embeddings.embed_query(data.prompt)
    retriever = db.as_retriever(
        search_kwargs=dict(alpha=alpha, k=k, vector=query_embedding)
    )
    llm = Ollama(
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
    return chain, llm


async def llm_generator(state: State, data: Parameters) -> AsyncGenerator[bytes, None]:
    chain, llm = create_chain(state, data)
    link_dict = {}
    metrics_dist["genai_requests"].add(
        1,
    )
    metrics_dist["db_requests"].add(1)

    num_input_tokens = get_num_tokens(state.ollama_client, data.model, data.prompt)
    metrics_dist["genai_prompt_tokens"].add(num_input_tokens)

    num_output_tokens = 0

    async for chunk in chain.astream(
        {"input": data.prompt}, config={"callbacks": [langfuse_handler]}
    ):
        if "answer" in chunk:
            yield encode_json({"completion": chunk["answer"]})
            num_output_tokens += 1
        elif "context" in chunk:
            link_dict = {
                "links": list({doc.metadata["link"] for doc in chunk["context"]})
            }
    metrics_dist["genai_completion_tokens"].add(num_output_tokens)
    metrics_dist["genai_total_tokens"].add(num_input_tokens + num_output_tokens)
    metrics_dist["db_requests"].add(1)
    yield encode_json(link_dict)


@post("/llm/stream")
async def post_llm_stream(state: State, data: Parameters) -> Stream:
    return Stream(llm_generator(state, data))


@get("models")
async def get_models(state: State) -> ModelSchema:
    client = state.ollama_client
    models_req = client.list()
    choices = [dd["name"] for dd in models_req["models"]]

    return ModelSchema(models=choices)


@post("/llm/invoke")
async def post_llm(state: State, data: Parameters) -> LlmCompletionSchema:
    try:
        num_input_tokens = get_num_tokens(state.ollama_client, data.model, data.prompt)
        chain, llm = create_chain(state, data)
        # with tracer.start_as_current_span(name="langchain") as span:
        #     span.set_attribute("genai.request.model", llm.model)
        #     for attr in ["temperature", "top_p", "top_k"]:
        #         val = llm._default_params["options"][attr]
        #         if val is None:
        #             val = "default"
        #         span.set_attribute(f"genai.request.{attr}", val)

        #     span.set_attribute("gen_ai.request.is_stream", False)
        #     span.set_attribute("gen_ai.usage.input_tokens", num_input_tokens)
        ans = chain.invoke(
            {"input": data.prompt}, config={"callbacks": [langfuse_handler]}
        )

        num_output_tokens = get_num_tokens(
            state.ollama_client, data.model, ans["answer"]
        )

        # span.set_attribute("gen_ai.usage.output_tokens", num_output_tokens)
        # span.set_attribute(
        #     "gen_ai.usage.total_tokens", num_input_tokens + num_output_tokens
        # )

        # span.add_event(
        #     name="genai.content.prompt", attributes={"genai.prompt": data.prompt}
        # )
        # span.add_event(
        #     name="genai.content.completion",
        #     attributes={"genai.completion": ans["answer"]},
        # )

        metrics_dist["genai_requests"].add(
            1,
        )

        metrics_dist["genai_prompt_tokens"].add(num_input_tokens)
        metrics_dist["genai_completion_tokens"].add(num_output_tokens)

        metrics_dist["genai_total_tokens"].add(num_input_tokens + num_output_tokens)
        metrics_dist["db_requests"].add(1)
        return LlmCompletionSchema(completion=ans["answer"])
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        return LlmCompletionSchema(completion="")


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
