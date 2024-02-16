import gradio as gr
import numpy as np

def flip(im):
    """
    Flips the input image vertically.

    Parameters:
    im (numpy.ndarray): The input image to be flipped.

    Returns:
    numpy.ndarray: The flipped image.
    """
    return np.flipud(im)

demo = gr.Interface(
    flip, 
    gr.Image(sources=["webcam"], streaming=True), 
    "image",
    live=True
)
demo.launch()