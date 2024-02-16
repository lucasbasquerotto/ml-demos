import gradio as gr

def greet(history, input):
    return history + [(input, "Hello, " + input)]

def vote(data: gr.LikeData):
    if data.liked:
        print("You upvoted this response: " + data.value)
    else:
        print("You downvoted this response: " + data.value)
    

with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    textbox = gr.Textbox()
    textbox.submit(greet, [chatbot, textbox], [chatbot])
    chatbot.like(vote, None, None)  # Adding this line causes the like/dislike icons to appear in your chatbot
    
demo.launch()