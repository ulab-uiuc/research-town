import gradio as gr

def get_ideas():
    return ["idea 1", "idea 2", "idea 3"]

with gr.Blocks() as demo:
    input_text = gr.Textbox(label="input")
    mode = gr.Radio(["textbox", "button"], value="textbox")

    @gr.render(inputs=[input_text, mode], triggers=[input_text.submit])
    def show_ideas(text, mode):
        if len(text) == 0:
            gr.Markdown("## No arxiv link provided")
        else:
            ideas = get_ideas()
            for idea in ideas:
                if mode == "textbox":
                    gr.Textbox(idea)
                else:
                    gr.Button(idea)

demo.launch()