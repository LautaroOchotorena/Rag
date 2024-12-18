from langchain_google_genai import ChatGoogleGenerativeAI
import config_api_key
from langchain_chroma import Chroma
from langchain_core.prompts import (ChatPromptTemplate, MessagesPlaceholder)
import warnings
import os
import torch
from langchain_core.runnables import RunnableLambda
from langchain.chains import (create_history_aware_retriever, create_retrieval_chain)
from langchain.chains.combine_documents import create_stuff_documents_chain
from describe_images import process_context_with_images
from langchain_google_vertexai import VertexAIEmbeddings

warnings.filterwarnings("ignore")

# Disable the warning of TensorFlow
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Verify if CUDA is available
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print('Device used:', device)

# LLM model 
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.1
)

embedding_model = VertexAIEmbeddings(model="textembedding-gecko@003")

# Loading the vectorstore
vectorstore = Chroma(
    embedding_function=embedding_model,
    collection_name="vectorstore",
    persist_directory="./chroma/"
)

retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"score_threshold": 0.2, "k": 10})

check_context = False
i = 1
# Function to describe images
def describe_images_func(context):
    global check_context
    if check_context:
        print('Context:', context, '\n')

    context.page_content = process_context_with_images(context.page_content)

    if check_context:
        print('Process context:', context.page_content, '\n')
    return context

def format_context_with_metadata(documents):
    """
    Format the retrieved documents to include metadata in the context.
    """
    for doc in documents:
        doc.page_content = f"{doc.page_content}\nmetadata={{'book': '{doc.metadata.get('book', 'desconocido')}', 'index':{doc.metadata.get('index', 'desconocido')}}}"
    return documents

class rag():
    def __init__(self, describe_images_bool):
        self.describe_images_bool = describe_images_bool
        self.processed_retriever = RunnableLambda(
            lambda query: format_context_with_metadata([describe_images_func(context) if
                                                        self.describe_images_bool else context
                                                        for context in retriever.invoke(query)])
                                                        )
        # top = 7
        # # Reranking
        # self.processed_retriever = RunnableLambda(
        #     lambda query: sorted([describe_images_func(context) if
        #                           self.describe_images_bool else context
        #                           for context in retriever.invoke(query)],
        #                          key=lambda x: x.metadata['relevance_score'], reverse=True)[:top]
        # )

        contextualize_q_system_prompt = """
        Given a chat history and the user's latest question, formulate a question that can be understood without the chat history.
        DO NOT answer the question; simply rephrase it if necessary, and if not, return it as it is.
        """

        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        # Simplify the context and save it as history
        self.history_aware_retriever = create_history_aware_retriever(
            llm, self.processed_retriever, contextualize_q_prompt
        )

        system_template = '''
        You are an assistant for answering mathematics-related questions.
        Use the following pieces of retrieved context to respond to the question.
        Keep in mind that the context may contain tables and mathematical formulas.

        Each piece of context has associated metadata in the format metadata={{"book": book_name}}, where "book_name" indicates the book that the information comes from.
        The "index" metadata helps indicate the continuity of context within the same book.

        At the end of the response, include the name(s) of the primary book(s) used to answer the question.
        If you do not know the answer, simply state that you do not know.
        Question:
        {input}

        Context:
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

rag_maths = rag(describe_images_bool = True)
if __name__ == '__main__':
    chat_history = []

    question = r"In which chapters can I find power series?"

    print(rag_maths.history_aware_retriever.invoke({"input": question, "chat_history": chat_history})[0], '\n')

    print('Contextual retriever:')
    print(rag_maths.processed_retriever.invoke(question)[0], '\n')

    # So that the change in context and processed context can be seen
    check_context = False

    respuesta = rag_maths.rag_chain.invoke({"input": question, "chat_history": chat_history})
    print('Question:', question)
    print('Answer:', respuesta['answer'])