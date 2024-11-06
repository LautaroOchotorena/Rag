import PyPDF2
from langchain_community.document_loaders import PyMuPDFLoader

# Rutas de los archivos PDF
pdf_path = './docs/Análisis de datos multivariantes - Daniel Peña.pdf'
new_pdf_path = './docs/prueba.pdf'

# Páginas de inicio y fin que deseas extraer (empiezan desde 0)
start_page = 375  # Primera página a extraer (ajústala según necesites)
end_page = 381   # Última página a extraer (inclusive)

# Abre el archivo PDF original
with open(pdf_path, 'rb') as pdf_file:
    reader = PyPDF2.PdfReader(pdf_file)
    writer = PyPDF2.PdfWriter()

    # Extrae cada página en el rango especificado
    for page_number in range(start_page, end_page + 1):
        writer.add_page(reader.pages[page_number])

    # Guarda las páginas en un nuevo archivo PDF
    with open(new_pdf_path, 'wb') as new_pdf_file:
        writer.write(new_pdf_file)

print(f'Las páginas desde {start_page + 1} hasta {end_page + 1} han sido extraídas y guardadas en {new_pdf_path}.')

# Cargar el PDF temporal con PyMuPDFLoader
loader = PyMuPDFLoader(new_pdf_path)
documents = loader.load()

# Imprimir el contenido del documento
for doc in documents:
    print(doc.page_content)