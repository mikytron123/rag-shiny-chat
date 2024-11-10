import environ

@environ.config(prefix="")
class AppConfig:
    ollama_host = environ.var()
    ollama_port = environ.var()
    weaviate_port = environ.var(converter=int)
    weaviate_host = environ.var()
    tei_host = environ.var()
    tei_port = environ.var()
    langfuse_host = environ.var()
    langfuse_port = environ.var()
    langfuse_project_public_key = environ.var()
    langfuse_project_secret_key = environ.var()

config = environ.to_config(AppConfig)    
