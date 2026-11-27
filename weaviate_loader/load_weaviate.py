from dataclasses import replace
from time import perf_counter, sleep
from typing import Any

import httpx2
import pandas as pd
from constants import DOCUMENT_COLLECTION_PROPERTIES
from appconfig import config
from haystack.dataclasses.document import Document
from haystack_integrations.components.embedders.huggingface_api import (
    HuggingFaceAPIDocumentEmbedder,
)
from haystack_integrations.document_stores.weaviate import WeaviateDocumentStore
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core.schema import MetadataMode

# from teiembedding import TextEmbeddingsInference

WEAVIATE_HOST = config.weaviate_host
WEAVIATE_PORT = config.weaviate_port
TEI_HOST = config.tei_host
TEI_PORT = config.tei_port
EMBEDDING_MODEL = config.model


def wait_for_service(url: str, service: str, timeout: int = 300) -> None:
    deadline = perf_counter() + timeout
    last_error = None

    while perf_counter() < deadline:
        try:
            response = httpx2.get(url, timeout=5)
            if response.status_code == 200:
                return
            last_error = RuntimeError(f"HTTP {response.status_code}")
        except httpx2.ConnectError as error:
            last_error = error
        sleep(2)

    raise TimeoutError(
        f"{service} did not become ready at {url} within {timeout} seconds"
    ) from last_error


def load_db():
    collection_name = "document_collection"
    weaviate_url = f"http://{WEAVIATE_HOST}:{WEAVIATE_PORT}"
    wait_for_service(f"{weaviate_url}/v1/.well-known/ready", "Weaviate")
    tei_url = f"http://{TEI_HOST}:{TEI_PORT}"


    weaviate_store = WeaviateDocumentStore(
        url=weaviate_url,
        collection_settings={
            "class": collection_name,
            "properties": DOCUMENT_COLLECTION_PROPERTIES,
            "vectorIndexType": "hnsw",
            "vectorIndexConfig": {"distance": "cosine"},
            "vectorizer": "none",
        },
    )
    num_documents = weaviate_store.count_documents()
    if num_documents > 0:
        return

    wait_for_service(f"{tei_url}/health", "Text Embeddings Inference")
    documents = SimpleDirectoryReader("documents", recursive=True).load_data()

    splitter = MarkdownNodeParser()

    nodes = splitter.get_nodes_from_documents(documents, show_progress=True)

    texts = [node.get_content(metadata_mode=MetadataMode.NONE) for node in nodes]

    metadata_lst: list[dict[str, Any]] = []
    word = "documents"
    url = "https://docs.pola.rs/user-guide"

    for node in nodes:
        node_text = node.get_content(metadata_mode=MetadataMode.NONE)
        meta = node.metadata | {
            "text": node_text
        }
        for date_field in ("creation_date", "last_modified_date"):
            if meta.get(date_field) is not None:
                meta[date_field] = pd.to_datetime(
                    meta[date_field], utc=True
                ).to_pydatetime()
        file_path = node.metadata["file_path"]
        start_idx = file_path.find(word) + len(word)
        link = url + file_path[start_idx:-8]
        meta = meta | {"link": link} | {"embedding_model": EMBEDDING_MODEL}

        metadata_lst.append(meta)

    text_embedder = HuggingFaceAPIDocumentEmbedder(
        api_type="text_embeddings_inference",
        api_params={"url": tei_url},
    )
    docs_lst = [Document(content=text) for text in texts]
    docs_lst = text_embedder.run(documents=docs_lst)["documents"]

    docs_lst = [
        replace(document, meta=metadata)
        for document, metadata in zip(docs_lst, metadata_lst)
    ]

    weaviate_store.write_documents(docs_lst)


if __name__ == "__main__":
    load_db()
