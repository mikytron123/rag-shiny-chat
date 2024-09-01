from ollama import Client
import os

OLLAMA_HOST = os.getenv("OLLAMA_HOST", default="localhost")


def get_num_tokens(client:Client,model: str, input: str) -> int:
    embed = client.embed(model=model, input=input)
    return embed["prompt_eval_count"]
