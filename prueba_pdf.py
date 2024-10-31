import PyPDF2
from langchain_community.document_loaders import PyMuPDFLoader
# Ruta del archivo PDF original
pdf_path = './docs/Applied Multivariate Statistical Analysis, 2nd edition - Härdle & Simar.pdf'
# Ruta del nuevo archivo PDF
new_pdf_path = './docs/prueba.pdf'
# Número de la página que deseas extraer (empezando desde 0)
page_number = 32  # Cambia este número según la página que necesites

# Abre el archivo PDF original
with open(pdf_path, 'rb') as pdf_file:
    reader = PyPDF2.PdfReader(pdf_file)
    writer = PyPDF2.PdfWriter()

    # Extrae la página deseada
    writer.add_page(reader.pages[page_number])

    # Guarda la nueva página en un nuevo archivo PDF
    with open(new_pdf_path, 'wb') as new_pdf_file:
        writer.write(new_pdf_file)

print(f'La página {page_number + 1} ha sido extraída y guardada en {new_pdf_path}.')

# Cargar el PDF temporal con PyMuPDFLoader
loader = PyMuPDFLoader(new_pdf_path)
documents = loader.load()

# Imprimir el contenido del documento
for doc in documents:
    print(doc.page_content)