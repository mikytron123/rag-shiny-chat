from dataclasses import dataclass
import requests
from langchain_community.llms import Ollama
from litestar import Litestar, post, get

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from langchain_qdrant import Qdrant
from constants import system_prompt, collection_name
from langchain_huggingface import HuggingFaceEmbeddings
from load_qdrant import load_db
import os

OLLAMA_HOST = os.getenv("OLLAMA_HOST")
QDRANT_HOST = os.getenv("QDRANT_HOST")

@dataclass
class Parameters:
    model: str
    temperature: float
    prompt: str


@get("models")
async def get_models() -> dict[str, str]:
    models_req = requests.get(f"http://{OLLAMA_HOST}:11434/api/tags").json()
    choices_dict = {dd["name"]: dd["name"] for dd in models_req["models"]}
    return choices_dict


@post("/llm")
async def post_llm(data: Parameters) -> dict[str, str]:
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    qdrant = Qdrant.from_existing_collection(
        embedding=embeddings,
        collection_name=collection_name,
        url=f"http://{QDRANT_HOST}:6333",
        content_payload_key="text",
    )
    retriever = qdrant.as_retriever(search_kwargs={"k": 4})
    llm = Ollama(
        base_url=f"http://{OLLAMA_HOST}:11434", model=data.model, temperature=data.temperature
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    chain = create_retrieval_chain(retriever, question_answer_chain)
    ans = chain.invoke({"input": data.prompt})
    return {"completion": ans["answer"]}



load_db()
app = Litestar([post_llm])
