from itertools import islice
from typing import List

from langchain_core.embeddings import Embeddings
from pydantic import BaseModel
import httpx


def batched(iterable, n):
    if n < 1:
        raise ValueError("n must be at least one")
    iterator = iter(iterable)
    while batch := tuple(islice(iterator, n)):
        yield batch


class TextEmbeddingsInference(BaseModel, Embeddings):
    url: str
    """Url of text embeddings inference server"""
    normalize: bool = True

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Compute doc embeddings using a Text Embeddings Inference server.

        Args:
            texts: The list of texts to embed.

        Returns:
            List of embeddings, one for each text.
        """
        embeddings = []
        for batch in batched(texts, 8):
            payload = {
                "inputs": list(batch),
                "normalize": self.normalize,
                "truncate": True,
            }
            response = httpx.post(f"{self.url}/embed", json=payload).json()
            embeddings.extend(response)

        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Compute query embeddings using a Text Embeddings Inference server.

        Args:
            text: The text to embed.

        Returns:
            Embeddings for the text.
        """
        return self.embed_documents([text])[0]
