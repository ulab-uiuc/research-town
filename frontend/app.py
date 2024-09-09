import gradio as gr


def get_proposals():
    return ['idea 1', 'idea 2', 'idea 3']


with gr.Blocks() as demo:
    input_text = gr.Textbox(label='input')
    mode = gr.Radio(['textbox', 'button'], value='textbox')

    @gr.render(inputs=[input_text, mode], triggers=[input_text.submit])
    def show_ideas(text, mode):
        if len(text) == 0:
            gr.Markdown('## No arxiv link provided')
        else:
            proposals = get_proposals()
            for proposal in proposals:
                if mode == 'textbox':
                    gr.Textbox(proposal)
                else:
                    gr.Button(proposal)


demo.launch()
