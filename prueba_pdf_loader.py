from langchain_community.document_loaders import PyMuPDFLoader
from fpdf import FPDF
import tempfile

# Crear PDF temporal con el texto "prueba acá"
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="prueba acá perforación, gráficas", ln=True, align="C")

# Guardar el PDF temporalmente
with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
    pdf.output(temp_pdf.name)
    temp_pdf_path = temp_pdf.name

# Cargar el PDF temporal con PyMuPDFLoader
loader = PyMuPDFLoader(temp_pdf_path)
documents = loader.load()

# Imprimir el contenido del documento
for doc in documents:
    print(doc.page_content)