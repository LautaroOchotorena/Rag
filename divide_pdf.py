import os
from PyPDF2 import PdfReader, PdfWriter

def split_pdf(input_pdf_path, output_dir, max_pages=500):
    # Read the pdf
    reader = PdfReader(input_pdf_path)
    total_pages = len(reader.pages)

    # Create the necessary PDFs with a maximum of max_pages per file
    for start_page in range(0, total_pages, max_pages):
        writer = PdfWriter()
        
        # Add pages to the new PDF until reaching max_pages or the end of the PDF
        for page_num in range(start_page, min(start_page + max_pages, total_pages)):
            writer.add_page(reader.pages[page_num])
        
        # Give the proper name if it is a part of a document or the whole document
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
        # Save the file
        with open(output_pdf_path, "wb") as output_pdf:
            writer.write(output_pdf)
        print(f"Saved: {output_pdf_path}")

def process_pdfs_in_folder(folder_path, max_pages=500):
    # Create an output foleder for the new files
    output_dir = os.path.join(folder_path, "divided_pdfs")
    os.makedirs(output_dir, exist_ok=True)

    # Process each pdf file in the folder_path
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(".pdf"):
            input_pdf_path = os.path.join(folder_path, file_name)
            split_pdf(input_pdf_path, output_dir, max_pages)
            print(f"Process: {file_name}")

# Folder where the documents before splitting are stored
pdfs_folder = "./docs/"
process_pdfs_in_folder(pdfs_folder)