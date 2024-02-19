import gradio as gr

def slow_echo(message, history):
    return message

demo = gr.ChatInterface(slow_echo).queue().launch()
