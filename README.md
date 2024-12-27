# RAG for mathematical documents
This project aims to create a chatbot based on mathematical documents, allowing users to interact with it and ask about exercises, information about a topic, examples, references to other authors cited in the documents, and more.

The documents must be in english; otherwise, it will be necessary to switch to a multilingual embedding model.

# Flow of the RAG

<div style="text-align: center;">
  <img src="flow_chart.png" alt="Flow Chart"/>
</div>

# Results
<video width="1280" height="720" controls>
  <source src="chat_examples/example_video.mp4" type="video/mp4">
  Your browser does not support the video element.
</video>

Some chat tests that I did are located in the *"chat_examples"* folder.

# How to run it

Keep in mind the structure of the folders:
```bash
├── Rag/
├── ├── chat_examples/
│   ├── docs/
│   │   └── divided_pdfs/
│   ├── md/
│   │   └── merged_files/
│   │       └── images/
│   └── final_md/
```
The files in these folders provide an example without requiring all the steps. Credits to [OpenStax](https://openstax.org/) that allows the usage of those books under a CC BY-NC-SA 4.0 license.

If you want to run this example, just follow steps 1 to 3 and then skip to the step 9.

Empty the folders and follow these steps to create your own chatbot based on your documents.

### Steps
**1.** If you want the examples to be included:

Clone the repository using git or download everything by yourself:
```bash
    git clone https://github.com/LautaroOchotorena/Rag
    cd Rag
```
If not:
```bash
    git clone --no-checkout https://github.com/LautaroOchotorena/Rag
    cd Rag
    git sparse-checkout init --cone
    git sparse-checkout set */
    git checkout master
    mkdir docs
    mkdir final_md
    mkdir md
```

**2.** Create a JSON file called "config.json":
```bash
echo '{"api_key": "Gemini API KEY", "PROJECT_ID": "Project ID Google AI Studio"}' > config.json
```
For this project I used Gemini for the LLM and VertexAIEmbeddings for the vectorstore.
To obtain the keys: Create a Google Cloud project, then generate the [Gemini API KEY](https://aistudio.google.com/app/apikey) and [enable the Vertex AI API](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com).

Don't forget to replace the values in the JSON file.

Also you need to [Install Google Cloud CLI](https://cloud.google.com/sdk/docs/install-sdk#windows) so follow the steps provided in the link, and then run on the terminal:

```bash
gcloud auth login
```

to authenticate with a Google account.

> [!NOTE]  
You can still visualize the chatbot (though you can't chat) even without following this step. This might help in reviewing the chats from the folder *"chat_examples"*.

**3.** Using Conda or Miniconda (on Windows):
```bash
    conda env create -f environment.yaml
```
This will install the environment and the dependencies needed.

An alternative on Linux or Windows after creating your own environment (with Python 3.11.9) is:
```bash
    pip install -r requirements.txt
```

Then activate your environment. In Conda:
```bash
    conda activate rag
```

In case you are using an embedding model from Hugging Face, I recommend following the [instructions to install PyTorch](https://pytorch.org/get-started/locally/) to set up **CUDA** if you have a GPU compatible with CUDA (remember to install the CUDA Toolkit compatible with your PyTorch version) or **NO CUDA** if you want to run everything on the CPU.

**4.** Put the pdf documents inside the *"docs"* folder, acces to [SimpleTex](https://simpletex.net/) (it may ask you to create an account) and use the Online OCR to process the documents (one by one) to convert them into a Markdown file with LaTeX notation. Export them with the images, and this will download a .zip containing a folder with the .md and a folder with the images.
It can't process more than 500 pages per document, so if you have more than that you can use the [divide_pdf.py](https://github.com/LautaroOchotorena/Rag/blob/master/divide_pdf.py) script to divide each document into pieces of up to 500 pages. The resulting PDF files will be stored in the *"divided_pdfs"* folder.<br>
> [!NOTE]  
At the time of writing this, SimpleTex doesn't support an API that allows you to do this efficiently and easily. You can use [Nougat](https://github.com/facebookresearch/nougat?tab=readme-ov-file) instead, but it won't process images, and you might need to makes changes in step 7.

**5.** Put the folders (which are inside the .zip file) created by SimpleTex into the *"md"* folder. After that, run the [combine_parts_and_images.py](https://github.com/LautaroOchotorena/Rag/blob/master/combine_parts_and_images.py) script to combine the divided documents into a single file, and it will also place all the images from each document into a single folder. The outputs will be saved in the *"merged_files"* folder.

**6.** Check the .md files for vertical tables, as they might not be recognized correctly during the conversion, and rarely (though it happended to me) some pages may be skipped. To redo some of the pages, use the [extract_pdf_pages.py](https://github.com/LautaroOchotorena/Rag/blob/master/extract_pdf_pages.py) script and select a range of pages to export so they can be processed successfully with SimpleTex. The results should be pasted manually into the correspond .md file.

**7.** Optional but usefull:

Use the [formulas_into_text.py](https://github.com/LautaroOchotorena/Rag/blob/master/formulas_into_text.py) script to replace the LaTeX formulas and tables with plain text (in a compact form). This will helps a lot due to the reduction of characters/tokens using a compact representation.

**8.** Create the vectorstore using the [md_loader.py](https://github.com/LautaroOchotorena/Rag/blob/master/md_loader.py) script. It will be stored locally in the *"chroma"* folder.

**9.** Ready to launch the app:
```bash
    python app.py
```
It will run locally.

## Reduction of characters
> [!TIP]
The use of **step 7** makes a big difference.

For example:
<div align="center">

| <h4>Document</h4> | <h4>Number of tokens</h4>  | <h4>Number of characters</h4>
|-----------------------|--------------------|--------------------|
| <h4>**Original**</h4>   | <h4>485,433</h4>  | <h4>1,374,860</h4>
| <h4>**Compacted version**</h4>| <h4>401,561</h4> | <h4>1,143,874</h4>

</div>

This implies a reduction of **17%** in the number of characters.

This helps with the embedding model, which has a token limit per chunk.

Now you can store more data in a chunk.

# Other implementations
It would be much easier to implement [MathPix](https://mathpix.com/) as a [MathPixPDFLoader](https://python.langchain.com/docs/integrations/document_loaders/mathpix/), but unfortunately, it is a paid service.