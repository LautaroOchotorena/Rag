from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import torch

# Verifica si CUDA está disponible
device = 'cuda' if torch.cuda.is_available() else 'cpu'

embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2',
                                        model_kwargs={'device': device})

# Carga del vectorstore
vectorstore = Chroma(
    embedding_function=embedding_model,
    collection_name="vectorstore",
    persist_directory="."
)

query = '¿En qué página se encuentra componentes principales?'
respuesta = vectorstore.search(query=query, search_type='similarity', k=3)

print('Pregunta:', query)
print('Respuesta:', respuesta)