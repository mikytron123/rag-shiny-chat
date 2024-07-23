from dataclasses import dataclass
from typing import AsyncGenerator, Any

import requests
from langchain_community.llms import Ollama
from litestar import Litestar, post, get
from litestar.response import Stream
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from litestar.serialization import encode_json
from weaviate import WeaviateClient

from constants import system_prompt, collection_name
from load_weaviate import load_db
from langchain_weaviate.vectorstores import WeaviateVectorStore
import os
import weaviate
from teiembedding import TextEmbeddingsInference
import traceback

OLLAMA_HOST = os.getenv("OLLAMA_HOST", default="localhost")
WEAVIATE_HOST = os.getenv("WEAVIATE_HOST", default="localhost")
TEI_HOST = os.getenv("TEI_HOST", default="localhost")


@dataclass
class Parameters:
    model: str
    temperature: float
    prompt: str


def create_chain(data: Parameters) -> tuple[Any, WeaviateClient]:
    client = weaviate.connect_to_local(host=WEAVIATE_HOST, port=8090)
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
    return chain, client


async def llm_generator(data: Parameters) -> AsyncGenerator[bytes, None]:
    llm, client = create_chain(data)
    link_dict = {}
    async for chunk in llm.astream({"input": data.prompt}):
        if "answer" in chunk:
            yield encode_json({"completion": chunk["answer"]})
        elif "context" in chunk:
            link_dict = {"links": list({doc.metadata["link"] for doc in chunk["context"]})}
            
    yield encode_json(link_dict)
    
    client.close()


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
    try:
        chain, client = create_chain(data)
        ans = chain.invoke({"input": data.prompt})
        client.close()
        return {"completion": ans["answer"]}
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        return {}


load_db()
app = Litestar([get_models, post_llm, post_llm_stream])
