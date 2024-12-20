import gradio as gr
from langchain_core.messages import (AIMessage, HumanMessage)
from rag import *
import time 

chats = {'Chat 1':[]}
current_chat_id = 'Chat 1'

rag_maths = rag(describe_images_bool = False)

# Convert the chats into a history format
def format_chat_history(chat_history):
    formatted_history = []
    for user_message, bot_message in chat_history:
        # User message
        if user_message:
            formatted_history.append(HumanMessage(content=user_message))
        # Bot message
        if bot_message:
            formatted_history.append(AIMessage(content=bot_message))
    return formatted_history

# Main chat
def chat(question):
    global rag_maths
    # Format the history to pass it to the rag
    formatted_history = format_chat_history(chats[current_chat_id])
    response = rag_maths.rag_chain.invoke({
        "input": question,
        "chat_history": formatted_history
    })
    # Add the response and the question to the history
    chats[current_chat_id].append((question, response['answer']))
    return chats[current_chat_id]

# Create a new chat
def start_new_chat():
    global current_chat_id
    chat_id = f"Chat {len(chats) + 1}"
    chats[chat_id] = []  # Create new chat empty
    current_chat_id = chat_id
    return gr.update(choices=list(chats.keys()), value=chat_id), chats[chat_id]

# Select an existing chat and display its history
def select_chat(chat_id):
    global current_chat_id
    current_chat_id = chat_id
    return chats[chat_id]

# Save the chats in a text file
def save_chat_to_file():
    with open("chat_history.txt", "w", encoding="utf-8") as f:
        for chat_id, history in chats.items():
            f.write(f"Chat ID: {chat_id}\n")
            for user_message, bot_message in history:
                f.write(f"User: {user_message}\n")
                f.write(f"Bot: {bot_message}\n")
            f.write("\n")  # Separate chats

    return "Chats saved in 'chat_history.txt'"

# Return the original text of the save chat button
def return_original_message():
    time.sleep(3) # Wait 3 seconds to change the text
    return "Save chats locally"

# Load chat history from a file text
def load_chat_history(file):
    global chats
    global chat_list
    global current_chat_id
    # Read the file name
    content = file.name
    # Open the file content
    with open(content, 'r', encoding='utf-8') as f:
        chat_id = None
        # Empty the previous chats
        chats = {}
        # Read each line
        for line in f:
            if line.startswith("Chat ID:"):
                # When it finds a new chat ID it saves the previous chat ID conversation
                if chat_id is not None:
                    chats[chat_id] = current_chat
                chat_id = line.replace("Chat ID: ", "")
                # Current chat it will store tuples of (question, bot_answer)
                current_chat = []
            
            elif line.startswith("User:"):
                # Append the line to the current chat
                current_chat.append((line[6:], None))
            
            elif line.startswith("Bot:"):
                if current_chat and current_chat[-1][1] is None:
                    current_chat[-1] = (current_chat[-1][0], line[5:])
                else:
                    # If there is no previous user, ignore it
                    pass

            else:
                # Additional text for the bot answer
                if current_chat and current_chat[-1][1] is not None:
                    # Concatenate additional lines to the bot's last response
                    current_chat[-1] = (current_chat[-1][0], current_chat[-1][1] + "\n" + line)
        
        # Save the last Chat ID conversation
        if chat_id:
            chats[chat_id] = current_chat
        
        current_chat_id = chat_id
        # Refresh the dropdown list of chats and show the last chat
        return gr.update(choices=list(chats.keys()), value=current_chat_id), chats[current_chat_id]

# Enable/Disable image drescriptions
def checkbox_action(checked):
    global rag_maths
    if checked:
        rag_maths = rag(describe_images_bool = True)
    else:
        rag_maths = rag(describe_images_bool = False)
    return chats[current_chat_id]

# Empty the history of chats
def delete_history_chats():
    global chats
    global current_chat_id
    chats = {'Chat 1':[]}
    current_chat_id = 'Chat 1'
    # Refresh the dropdown list of chats and show the first chat empty
    return gr.update(choices=list(chats.keys()), value=list(chats.keys())[0]), chats['Chat 1']

# Gradio interface
with gr.Blocks(fill_height=True) as demo:
    with gr.Row():
        # First column
        with gr.Column(scale=1):
            chat_list = gr.Dropdown(label="Chat Histories", choices=['Chat 1'], value='Chat 1')
            delete_button = gr.Button("Delete chat history")
            new_chat_button = gr.Button("New Chat")
            save_button = gr.Button("Save chats locally")

            # To upload a chat history
            file_input = gr.File(file_count="single", file_types=[".txt"], label="Upload a chat history (txt)")

        # Second column
        with gr.Column(scale=9):
            checkbox = gr.Checkbox(label="Describe images from the context? (slower answer)")
            chatbot = gr.Chatbot(label="Chat", height="70vh")
            input_box = gr.Textbox(label="Write your message:", interactive=True)

    # Interaction functions
    # Create new chat
    new_chat_button.click(start_new_chat, [], [chat_list, chatbot])

    # Delete the chat history and clear the interface
    delete_button.click(delete_history_chats, [], [chat_list, chatbot])

    # Change the interface when switching between chats
    chat_list.change(select_chat, [chat_list], chatbot)

    # Enable/Disable image descriptions
    checkbox.change(checkbox_action, inputs=checkbox, outputs=chatbot)

    # Save the chats in a text file
    save_button.click(save_chat_to_file, outputs=save_button)
    save_button.click(return_original_message, outputs=save_button)

    # Allow sending the input to the LLM and clear the value once sent
    input_box.submit(chat, inputs=input_box, outputs=chatbot)
    input_box.submit(lambda x: gr.update(value=''), [],[input_box])

    # Load chat history from a file text and redirect to the last chat
    file_input.upload(load_chat_history, inputs=file_input, outputs=[chat_list, chatbot])

demo.launch()