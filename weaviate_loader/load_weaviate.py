from typing import Any
from llama_index.core import SimpleDirectoryReader
from llama_index.core.schema import MetadataMode
from llama_index.core.node_parser import MarkdownNodeParser
import weaviate
from teiembedding import TextEmbeddingsInference

import pandas as pd
from appconfig import config

WEAVIATE_HOST = config.weaviate_host
WEAVIATE_PORT = config.weaviate_port
TEI_HOST = config.tei_host
TEI_PORT = config.tei_port
EMBEDDING_MODEL = config.model


def load_db():
    collection_name = "document_collection"
    client = None
    try:
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

        texts = [node.get_content(metadata_mode=MetadataMode.NONE) for node in nodes]

        metadata_lst: list[dict[str, Any]] = []
        word = "documents"
        url = "https://docs.pola.rs/user-guide"

        for node in nodes:
            node.get_content()
            meta = node.metadata | {
                "text": node.get_content(metadata_mode=MetadataMode.NONE)
            }
            file_path = node.metadata["file_path"]
            start_idx = file_path.find(word) + len(word)
            link = url + file_path[start_idx:-8]
            meta = meta | {"link": link} | {"embedding_model": EMBEDDING_MODEL}

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
                        doc[k] = pd.to_datetime(v,utc=True).to_pydatetime()

                # Add object to batch queue
                batch.add_object(properties=doc, vector=embeddings[idx])
                # Batcher automatically sends batches

        # Check for failed objects
        if len(documents.batch.failed_objects) > 0:
            print(f"Failed to import {len(documents.batch.failed_objects)} objects")
    except Exception as e:
        print(e)
    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    load_db()
