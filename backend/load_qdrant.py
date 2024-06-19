from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import MarkdownNodeParser
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams


def load_db():

    client = QdrantClient(url="http://qdrant:6333")
    collection_name = "document_collection"
    if client.collection_exists(collection_name):
        return

    documents = SimpleDirectoryReader("documents", recursive=True).load_data()
    splitter = MarkdownNodeParser()

    nodes = splitter.get_nodes_from_documents(documents, show_progress=True)

    node_txt = [node.get_text() for node in nodes]
    metadata_lst = [node.metadata | {"text": node.get_text()} for node in nodes]

    model = SentenceTransformer(
        "/tmp/models--BAAI--bge-small-en-v1.5/snapshots/5c38ec7c405ec4b44b94cc5a9bb96e735b38267a"
    )
    embeddings = model.encode(node_txt, show_progress_bar=True)

    if client.collection_exists(collection_name) == False:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE
            ),
        )

    client.upload_points(
        collection_name=collection_name,
        points=[
            models.PointStruct(
                id=idx, vector=embeddings[idx].tolist(), payload=metadata_lst[idx]
            )
            for idx, doc in enumerate(documents)
        ],
    )
