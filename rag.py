from langchain_google_genai import ChatGoogleGenerativeAI
import config_api_key
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
import warnings
import os
import torch
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.chains.conversation.base import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain

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

system_template = '''
Eres un asistente para tareas de respuestas a preguntas sobre estadística.
Utiliza las siguientes piezas de contexto recuperado para responder la pregunta.
Ten en cuenta que pueden haber tablas y fórmulas matemáticas en el contexto.
Si no sabes la respuesta simplemente menciona que no la sabes.

{context}
'''

prompt = ChatPromptTemplate([
    ('system', system_template),
    ('human', "{question}")
])

retriever = vectorstore.as_retriever(k=3)

memory = ConversationBufferMemory(memory_key="chat_history")

# rag chain
rag_chain = (
    {'context': retriever, 'question': RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)   

if __name__ == '__main__':
    # Consulta para buscar documentos relevantes
    query = "Explicame escalado multidimensional con fórmulas"

    result = rag_chain.invoke(query)

    print('Pregunta:', query)
    print('Respuesta:', result)