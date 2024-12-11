# RAG for mathematical documents
This project aims to create a chatbot based on mathematical documents where you can interact with and ask about exercises, more information about a topic, other authors that the documents cite, etc.

# Results obtained

# How to run it

1. Clone the repository using git or download everything by yourself:
```bash
    git clone https://github.com/LautaroOchotorena/Rag
    cd Walking-around-the-city
```

2. Using Conda or Miniconda:
```bash
    conda env create -f environment.yml python=3.11.10
```
This will install the environment and the dependencies needed.

3. Acces to (SimpleTex)[https://simpletex.net/] and use the Online OCR where you need to pass all the documents (one by one) in order to convert them into a markdown file with latex notation. Export them with the images, this will download a folder with the md and a folder with the images.
It can't process more than 500 pages per documents so if you have more than that you can use the (dividir_pdf.py)[https://github.com/LautaroOchotorena/Rag/blob/master/dividir_pdf.py] to divide each documents into pieces of at least 500 pages.
**Note:** At the moment of writting this SimpleTex doesn't support an api where you can do this efficiently and easily.

4. Check your new files: vertical tables and rarely (but it happended to me) some pages are skipped in the convertion.
If this happens you can use (create_pdf.py)[https://github.com/LautaroOchotorena/Rag/blob/master/crear_pdf.py] to select a range of pages of a pdf document so it can be processed successfully with SimpleTex. The results should be pasted manually into the correspond md file.

5. If you has had to divide documents into pieces then you can combine them again into a single markdown file with the usage of (archivos_md.py)[https://github.com/LautaroOchotorena/Rag/blob/master/archivos_md.py]

6. Optional but usefull: use (formulas_into_text.py)[https://github.com/LautaroOchotorena/Rag/blob/master/formulas_into_text.py] to convert the latex formulas into plain text (in a compacted way). This will helps a lot due to the reduction of characters using a compacted representation instead of the latex formula.

7. Create the vectorstore using (md_loader.py)[https://github.com/LautaroOchotorena/Rag/blob/master/md_loader.py]. It will be stored locally.

8. Ready to launch the app:
```bash
    python app.py
```
It will run locally.