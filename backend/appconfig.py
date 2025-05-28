import environ


@environ.config(prefix="")
class AppConfig:
    ollama_host: str = environ.var(default="localhost")
    ollama_port: str = environ.var()
    weaviate_port: int = environ.var(default="localhost", converter=int)
    weaviate_host: str = environ.var()
    tei_host: str = environ.var()
    tei_port: str = environ.var()
    langfuse_host: str = environ.var(default="localhost")
    langfuse_port: str = environ.var(default="3000")
    langfuse_project_public_key: str = environ.var(default="pk-lf")
    langfuse_project_secret_key: str = environ.var(default="sk-lf")
    redis_host: str = environ.var()
    redis_port: int = environ.var(converter=int)
    model: str = environ.var()
    llm: str = environ.var()
    telemetry_enabled = environ.var(
        converter=lambda x: x.casefold() == "True".casefold()
    )


config = environ.to_config(AppConfig)
