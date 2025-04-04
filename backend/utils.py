from ollama import Client

def get_num_tokens(client: Client, model: str, input: str) -> int:
    embed = client.embed(model=model, input=input)
    return embed["prompt_eval_count"]
