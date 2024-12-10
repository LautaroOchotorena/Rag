from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from transformers import AutoTokenizer
import matplotlib.pyplot as plt
import os
import warnings
import random
import re
import torch
import heapq
from langchain_google_vertexai import VertexAIEmbeddings
import config_api_key

warnings.filterwarnings("ignore")

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print('Device utilizado:', device)

# Define el directorio donde están tus archivos PDF
md_directory = "./prueba"

# Crea una lista para almacenar todos los documentos cargados
splits_all_documents = []
separators = ["."]
# Itera sobre cada archivo md en el directorio
for filename in os.listdir(md_directory):
    if filename.endswith(".md"):  # Solo procesa archivos PDF
        filepath = os.path.join(md_directory, filename)
        loader = TextLoader(filepath, encoding="utf-8")
        documents = loader.load()

        # Configura el divisor de texto para dividir los documentos en fragmentos
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                                                            model_name="gpt-4",
                                                            chunk_size=2500,
                                                            chunk_overlap=300,
                                                        )
        splits = text_splitter.split_documents(documents) 

        # Pongo un index para que se interprete mejor qué texto va después
        for i, doc in enumerate(splits, start=1):
            doc.metadata["index"] = i
            doc.metadata['book'] = filename.replace(".md","")
            # Elimino el metadato "source" ya que es redundante con "book"
            del doc.metadata['source']

        # Agrega los documentos cargados a la lista general
        splits_all_documents.extend(splits)

# Función de preprocesamiento para separar referencias de ecuaciones
def preprocess_formula(text):
    # Patrón para detectar referencias de ecuaciones, como (3.8) o (3-8)
    equation_ref_pattern = r"\((\d+\.\d+|\d+-\d+)\)$"
    # Reemplaza las referencias de ecuaciones con un marcador. Output: "[REF: 3.8]"
    processed_text = re.sub(equation_ref_pattern, r" [REF: \g<0>]", text)

    return processed_text

# Aplica el preprocesamiento a cada fragmento
for fragment in splits_all_documents:
    fragment.page_content = preprocess_formula(fragment.page_content)

# Inicializa el modelo de incrustación de HuggingFace
embedding_model = VertexAIEmbeddings(model="textembedding-gecko@003")
# dimension de 768
tokenizer = AutoTokenizer.from_pretrained('dunzhang/stella_en_400M_v5', trust_remote_code=True)

max_tokens =  3072
#max_tokens = tokenizer.model_max_length
print('Máximo de tokens:', max_tokens)
tokens_counts = [tokenizer(sentence.page_content, padding=False, truncation=False, return_tensors='pt')['input_ids'].shape[1] for sentence in splits_all_documents]
print('Cantidad total de tokens de los documentos:', sum(tokens_counts))

max_3 = heapq.nlargest(3, set(tokens_counts))
print('Top 3 fragmentos con más tokens:')
for i, maximo in enumerate(max_3):
    print(f'Fragmento {i+1}:')
    print(splits_all_documents[tokens_counts.index(maximo)].page_content)

min_3 = heapq.nsmallest(3, set(tokens_counts))
print("\nLos 3 fragmentos con menos tokens:")
for i, min in enumerate(min_3):
    print(f'Fragmento {i+1}:')
    print(splits_all_documents[tokens_counts.index(min)].page_content)

plt.plot(tokens_counts, marker='o', color='blue', linestyle='', alpha=0.3)
# textos truncados a partir de 512 tokens
plt.axhline(y=max_tokens, color='r', linestyle='--', label='Max')
plt.xlabel('Index')
plt.ylabel('Número de tokens')
plt.title('Tokens de cada fragmento de texto')
plt.grid(True)
plt.legend()
plt.show()

target_batch_size = 5461  # max batch size para ChromaDB

# Crea la colección inicialmente con una primera carga de documentos
vectorstore = Chroma.from_documents(
    documents=splits_all_documents[:target_batch_size],  # Procesa un batch inicial dentro del límite
    embedding=embedding_model,
    collection_name='vectorstore',
    persist_directory="./chroma/",
    # Sin collection_metadata dará los similarity_score_threshold negativos 
    collection_metadata={"hnsw:space": "cosine"}
)

# añade los documentos restantes
for i in range(target_batch_size, len(splits_all_documents), target_batch_size):
    batch = splits_all_documents[i:i + target_batch_size]
    vectorstore.add_documents(documents=batch)

if __name__ == '__main__':
    print('Primeros metadatos de los documentos:')
    for i in range(3):
        print(f'{splits_all_documents[i].metadata}')

    print('\nPrimeros chunks:')
    for i in range(3):
        text = splits_all_documents[i].page_content.replace('\n', ' ')
        print(f'Chunk {i+1}:\n', text)
    
    try:
        print('\nRandom chunks:')
        i = random.randint(400, 800)
        for i in range(i, i+3):
            text = splits_all_documents[i].page_content.replace('\n', ' ')
            print(f'Chunk {i+1}:\n', text)
    except IndexError:
        print('Error al seleccionar fragmentos aleatorios:', IndexError)