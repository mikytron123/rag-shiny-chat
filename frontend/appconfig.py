import environ

@environ.config(prefix="")
class AppConfig:
    server_host = environ.var()
    server_port = environ.var()

config = environ.to_config(AppConfig)