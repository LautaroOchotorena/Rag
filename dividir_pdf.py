import os
from PyPDF2 import PdfReader, PdfWriter

def split_pdf(input_pdf_path, output_dir, max_pages=500):
    # Leer el archivo PDF
    reader = PdfReader(input_pdf_path)
    total_pages = len(reader.pages)

    # Crear los PDFs necesarios con un máximo de max_pages cada uno
    for start_page in range(0, total_pages, max_pages):
        writer = PdfWriter()
        
        # Añadir páginas al nuevo PDF hasta llegar a max_pages o al final del PDF
        for page_num in range(start_page, min(start_page + max_pages, total_pages)):
            writer.add_page(reader.pages[page_num])
        
        # Guardar el archivo dividido
        if total_pages > max_pages:
            output_pdf_path = os.path.join(
                output_dir,
                f"{os.path.splitext(os.path.basename(input_pdf_path))[0]}_part{start_page // max_pages + 1}.pdf"
            )
        else:
            output_pdf_path = os.path.join(
                output_dir,
                f"{os.path.splitext(os.path.basename(input_pdf_path))[0]}.pdf"
            )
        with open(output_pdf_path, "wb") as output_pdf:
            writer.write(output_pdf)
        print(f"Guardado: {output_pdf_path}")

def process_pdfs_in_folder(folder_path, max_pages=500):
    # Crear una carpeta de salida para los archivos divididos
    output_dir = os.path.join(folder_path, "divided_pdfs")
    os.makedirs(output_dir, exist_ok=True)

    # Procesar cada archivo PDF en la carpeta
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(".pdf"):
            input_pdf_path = os.path.join(folder_path, file_name)
            split_pdf(input_pdf_path, output_dir, max_pages)
            print(f"Procesado: {file_name}")

# Usar la función en la carpeta con los PDFs
carpeta_pdfs = "./docs/"  # Reemplaza esta ruta
process_pdfs_in_folder(carpeta_pdfs)