# RAG for mathematical documents
This project aims to create a chatbot based on mathematical documents where you can interact with and ask about exercises, information about a topic, examples, other authors that the documents cite, etc.

The documents Vhave to be in english otherwise it will be needed to change the embedding model to a multilingual one.

# Flow of the RAG

<div style="text-align: center;">
  <img src="flow_chart.png" alt="Flow Chart" />
</div>

# Results obtained

# How to run it

Keep in mind the structure of the folders
- Rag folder/
  - docs/
    - divided_pdfs/
  - md/
    - merged_files/
      - images/
  - prueba/

and follow the instructions:

**1.** Clone the repository using git or download everything by yourself:
```bash
    git clone https://github.com/LautaroOchotorena/Rag
    cd Walking-around-the-city
```
**2.** Create a file called "config.json" and put
```
{
	"api_key": "Gemini API KEY",
	"PROJECT_ID": "Project ID Google AI Studio"
}
```
For this project I used Gemini for the LLM and VertexAIEmbeddings for the vectorstore.
To obtain the keys: Create a Google Cloud project, then generate the [Gemini API KEY](https://aistudio.google.com/app/apikey) and [enable the Vertex AI API](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com).

Don't forget to replace the values in the json file.

**3.** Using Conda or Miniconda:
```bash
    conda env create -f environment.yml python=3.11.10
```
This will install the environment and the dependencies needed.

   Activate it
```bash
    conda activate rag
```
and follow the [instructions](https://pytorch.org/get-started/locally/) to use **CUDA** if you have a GPU or **NO CUDA** if you want to run everything on CPU.

**4.** Put the pdf documents inside the docs folder and acces to [SimpleTex](https://simpletex.net/) and use the Online OCR where you need to pass all the documents (one by one) in order to convert them into a markdown file with latex notation. Export them with the images, this will download a folder with the md and a folder with the images.
It can't process more than 500 pages per documents so if you have more than that you can use the [dividir_pdf.py](https://github.com/LautaroOchotorena/Rag/blob/master/dividir_pdf.py) to divide each documents into pieces of at least 500 pages. The pdf outputs will be stored in the divided_pdfs folder.
**Note:** At the moment of writting this SimpleTex doesn't support an api where you can do this efficiently and easily.

**5.** Check your new files: vertical tables and rarely (but it happended to me) some pages are skipped in the convertion.
If this happens you can use [create_pdf.py](https://github.com/LautaroOchotorena/Rag/blob/master/crear_pdf.py) to select a range of pages of a pdf document to be download so it can be processed successfully with SimpleTex. The results should be pasted manually into the correspond md file.

**6.** Put the folders created by SimpleTex inside the md folder. After that, combine the divided documents into a single one and also put all the images of each doc into a single folder. To do that just run [archivos_md.py](https://github.com/LautaroOchotorena/Rag/blob/master/archivos_md.py). The outputs will be in the merged_files folder.

**7.** Optional but usefull: use [formulas_into_text.py](https://github.com/LautaroOchotorena/Rag/blob/master/formulas_into_text.py) to replace the latex formulas into plain text (in a compacted way). This will helps a lot due to the reduction of characters using a compacted representation instead of the latex formula.

**8.** Create the vectorstore using [md_loader.py](https://github.com/LautaroOchotorena/Rag/blob/master/md_loader.py). It will be stored locally.

**9.** Ready to launch the app:
```bash
    python app.py
```
It will run locally.

## Reduction of characters
The usage of the **step 7** makes a lot of difference. <br>
For example:
<div align="center">

| <h4>Document</h4> | <h4>Number of tokens</h4>  | <h4>Number of characters</h4>
|-----------------------|--------------------|--------------------|
| <h4>**Original**</h4>   | <h4>358,374</h4>  | <h4>976,153</h4>
| <h4>**Compacted version**</h4>| <h4>227,832</h4> | <h4>658,651</h4>

</div>

That implies a reduction of **32.5%** for the number of characters.

This helps with the embedding model that has a limit of tokens per chunk.

Now you can store more data into a chunk.