from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import MarkdownNodeParser
import weaviate
from weaviate.classes.config import Configure, VectorDistances, DataType, Property
from constants import collection_name
from teiembedding import TextEmbeddingsInference
import os
import pandas as pd

WEAVIATE_HOST = os.getenv("WEAVIATE_HOST", default="localhost")
TEI_HOST = os.getenv("TEI_HOST", default="localhost")


def load_db():
    client = weaviate.connect_to_local(host=WEAVIATE_HOST, port=8090)

    if client.collections.exists(collection_name):
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

    properties = []
    for k, v in metadata_lst[0].items():
        name = k
        if "date" in k:
            data_type = DataType.DATE
        elif isinstance(v, str):
            data_type = DataType.TEXT
        elif isinstance(v, int):
            data_type = DataType.INT
        else:
            data_type = DataType.TEXT
        if k == "text":
            skip_vec = False
        else:
            skip_vec = True
        properties.append(
            Property(
                name=name,
                data_type=data_type,
                skip_vectorization=skip_vec,
                vectorize_property_name=False,
            )
        )
        
    if not client.collections.exists(collection_name):
        client.collections.create(
            name=collection_name,
            properties=properties,
            vectorizer_config=Configure.Vectorizer.none(),
            vector_index_config=Configure.VectorIndex.hnsw(
                distance_metric=VectorDistances.COSINE
            ),
        )

    documents = client.collections.get(collection_name)

    tei_url = f"http://{TEI_HOST}:8080"
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
