import gradio as gr
from langchain_core.messages import (AIMessage, HumanMessage)
from rag import *

chat_history = []
def chat(question, history):
    response = rag_chain.invoke({"input": question, "chat_history": chat_history})
    chat_history.extend([
        HumanMessage(content=question),
        AIMessage(content=response['answer'])
    ])
    return response['answer']

def checkbox_action(checked):
    global describir_imagenes
    if checked:
        describir_imagenes = True
        return "Modo activado."
    else:
        describir_imagenes = False
        return "Modo desactivado."

css = """
#chat-container .gr-chat-container {
    height: 1800px !important;  /* Ajusta la altura */
    max-height: 1800px !important;
}
#chat-container .gr-chat-message {
    font-size: 18px !important;  /* Aumenta el tamaño del texto */
}
"""

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():  # Escala más pequeña para el checkbox
            checkbox = gr.Checkbox(label="¿Describir imagenes del contexto?", elem_id="small-checkbox")
         # Espacio mayor para el chat
        chat_interface = gr.ChatInterface(chat, title="Chat con RAG", css=css)
    
    # Actualizar el estado del modo en función del checkbox
    checkbox.change(checkbox_action, inputs=checkbox)

demo.launch()