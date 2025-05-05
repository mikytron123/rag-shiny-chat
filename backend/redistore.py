import hashlib
import redis
import msgspec
from shared.api_models import LlmCompletionSchema

class RedisStore:
    def __init__(self, host="localhost", port=6379, db=0, password=None):
        """
        Initialize Redis connection
        """
        self.redis = redis.Redis(host=host, port=port, db=db, password=password)

    def _get_key_hash(self, input_string: str) -> str:
        """
        Compute SHA-256 hash of the input string to use as key
        """
        return hashlib.sha256(input_string.encode("utf-8")).hexdigest()

    def store_data(
        self, input_string: str, value: dict, expiration_seconds: int = 3600
    ) -> str:
        """
        Store data in Redis with hashed key and expiration time

        Args:
            input_string: The string to hash for the key
            value: The value to store (will be converted to string)
            expiration_seconds: Time to live in seconds (default 1 hour)

        Returns:
            The hashed key used for storage
        """
        key = self._get_key_hash(input_string)
        encoder = msgspec.msgpack.Encoder()
        redis_value = encoder.encode(value)
        self.redis.setex(key, expiration_seconds, redis_value)
        return key

    def retrieve_data(self, input_string: str) -> LlmCompletionSchema:
        """
        Retrieve data from Redis using the hashed key

        Args:
            input_string: The original string used to generate the key

        Returns:
            The stored value or None if not found/expired
        """
        key = self._get_key_hash(input_string)
        value = self.redis.get(key)
        decoder = msgspec.msgpack.Decoder(type=LlmCompletionSchema)
        
        if value is None:
            raise ValueError(f"key is missing {input_string}")
        assert isinstance(value, bytes)

        llm_completion = decoder.decode(value)
        return llm_completion
