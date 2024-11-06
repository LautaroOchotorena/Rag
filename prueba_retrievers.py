from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import torch

# Verifica si CUDA está disponible
device = 'cuda' if torch.cuda.is_available() else 'cpu'

embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/paraphrase-mpnet-base-v2',
                                        model_kwargs={'device': device})

# Carga del vectorstore
vectorstore = Chroma(
    embedding_function=embedding_model,
    collection_name="vectorstore",
    persist_directory="./chroma/",
    # Sin collection_metadata dará los similarity_score_threshold negativos 
    collection_metadata={"hnsw:space": "cosine"}
)

query = 'Describe la figura 12.1'
k = 15
retriever = vectorstore.as_retriever(search_kwargs={"k": k})
respuesta = retriever.invoke(query)

print('Pregunta:', query)
print(f'Usando similiraty k={k}:')
print('Respuesta:', respuesta, '\n')

retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": k})
respuesta = retriever.invoke(query)
print('Usando mmr:')
print('Respuesta:', respuesta, '\n')

retriever = vectorstore.as_retriever(search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.5, "k": k})
respuesta = retriever.invoke(query)
print('Usando similarity score:')
print('Respuesta:', respuesta)