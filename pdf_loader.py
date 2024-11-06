from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyMuPDFLoader
import os
import warnings
import random
import re

warnings.filterwarnings("ignore")

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Define el directorio donde están tus archivos PDF
pdf_directory = "./docs"

# Crea una lista para almacenar todos los documentos cargados
all_documents = []

# Itera sobre cada archivo PDF en el directorio
for filename in os.listdir(pdf_directory):
    if filename.endswith(".pdf"):  # Solo procesa archivos PDF
        filepath = os.path.join(pdf_directory, filename)
        # Carga el PDF utilizando PyMuPDFLoader
        loader = PyMuPDFLoader(filepath)
        documents = loader.load()
        
        # Para que el metadato de page comience desde 1
        for i, doc in enumerate(documents, start=1):
            doc.metadata["page"] = i

        # Agrega los documentos cargados a la lista general
        all_documents.extend(documents)

# Configura el divisor de texto para dividir los documentos en fragmentos 
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
splits = text_splitter.split_documents(all_documents)

# Función de preprocesamiento para separar referencias de ecuaciones
def preprocess_formula(text):
    # Patrón para detectar referencias de ecuaciones, como (3.8)
    equation_ref_pattern = r"\(\d+\.\d+\)$"
    # Reemplaza las referencias de ecuaciones con un marcador
    processed_text = re.sub(equation_ref_pattern, r" [REF: \g<0>]", text)

    # Cambia los caracteres "Þ" por el caracter correspondiente "fi"
    processed_text = processed_text.replace("Þ", "fi")
    return processed_text

# Aplica el preprocesamiento a cada fragmento
for fragment in splits:
    fragment.page_content = preprocess_formula(fragment.page_content)

# Inicializa el modelo de incrustación de HuggingFace
embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/paraphrase-mpnet-base-v2',
                                        model_kwargs={'device': 'cpu'})
# dimension de 384

target_batch_size = 5461  # max batch size para ChromaDB

# Crea la colección inicialmente con una primera carga de documentos
vectorstore = Chroma.from_documents(
    documents=splits[:target_batch_size],  # Procesa un batch inicial dentro del límite
    embedding=embedding_model,
    collection_name='vectorstore',
    persist_directory="./chroma/",
    # Sin collection_metadata dará los similarity_score_threshold negativos 
    collection_metadata={"hnsw:space": "cosine"}
)

# añade los documentos restantes
for i in range(target_batch_size, len(splits), target_batch_size):
    batch = splits[i:i + target_batch_size]
    vectorstore.add_documents(documents=batch)

if __name__ == '__main__':
    print('Primeros metadatos del documento:')
    for i in range(3):
        print(f'{all_documents[i]}')

    print('\nPrimeros chunks:')
    for i in range(3):
        text = splits[i].page_content.replace('\n', ' ')
        print(f'Chunk {i+1}:\n', text)
        
    print('\nRandom chunks:')
    i = random.randint(400, 800)
    for i in range(i, i+7):
        text = splits[i].page_content.replace('\n', ' ')
        print(f'Chunk {i+1}:\n', text)