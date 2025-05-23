from pydantic import BaseModel, ConfigDict
import weaviate
from teiembedding import TextEmbeddingsInference
import datetime
from weaviate.classes.query import Filter
from constants import cache_collection_name


class WeaviateStore(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    weaviate_client: weaviate.WeaviateClient
    tei_client: TextEmbeddingsInference
    embedding_model: str
    llm: str

    def search_vector_cache(self, text: str) -> list[str]:
        """Searches vector cache for text

        Args:
            text: text to search

        Returns:
            List of matching text in the vector db
        """

        last_24h = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
            hours=24
        )
        filter_date = Filter.by_property("last_modified_date").greater_than(last_24h)
        filter_embedding = Filter.by_property("embedding_model").equal(
            self.embedding_model
        )
        filter_llm = Filter.by_property("llm").equal(self.llm)

        collection = self.weaviate_client.collections.get(cache_collection_name)

        vec = self.tei_client.embed_query(text)

        result = collection.query.near_vector(
            vec,
            certainty=0.95,
            limit=1,
            filters=(filter_date & filter_embedding & filter_llm),
        )
        if len(result.objects) == 0:
            return []
        update_id = result.objects[0].uuid

        collection.data.update(
            uuid=update_id,
            properties={
                "last_modified_date": datetime.datetime.now(datetime.timezone.utc)
            },
        )
        return [str(result.objects[0].properties["query"])]

    def insert_vector_cache(self, text: str) -> None:
        """Insert vector embedding of text into vector db

        Args:
            text: string to store into db

        """
        vec = self.tei_client.embed_query(text)

        collection = self.weaviate_client.collections.get(cache_collection_name)
        current_time = datetime.datetime.now(datetime.timezone.utc)
        property = {
            "query": text,
            "created_on": current_time,
            "last_modified_date": current_time,
            "embedding_model": self.embedding_model,
            "llm": self.llm,
        }
        with collection.batch.dynamic() as batch:
            # Add object to batch queue
            batch.add_object(properties=property, vector=vec)

    def close(self):
        self.weaviate_client.close()
