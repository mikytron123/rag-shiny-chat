from shiny import App, ui, reactive, render, Inputs, Outputs, Session
import requests
import os

SERVER_HOST = os.getenv("SERVER_HOST")

choices_dict = requests.get(f"http://{SERVER_HOST}:8000/models").json()

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
                value=0.8,
                step=0.1,
            ),
            ui.input_action_button("submit_button", "Submit"),
            open="always",
            width=400,
        ),
        ui.output_text_verbatim("llm_output", placeholder=True),
    ),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:

    @render.text
    @reactive.event(input.submit_button)
    def llm_output():
        payload = {
            "model": input.model(),
            "temperature": input.input_temp(),
            "prompt": input.input_prompt(),
        }
        req = requests.post(f"http://{SERVER_HOST}:8000/llm", json=payload).json()
        return req["completion"]


if __name__ == "__main__":
    app = App(app_ui, server)
