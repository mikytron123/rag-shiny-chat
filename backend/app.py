from dataclasses import dataclass
from typing import AsyncGenerator

import requests
from langchain_community.llms import Ollama
from langchain_core.runnables import Runnable
from litestar import Litestar, post, get
from litestar.response import Stream
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from langchain_qdrant import Qdrant
from litestar.serialization import encode_json

from constants import system_prompt, collection_name
from langchain_huggingface import HuggingFaceEmbeddings
from load_qdrant import load_db
import os

OLLAMA_HOST = os.getenv("OLLAMA_HOST", default="localhost")
QDRANT_HOST = os.getenv("QDRANT_HOST", default="localhost")


@dataclass
class Parameters:
    model: str
    temperature: float
    prompt: str


def create_chain(data: Parameters) -> Runnable:
    encode_kwargs = {"normalize_embeddings": True}
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5", encode_kwargs=encode_kwargs
    )
    qdrant = Qdrant.from_existing_collection(
        embedding=embeddings,
        collection_name=collection_name,
        url=f"http://{QDRANT_HOST}:6333",
        content_payload_key="text",
        metadata_payload_key="metadata",
    )
    retriever = qdrant.as_retriever(search_kwargs={"k": 4})
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


async def llm_generator(data: Parameters) -> AsyncGenerator[bytes, None]:
    llm = create_chain(data)
    async for chunk in llm.astream({"input": data.prompt}):
        if "answer" in chunk:
            yield encode_json({"completion": chunk["answer"]})
        elif "context" in chunk:
            yield encode_json(
                {"links": [doc.metadata["link"] for doc in chunk["context"]]}
            )
        else:
            yield encode_json({})


@post("/llm/stream")
async def post_llm_stream(data: Parameters) -> Stream:
    return Stream(llm_generator(data))


@get("models")
async def get_models() -> dict[str, str]:
    models_req = requests.get(f"http://{OLLAMA_HOST}:11434/api/tags").json()
    choices_dict = {dd["name"]: dd["name"] for dd in models_req["models"]}
    return choices_dict


@post("/llm")
async def post_llm(data: Parameters) -> dict[str, str]:
    chain = create_chain(data)
    ans = chain.invoke({"input": data.prompt})
    return {"completion": ans["answer"]}


load_db()
app = Litestar([get_models, post_llm, post_llm_stream])
