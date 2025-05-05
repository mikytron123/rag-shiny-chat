from ollama import Client

def get_num_tokens(client: Client, model: str, input: str) -> int:
    """ Returns the total number of tokens in input string

    Args:
        client: ollama client
        model: ollama model
        input: input string to tokenize
    
    Returns:
        Integer count of the number of tokens
    """
    embed = client.embed(model=model, input=input)
    num_tokens = embed.prompt_eval_count
    assert num_tokens is not None 
    return num_tokens
