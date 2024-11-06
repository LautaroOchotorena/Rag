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

gr.ChatInterface(chat, title='Chat con RAG').launch()