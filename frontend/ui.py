from shiny import App, ui, Inputs, Outputs, Session
import httpx
import os
import json
from shared.api_models import ModelSchema
import msgspec
from appconfig import config

SERVER_HOST = config.server_host
SERVER_PORT = config.server_port
client = httpx.AsyncClient(timeout=120)

decoder = msgspec.json.Decoder(type=ModelSchema)

r = httpx.get(f"http://{SERVER_HOST}:{SERVER_PORT}/models")
choices = decoder.decode(r.content).models

app_ui = ui.page_fluid(
    ui.panel_title("LLM RAG chat bot"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_select(id="model", label="Ollama models", choices=choices),
            ui.input_slider(
                id="input_temp",
                label="Temperature",
                min=0.0,
                max=2.0,
                value=0.0,
                step=0.1,
            ),
            open="closed",
            width=400,
        ),
        ui.chat_ui("chat"),
    ),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    chat = ui.Chat(id="chat", tokenizer=None)
    chat.ui()

    async def respone_to_iterator(r: httpx.Response):
        links_list: list[str] = []
        async for message in r.aiter_bytes():
            data_dict = json.loads(message.decode())
            if "completion" in data_dict:
                yield data_dict["completion"]
            elif "links" in data_dict:
                links_list = data_dict["links"]
        yield "\n\nCitations\n"
        for link in links_list:
            yield f"- {link}\n"

    @chat.on_user_submit
    async def _():
        query = chat.user_input()
        payload = {
            "model": input.model(),
            "temperature": input.input_temp(),
            "prompt": query,
        }

        req = client.build_request(
            "POST", f"http://{SERVER_HOST}:{SERVER_PORT}/llm/stream", json=payload
        )
        r = await client.send(req, stream=True)
        response_iter = respone_to_iterator(r)
        await chat.append_message_stream(response_iter)


app = App(app_ui, server)
