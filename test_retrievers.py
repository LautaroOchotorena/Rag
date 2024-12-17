from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import torch

# Verify if CUDA is available
device = 'cuda' if torch.cuda.is_available() else 'cpu'

embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/LaBSE',
                                        model_kwargs={'device': device})

# Loading the vectorstore
vectorstore = Chroma(
    embedding_function=embedding_model,
    collection_name="vectorstore",
    persist_directory="./chroma/",
    # Without collection_metadata, it will give negative similarity_score_thresholds.
    collection_metadata={"hnsw:space": "cosine"}
)

query = 'Describe la figura 12.1'
k = 15
retriever = vectorstore.as_retriever(search_kwargs={"k": k})
answer = retriever.invoke(query)

print('Question:', query)
print(f'Using k={k} similarity:')
print('Answer:', answer, '\n')

retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": k})
answer = retriever.invoke(query)
print('Using mmr:')
print('Answer:', answer, '\n')

retriever = vectorstore.as_retriever(search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.5, "k": k})
answer = retriever.invoke(query)
print('Using similarity scores:')
print('Answer:', answer)