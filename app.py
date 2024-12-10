import gradio as gr
from langchain_core.messages import (AIMessage, HumanMessage)
from rag import *

# Gestión de chats
chats = {'Chat 1':[]}
current_chat_id = ['Chat 1']
rag_estadistica = rag(describir_imagenes=False)

# Función para convertir historial al formato esperado
def format_chat_history(chat_history):
    formatted_history = []
    for user_message, bot_message in chat_history:
        if user_message:  # Mensaje del usuario
            formatted_history.append(HumanMessage(content=user_message))
        if bot_message:  # Respuesta del bot
            formatted_history.append(AIMessage(content=bot_message))
    return formatted_history

# Función principal de chat
def chat(question):
    global rag_estadistica
    # Formatea el historial antes de pasarlo a LangChain
    formatted_history = format_chat_history(chats[current_chat_id[0]])
    response = rag_estadistica.rag_chain.invoke({
        "input": question,
        "chat_history": formatted_history
    })
    chats[current_chat_id[0]].append((question, response['answer']))
    return chats[current_chat_id[0]]

# Crear un nuevo chat
def start_new_chat():
    chat_id = f"Chat {len(chats) + 1}"
    chats[chat_id] = []  # Crear un nuevo historial vacío
    current_chat_id[0] = chat_id
    return gr.update(choices=list(chats.keys()), value=chat_id), chats[chat_id]

# Seleccionar un chat existente y mostrar su historial
def select_chat(chat_id):
    current_chat_id[0] = chat_id
    return chats[chat_id]

# Función para guardar todos los chats en un archivo de texto
def save_chat_to_file():
    with open("chat_history.txt", "w", encoding="utf-8") as f:
        for chat_id, history in chats.items():
            f.write(f"Chat ID: {chat_id}\n")
            for user_message, bot_message in history:
                f.write(f"Usuario: {user_message}\n")
                f.write(f"Bot: {bot_message}\n")
            f.write("\n")  # Separar chats
    return "Chats guardados en 'chat_history.txt'"

# Función para cargar los chats desde un archivo de texto
def load_chat_history(file):
    global chats
    global chat_list
    # Leer el contenido del archivo cargado
    content = file.name
    with open(content, 'r', encoding='utf-8') as f:
        chat_id = None
        current_chat = []
         # Limpiar los chats anteriores
        chats = {}
        for line in f:
            line = line.strip()
            if line.startswith("Chat ID:"):
                # Nuevo chat, se añade el anterior
                if chat_id:
                    chats[chat_id] = current_chat
                chat_id = line.replace("Chat ID: ", "")
                current_chat = []
            elif line.startswith("Usuario:"):
                current_chat.append((line[9:], None))  # Guardamos el mensaje del usuario
            elif line.startswith("Bot:"):
                if current_chat and current_chat[-1][1] is None:  # Aseguramos que el mensaje del bot sea después del usuario
                    current_chat[-1] = (current_chat[-1][0], line[5:])  # Actualizamos con la respuesta del bot
        # Guardamos el último chat
        if chat_id:
            chats[chat_id] = current_chat
        
        # Actualizar la lista de chats en el Dropdown
        return gr.update(choices=list(chats.keys()), value=list(chats.keys())[0])

# Activar/desactivar descripción de imágenes
def checkbox_action(checked):
    global rag_estadistica
    if checked:
        rag_estadistica = rag(describir_imagenes=True)
    else:
        rag_estadistica = rag(describir_imagenes=False)
    return chats[current_chat_id[0]]

# Función para mostrar el chat seleccionado
def display_chat(chat_id):
    return chats.get(chat_id, [])

# Interfaz con Gradio
with gr.Blocks(fill_height=True) as demo:
    with gr.Row():
        with gr.Column(scale=1):  # Menú lateral para chats
            chat_list = gr.Dropdown(label="Historiales de Chat", choices=[], value=None)
            new_chat_button = gr.Button("Nuevo Chat")
            save_button = gr.Button("Guardar chats en local")
            # Componente para cargar el archivo de texto
            file_input = gr.File(file_count="single", file_types=[".txt"], label="Cargar historial de chat (txt)")
    
        with gr.Column(scale=9):  # Chat principal
            checkbox = gr.Checkbox(label="¿Describir imágenes del contexto? (respuesta más lenta)")
            chatbot = gr.Chatbot(label="Chat con RAG", height="70vh")
            input_box = gr.Textbox(label="Escribe tu mensaje:", interactive=True)

    # Funciones de interacción
    new_chat_button.click(start_new_chat, [], [chat_list, chatbot])
    chat_list.change(select_chat, [chat_list], chatbot)
    checkbox.change(checkbox_action, inputs=checkbox, outputs=chatbot)
    save_button.click(save_chat_to_file, outputs=save_button)
    input_box.submit(chat, inputs=input_box, outputs=chatbot)
    input_box.submit(lambda x: gr.update(value=''), [],[input_box])
    # Función de carga del archivo
    file_input.upload(load_chat_history, inputs=file_input, outputs=[chat_list])
    
    chat_list.change(display_chat, chat_list, chatbot)
demo.launch()