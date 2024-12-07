from langchain_google_genai import ChatGoogleGenerativeAI
import config_api_key
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import (ChatPromptTemplate, MessagesPlaceholder)
import warnings
import os
import torch
from langchain.retrievers import ContextualCompressionRetriever 
from ragatouille import RAGPretrainedModel
from langchain_core.runnables import RunnableLambda
from langchain.chains import (create_history_aware_retriever, create_retrieval_chain)
from langchain.chains.combine_documents import create_stuff_documents_chain
from describir_imagenes import process_context_with_images
from langchain_google_vertexai import VertexAIEmbeddings

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

embedding_model = VertexAIEmbeddings(model="textembedding-gecko@003")

# Carga del vectorstore
vectorstore = Chroma(
    embedding_function=embedding_model,
    collection_name="vectorstore",
    persist_directory="./chroma/"
)

retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"score_threshold": 0.3, "k": 10, "include_metadata": True})

# RAG = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
# # Crear el compresor utilizando RAG
# compresor = RAG.as_langchain_document_compressor()

# # Crear el retriever con compresión contextual
# compression_retriever = ContextualCompressionRetriever(
#     base_compressor=compresor,  # El compresor basado en RAG
#     base_retriever=retriever  # El retriever que hemos configurado
# )

comprobar = False
# Función para procesar las imagenes a texto descriptivo
def procesar_contexto(context):
    global comprobar
    if comprobar:
        print('Contexto:', context, '\n')

    context.page_content = process_context_with_images(context.page_content)

    if comprobar:
        print('Contexto procesado:', context.page_content, '\n')
    return context

def format_context_with_metadata(documents):
    """
    Formatea los documentos recuperados para incluir metadatos en el contexto.
    """
    for doc in documents:
        doc.page_content = f"{doc.page_content}\nmetadata={{'book': '{doc.metadata.get('book', 'desconocido')}', 'index':{doc.metadata.get('index', 'desconocido')}}}"
    return documents

class rag():
    def __init__(self, describir_imagenes):
        self.describir_imagenes = describir_imagenes
        self.retriever_procesado = RunnableLambda(
            lambda query: format_context_with_metadata([procesar_contexto(context) if
                                                        self.describir_imagenes else context
                                                        for context in retriever.invoke(query)])
                                                        )
        # top = 7
        # # Reranking
        # retriever_procesado = RunnableLambda(
        #     lambda query: sorted([procesar_contexto(context) for context in compression_retriever.invoke(query)],
        #                          key=lambda x: x.metadata['relevance_score'], reverse=True)[:top]
        # )

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
        # Guarda el contexto de forma simplificada como historial
        self.history_aware_retriever = create_history_aware_retriever(
            llm, self.retriever_procesado, contextualize_q_prompt
        )

        system_template = '''
        Eres un asistente para tareas de respuestas a preguntas sobre estadística.
        Utiliza las siguientes piezas de contexto recuperado para responder la pregunta.
        Ten en cuenta que pueden haber tablas y fórmulas matemáticas en el contexto.
        Cada pieza de contexto tiene un metadato asociado en el formato metadata={{"book": nombre_del_libro}}, donde "nombre_del_libro" indica el libro de dicha pieza de información.
        El metadato "index" ayuda a indicar la continuidad del contexto en un mismo libro.
        Al final de la respuesta incluye el nombre de el o los libros principales que se utilizaron para responder la pregunta.
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

        self.question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

        self.rag_chain = create_retrieval_chain(self.history_aware_retriever, self.question_answer_chain)

rag_estadistica = rag(describir_imagenes = True)
if __name__ == '__main__':
    chat_history = []

    # Figura 9.7: Mezcla al 50% de dos distribuciones normales con la misma media
    # y distinta varianza
    question = r"En qué libro y capítulo encuentro componentes principales?"

    print(rag_estadistica.history_aware_retriever.invoke({"input": question, "chat_history": chat_history}))

    print('Contextual retriever:')
    print(rag_estadistica.retriever_procesado.invoke(question)[0], '\n')

    # Para que se vea el cambio de contexto y contexto procesado
    comprobar = True

    respuesta = rag_estadistica.rag_chain.invoke({"input": question, "chat_history": chat_history})
    print('Pregunta:', question)
    print('Respuesta:', respuesta['answer'])