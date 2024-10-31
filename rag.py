from langchain_google_genai import ChatGoogleGenerativeAI
import config_api_key
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import (ChatPromptTemplate, MessagesPlaceholder)
import warnings
import os
import torch
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.chains.conversation.base import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.chains import (create_history_aware_retriever, create_retrieval_chain)
from langchain.chains.combine_documents import create_stuff_documents_chain

warnings.filterwarnings("ignore")

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Esto desactiva las advertencias de TensorFlow

# Verifica si CUDA está disponible
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Inicializa el modelo
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.1
)

embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2',
                                        model_kwargs={'device': device})

# Carga del vectorstore
vectorstore = Chroma(
    embedding_function=embedding_model,
    collection_name="vectorstore",
    persist_directory="."
)

retriever = vectorstore.as_retriever(k=3)

contextualize_q_system_prompt = """
Dado un historial de chat y la última pregunta del usuario formula una pregunta que pueda entenderse sin el historial del chat.
NO respondas la pregunta, simplemente reformúlala si es necesario y, en caso contrario, devuélvela tal como está.
"""

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
# Se le pasa    
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

system_template = '''
Eres un asistente para tareas de respuestas a preguntas sobre estadística.
Utiliza las siguientes piezas de contexto recuperado para responder la pregunta.
Ten en cuenta que pueden haber tablas y fórmulas matemáticas en el contexto.
En caso de dar ejemplos o indicar algún capítulo acompañarlo con el nombre del documento de donde se sacó la información.
Si no sabes la respuesta simplemente menciona que no la sabes.
Pregunta:
{input}

Contexto:
{context}
'''

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_template),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

if __name__ == '__main__':
    chat_history = []
    # Consulta para buscar documentos relevantes
    question = "Explicame escalado multidimensional con fórmulas"

    result = rag_chain.invoke({'input': question, "chat_history": chat_history})

    print('Pregunta:', question)
    print('Respuesta:', result['answer'])