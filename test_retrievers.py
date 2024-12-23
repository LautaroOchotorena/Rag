from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import torch
from langchain_google_vertexai import VertexAIEmbeddings
import config_api_key

################################################################
# Test the working of a retriever with different search_types
################################################################

# Verify if CUDA is available
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/LaBSE',
#                                        model_kwargs={'device': device})

embedding_model = VertexAIEmbeddings(model="textembedding-gecko@003")

# Loading the vectorstore
vectorstore = Chroma(
    embedding_function=embedding_model,
    collection_name="vectorstore",
    persist_directory="./chroma/",
    # Without collection_metadata, it will give negative similarity_score_thresholds.
    collection_metadata={"hnsw:space": "cosine"}
)

query = 'Where can I find power series?'
k = 3
retriever = vectorstore.as_retriever(search_kwargs={"k": k})
contexts = retriever.invoke(query)

print('Question:', query)
for context in contexts:
    print(f'Using k={k} similarity:')
    print(context, '\n\n################################')

retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": k})
contexts = retriever.invoke(query)
for context in contexts:
    print('Using mmr:')
    print(context, '\n\n################################')

retriever = vectorstore.as_retriever(search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.2, "k": k})
contexts = retriever.invoke(query)
if contexts:
    for context in contexts:
        print('Using similarity scores:')
        print(context, '\n\n################################')
else:
    print('Nothing in the context')