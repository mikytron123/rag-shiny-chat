from shiny import App, ui, reactive, render, Inputs, Outputs, Session
import httpx
import os
import json
from utils import stream_to_reactive

SERVER_HOST = os.getenv("SERVER_HOST", default="localhost")

choices_dict = httpx.get(f"http://{SERVER_HOST}:8000/models").json()

app_ui = ui.page_fluid(
    ui.panel_title("LLM RAG chat bot"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_text_area("input_prompt", "Prompt", "", resize="both"),
            ui.input_select(id="model", label="Ollama models", choices=choices_dict),
            ui.input_slider(
                id="input_temp",
                label="Temperature",
                min=0.0,
                max=2.0,
                value=0.0,
                step=0.1,
            ),
            ui.input_action_button("submit_button", "Submit"),
            open="always",
            width=400,
        ),
        ui.output_text_verbatim("llm_output", placeholder=True),
        ui.output_text_verbatim("citation", placeholder=True),
    ),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    chunks: reactive.Value[tuple[str, ...]] = reactive.value(tuple())
    links: reactive.Value[tuple[str, ...]] = reactive.value(tuple())
    streaming_chat_messages_batch: reactive.Value[tuple[str, ...]] = reactive.value(
        tuple()
    )

    @reactive.effect()
    @reactive.event(streaming_chat_messages_batch)
    async def finalize_streaming_result():
        current_batch = streaming_chat_messages_batch()
        for message in current_batch:
            data_dict = json.loads(message.decode())
            if data_dict:
                if "completion" in data_dict:
                    chunks.set(chunks() + (data_dict["completion"],))
                elif "links" in data_dict:
                    links.set(links() + tuple(data_dict["links"],))

        return

    @reactive.effect()
    @reactive.event(input.submit_button)
    async def api_call():
        chunks.set(("",))
        payload = {
            "model": input.model(),
            "temperature": input.input_temp(),
            "prompt": input.input_prompt(),
        }
        client = httpx.AsyncClient(timeout=120)
        req = client.build_request(
            "POST", f"http://{SERVER_HOST}:8000/llm/stream", json=payload
        )
        r = await client.send(req, stream=True)
        messages = stream_to_reactive(r)
        chunks.set(("",))

        @reactive.Effect
        def copy_messages_to_batch():
            streaming_chat_messages_batch.set(messages())

    @render.text
    def llm_output():
        return "".join(chunks())

    @render.text
    def citation():
        if len(links()) == 0:
            return ""
        reference = "Citations\n"
        for link in links():
            reference += f"- {link}\n"
        return reference

    # @render.text
    # @reactive.event(input.submit_button)
    # def llm_output():
    #     payload = {
    #         "model": input.model(),
    #         "temperature": input.input_temp(),
    #         "prompt": input.input_prompt(),
    #     }
    #     req = httpx.post(f"http://{SERVER_HOST}:8000/llm", json=payload).json()
    #     return req["completion"]


app = App(app_ui, server)
