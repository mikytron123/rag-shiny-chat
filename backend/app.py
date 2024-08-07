from dataclasses import dataclass
from typing import AsyncGenerator

import requests
from langchain_community.llms import Ollama
from litestar import Litestar, post, get
from litestar.response import Stream
from litestar.datastructures import State
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from shared.api_models import LlmCompletionSchema, ModelSchema
from litestar.serialization import encode_json

from constants import system_prompt, collection_name
from load_weaviate import load_db
from langchain_weaviate.vectorstores import WeaviateVectorStore
import os
import weaviate
from teiembedding import TextEmbeddingsInference

OLLAMA_HOST = os.getenv("OLLAMA_HOST", default="localhost")
WEAVIATE_HOST = os.getenv("WEAVIATE_HOST", default="localhost")
TEI_HOST = os.getenv("TEI_HOST", default="localhost")


@dataclass
class Parameters:
    model: str
    temperature: float
    prompt: str


def on_startup(app: Litestar):
    app.state.client = weaviate.connect_to_local(host=WEAVIATE_HOST, port=8090)


def on_shutdown(app: Litestar):
    client = app.state.client
    client.close()


def create_chain(state: State, data: Parameters):
    client = state.client
    tei_url = f"http://{TEI_HOST}:8080"
    embeddings = TextEmbeddingsInference(url=tei_url, normalize=True)
    db = WeaviateVectorStore(
        client=client, index_name=collection_name, text_key="text", embedding=embeddings
    )
    query_embedding = embeddings.embed_query(data.prompt)
    print()
    retriever = db.as_retriever(
        search_kwargs=dict(alpha=0.5, k=4, vector=query_embedding)
    )
    llm = Ollama(
        base_url=f"http://{OLLAMA_HOST}:11434",
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


async def llm_generator(state: State, data: Parameters) -> AsyncGenerator[bytes, None]:
    llm = create_chain(state, data)
    link_dict = {}
    async for chunk in llm.astream({"input": data.prompt}):
        if "answer" in chunk:
            yield encode_json({"completion": chunk["answer"]})
        elif "context" in chunk:
            link_dict = {
                "links": list({doc.metadata["link"] for doc in chunk["context"]})
            }
    yield encode_json(link_dict)


@post("/llm/stream")
async def post_llm_stream(state: State, data: Parameters) -> Stream:
    return Stream(llm_generator(state, data))


@get("models")
async def get_models() -> ModelSchema:
    models_req = requests.get(f"http://{OLLAMA_HOST}:11434/api/tags").json()
    choices = [dd["name"] for dd in models_req["models"]]
    return ModelSchema(models=choices)


@post("/llm/invoke")
async def post_llm(state: State, data: Parameters) -> LlmCompletionSchema:
    chain = create_chain(state, data)
    ans = chain.invoke({"input": data.prompt})
    return LlmCompletionSchema(completion=ans["answer"])


load_db()
app = Litestar(
    [get_models, post_llm, post_llm_stream],
    on_startup=[on_startup],
    on_shutdown=[on_shutdown],
)
