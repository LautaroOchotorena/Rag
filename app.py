import gradio as gr
from rag import *

def chat(message, history):
    response = rag_chain.invoke(f'{message}')
    return response

gr.ChatInterface(chat, title='Chat con RAG').launch()