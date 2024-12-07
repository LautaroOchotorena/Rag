import gradio as gr
from langchain_core.messages import (AIMessage, HumanMessage)
from rag import *

chat_history = []
rag_estadistica = rag(describir_imagenes = False)
def chat(question, history):
    response = rag_estadistica.rag_chain.invoke({"input": question, "chat_history": chat_history})
    chat_history.extend([
        HumanMessage(content=question),
        AIMessage(content=response['answer'])
    ])
    return response['answer']

def checkbox_action(checked):
    global rag_estadistica
    if checked:
        # Actualizo todo el rag
        rag_estadistica = rag(describir_imagenes = True)
        return "Modo activado."
    else:
        # Actualizo todo el rag
        rag_estadistica = rag(describir_imagenes = False)
        return "Modo desactivado."

with gr.Blocks(fill_height=True) as demo:
    with gr.Column():  # Escala más pequeña para el checkbox
        checkbox = gr.Checkbox(label="¿Describir imágenes del contexto? (respuesta más lenta)", elem_id="small-checkbox")
    with gr.Column(scale=9):
        # Espacio mayor para el chat
        chat_interface = gr.ChatInterface(chat, title="Chat con RAG")
    
    # Actualizar el estado del modo en función del checkbox
    checkbox.change(checkbox_action, inputs=checkbox)

demo.launch()