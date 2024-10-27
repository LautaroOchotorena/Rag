from langchain_community.document_loaders import PyPDFLoader
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
        # Agrega los documentos cargados a la lista general
        all_documents.extend(documents)

# Para que el metadato de page comience desde 1
for i, doc in enumerate(all_documents, start=1):
    doc.metadata["page"] = i

# Configura el divisor de texto para dividir los documentos en fragmentos 
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
splits = text_splitter.split_documents(all_documents)

# Función de preprocesamiento para separar referencias de ecuaciones
def preprocess_formula(text):
    # Patrón para detectar referencias de ecuaciones, como (3.8)
    equation_ref_pattern = r"\(\d+\.\d+\)$"
    # Reemplaza las referencias de ecuaciones con un marcador
    processed_text = re.sub(equation_ref_pattern, r" [REF: \g<0>]", text)
    return processed_text

# Aplica el preprocesamiento a cada fragmento
for fragment in splits:
    fragment.page_content = preprocess_formula(fragment.page_content)

# Inicializa el modelo de incrustación de HuggingFace
embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2',
                                        model_kwargs={'device': 'cpu'})
# dimension de 384

# Crea el almacén de vectores usando Chroma
vectorstore = Chroma.from_documents(documents=splits, embedding=embedding_model,
                                    collection_name='vectorstore',
                                    persist_directory="./")

if __name__ == '__main__':
    print('Primeros metadatos del documento:')
    for i in range(3):
        print(f'{all_documents[i]}')

    print('\nPrimeros chunks:')
    for i in range(3):
        text = splits[i].page_content.replace('\n', ' ')
        print(f'Chunk {i+1}:\n', text)
        
    print('\nRandom chunks:')
    i = random.randint(400, 500)
    for i in range(i, i+3):
        text = splits[i].page_content.replace('\n', ' ')
        print(f'Chunk {i+1}:\n', text)