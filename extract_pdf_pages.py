import PyPDF2
from langchain_community.document_loaders import PyMuPDFLoader

# Path of the document
pdf_path = './docs/Calculus Volume 1.pdf'

# Set the pages you need (it starts at 0)
start_page = 375
end_page = 381   # Last page inclusive

new_pdf_path = pdf_path.replace(".pdf", f" (page {start_page + 1} to {end_page + 1}).pdf")

# Open the original pdf file
with open(pdf_path, 'rb') as pdf_file:
    reader = PyPDF2.PdfReader(pdf_file)
    writer = PyPDF2.PdfWriter()

    # Extract the pages requested
    for page_number in range(start_page, end_page + 1):
        writer.add_page(reader.pages[page_number])

    # Save them in a new file
    with open(new_pdf_path, 'wb') as new_pdf_file:
        writer.write(new_pdf_file)

print(f'The pages from {start_page + 1} to {end_page + 1} have been extracted and saved in {new_pdf_path}.')

# Load the new pdf file
loader = PyMuPDFLoader(new_pdf_path)
documents = loader.load()

# Show how the loader recognizes each page
for doc in documents:
    print(doc.page_content)