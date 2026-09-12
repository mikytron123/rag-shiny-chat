import io
from collections.abc import AsyncGenerator

from appconfig import config
from constants import alpha, collection_name, k, system_prompt
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.config import RunnableConfig
from langchain_ollama import OllamaLLM
from langchain_weaviate.vectorstores import WeaviateVectorStore
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.retrieval import create_retrieval_chain
from litestar import Litestar, get, post
from litestar.datastructures import State
from litestar.exceptions import HTTPException
from litestar.response import Stream
from litestar.serialization import encode_json
from pydantic import BaseModel, Field
from redistore import RedisStore
from shared.api_models import LlmCompletionSchema, ModelSchema
from teiembedding import TextEmbeddingsInference
from telemetry import Telemetry
from utils import get_num_tokens
from weaviatestore import WeaviateStore

import ollama
import weaviate

OLLAMA_HOST = config.ollama_host
OLLAMA_PORT = config.ollama_port
WEAVIATE_HOST = config.weaviate_host
WEAVIATE_PORT = config.weaviate_port
TEI_HOST = config.tei_host
TEI_PORT = config.tei_port
REDIS_HOST = config.redis_host
REDIS_PORT = config.redis_port
EMBEDDING_MODEL = config.model
LLM = config.llm
TELEMETRY_ENABLED = config.telemetry_enabled


class Parameters(BaseModel):
    model: str
    temperature: float = Field(..., ge=0)
    prompt: str


def on_startup(app: Litestar):
    """Initializes database and clients on startup"""

    app.state.telemetry = Telemetry()
    app.state.telemetry.initialize()

    # Initialize database clients, embedding model, LLM, and guardrails
    db_client = weaviate.connect_to_local(host=WEAVIATE_HOST, port=(WEAVIATE_PORT))
    tei_url = f"http://{TEI_HOST}:{TEI_PORT}"
    tei_client = TextEmbeddingsInference(url=tei_url, normalize=True)

    app.state.db_client = WeaviateStore(
        weaviate_client=db_client,
        tei_client=tei_client,
        embedding_model=EMBEDDING_MODEL,
        llm=LLM,
    )
    app.state.ollama_client = ollama.Client(host=f"http://{OLLAMA_HOST}:{OLLAMA_PORT}")
    app.state.redis_client = RedisStore(host=REDIS_HOST, port=REDIS_PORT)


def on_shutdown(app: Litestar):
    client: WeaviateStore = app.state.db_client
    client.close()


def create_chain(data: Parameters):
    """Creates langchain rag chain"""
    client = weaviate.connect_to_local(host=WEAVIATE_HOST, port=(WEAVIATE_PORT))
    tei_url = f"http://{TEI_HOST}:{TEI_PORT}"
    embeddings = TextEmbeddingsInference(url=tei_url, normalize=True)

    db = WeaviateVectorStore(
        client=client, index_name=collection_name, text_key="text", embedding=embeddings
    )
    query_embedding = embeddings.embed_query(data.prompt)
    retriever = db.as_retriever(
        search_kwargs={"alpha": alpha, "k": k, "vector": query_embedding}
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


def retreive_cache(
    vec_db_client: WeaviateStore, redis_client: RedisStore, prompt: str
) -> LlmCompletionSchema | None:
    """Retrieves cached response if available"""

    result = vec_db_client.search_vector_cache(prompt)
    if len(result) == 0:
        vec_db_client.insert_vector_cache(prompt)
        return

    cached_data = redis_client.retrieve_data(result[0])
    return cached_data


async def llm_generator(
    state: State,
    data: Parameters,
) -> AsyncGenerator[bytes, None]:
    """Generator function to stream LLM responses"""

    telemetry = state.telemetry
    langfuse_handler = telemetry.get_langfuse_handler()

    vec_db_client: WeaviateStore = state.db_client
    redis_client: RedisStore = state.redis_client

    cached_data = retreive_cache(vec_db_client, redis_client, data.prompt)
    if cached_data is not None:
        telemetry.record_cache_request()

        completion: str = cached_data.completion
        link_list: list[str] = cached_data.links

        # for token in completion.split():
        #     yield encode_json({"completion": token})
        yield encode_json({"completion": completion})
        yield encode_json({"links": link_list})

        return

    chain = create_chain(data)
    link_dict = {}

    num_input_tokens = get_num_tokens(state.ollama_client, data.model, data.prompt)
    telemetry.record_prompt_tokens(num_input_tokens)

    num_output_tokens = 0
    completion = ""
    string_buffer = io.StringIO()

    if langfuse_handler is None:
        config = None
    else:
        config = RunnableConfig(callbacks=[langfuse_handler])

    async for chunk in chain.astream(
        {"input": data.prompt},
        config=config,
    ):
        if "answer" in chunk:
            yield encode_json({"completion": chunk["answer"]})
            num_output_tokens += 1
            string_buffer.write(chunk["answer"])
        elif "context" in chunk:
            link_dict = {
                "links": list({doc.metadata["link"] for doc in chunk["context"]})
            }

    telemetry.record_genai_metrics(
        input_tokens=num_input_tokens,
        output_tokens=num_output_tokens,
    )

    completion = string_buffer.getvalue()
    redis_value = {"completion": completion} | link_dict
    redis_client.store_data(data.prompt, redis_value)

    yield encode_json(link_dict)


@post("/llm/stream", sync_to_thread=False)
async def post_llm_stream(
    state: State,
    data: Parameters,
) -> Stream:
    return Stream(llm_generator(state, data))


@get("models")
async def get_models(state: State) -> ModelSchema:
    client: ollama.Client = state.ollama_client
    models_req = client.list()
    choices = [dd.model for dd in models_req.models if dd.model is not None]
    return ModelSchema(models=choices)


@post("/llm/invoke", sync_to_thread=False)
async def post_llm(
    state: State,
    data: Parameters,
) -> LlmCompletionSchema:
    try:
        telemetry = state.telemetry
        langfuse_handler = telemetry.get_langfuse_handler()

        vec_db_client: WeaviateStore = state.db_client
        redis_client: RedisStore = state.redis_client

        cached_data = retreive_cache(vec_db_client, redis_client, data.prompt)

        if cached_data is not None:
            telemetry.record_cache_request()
            return cached_data

        num_input_tokens = get_num_tokens(state.ollama_client, data.model, data.prompt)
        chain = create_chain(data)

        if langfuse_handler is None:
            config = None
        else:
            config = RunnableConfig(callbacks=[langfuse_handler])

        ans = chain.invoke({"input": data.prompt}, config=config)

        num_output_tokens = get_num_tokens(
            state.ollama_client, data.model, ans["answer"]
        )
        telemetry.record_genai_metrics(
            input_tokens=num_input_tokens,
            output_tokens=num_output_tokens,
        )

        links_list = list({doc.metadata["link"] for doc in ans["context"]})

        redis_value = {"completion": ans["answer"], "links": links_list}
        redis_client.store_data(input_string=data.prompt, value=redis_value)

        return LlmCompletionSchema(completion=ans["answer"], links=links_list)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


telemetry = Telemetry()
plugins = telemetry.get_plugins()

app = Litestar(
    [get_models, post_llm, post_llm_stream],
    on_startup=[on_startup],
    on_shutdown=[on_shutdown],
    plugins=plugins,
)
