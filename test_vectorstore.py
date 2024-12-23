from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import torch
from langchain_google_vertexai import VertexAIEmbeddings
import config_api_key

################################################################
# Test the working of the vectorstore
################################################################

# Verify if CUDA is available
device = 'cuda' if torch.cuda.is_available() else 'cpu'

embedding_model = VertexAIEmbeddings(model="textembedding-gecko@003")
# embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2',
#                                        model_kwargs={'device': device})

# Loading the vectorstore
vectorstore = Chroma(
    embedding_function=embedding_model,
    collection_name="vectorstore",
    persist_directory="./chroma"
)

query = 'Give me an example of a limit'
contexts = vectorstore.search(query=query, search_type='similarity', k=3)

print('Question:', query)
print('Answers:')
for context in contexts:
    print(context, '\n################################')