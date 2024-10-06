from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import MarkdownNodeParser
import weaviate
from constants import collection_name
from teiembedding import TextEmbeddingsInference
import os
import pandas as pd

WEAVIATE_HOST = os.getenv("WEAVIATE_HOST", default="localhost")
WEAVIATE_PORT = os.getenv("WEAVIATE_PORT")
TEI_HOST = os.getenv("TEI_HOST", default="localhost")
TEI_PORT = os.getenv("TEI_PORT")

def load_db():
    client = weaviate.connect_to_local(host=WEAVIATE_HOST, port=int(WEAVIATE_PORT))

    if client.collections.exists(collection_name):
        collection = client.collections.get(collection_name)
        count = 0
        for _ in collection.iterator():
            count += 1
        if count > 0:
            client.close()
            return

    documents = SimpleDirectoryReader("documents", recursive=True).load_data()

    splitter = MarkdownNodeParser()

    nodes = splitter.get_nodes_from_documents(documents, show_progress=True)

    texts = [node.get_text() for node in nodes]

    metadata_lst = []
    word = "documents"
    url = "https://docs.pola.rs/user-guide"

    for node in nodes:
        meta = node.metadata | {"text": node.get_text()}
        file_path = node.metadata["file_path"]
        start_idx = file_path.find(word) + len(word)
        link = url + file_path[start_idx:-8]
        meta = meta | {"link": link}

        metadata_lst.append(meta)

    documents = client.collections.get(collection_name)

    tei_url = f"http://{TEI_HOST}:{TEI_PORT}"
    embedding_model = TextEmbeddingsInference(url=tei_url, normalize=True)
    embeddings = embedding_model.embed_documents(texts)

    # Enter context manager
    with documents.batch.dynamic() as batch:
        # Loop through the data
        for idx, doc in enumerate(metadata_lst):
            # Convert data types

            for k, v in doc.items():
                if "date" in k:
                    doc[k] = pd.to_datetime(v).to_pydatetime()

            # Add object to batch queue
            batch.add_object(properties=doc, vector=embeddings[idx])
            # Batcher automatically sends batches

    # Check for failed objects
    if len(documents.batch.failed_objects) > 0:
        print(f"Failed to import {len(documents.batch.failed_objects)} objects")

    client.close()
