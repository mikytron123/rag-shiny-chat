from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import MarkdownNodeParser
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams
from constants import collection_name
import os

QDRANT_HOST = os.getenv("QDRANT_HOST", default="localhost")


def load_db():
    client = QdrantClient(url=f"http://{QDRANT_HOST}:6333")

    if client.collection_exists(collection_name):
        return

    documents = SimpleDirectoryReader("documents", recursive=True).load_data()

    splitter = MarkdownNodeParser()

    nodes = splitter.get_nodes_from_documents(documents, show_progress=True)

    node_txt = [node.get_text() for node in nodes]

    metadata_lst = []
    word = "documents"
    url = "https://docs.pola.rs/user-guide"

    for node in nodes:
        meta = node.metadata
        file_path = node.metadata["file_path"]
        start_idx = file_path.find(word) + len(word)
        link = url + file_path[start_idx:-8]
        meta = meta | {"link": link}

        metadata_lst.append(meta)

    model = SentenceTransformer(model_name_or_path="BAAI/bge-small-en-v1.5")
    embeddings = model.encode(
        node_txt, show_progress_bar=True, normalize_embeddings=True
    )

    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=model.get_sentence_embedding_dimension(),
                  distance=Distance.COSINE
            ),
        )

    client.upload_points(
        collection_name=collection_name,
        points=[
            models.PointStruct(
                id=idx,
                vector=embeddings[idx].tolist(),
                payload=({"metadata": metadata_lst[idx]} | {"text": node_txt[idx]}),
            )
            for idx, doc in enumerate(documents)
        ],
    )
