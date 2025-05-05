import msgspec

class ModelSchema(msgspec.Struct):
    models: list[str]

class LlmCompletionSchema(msgspec.Struct):
    completion: str
    links: list[str]
