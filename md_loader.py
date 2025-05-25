from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from transformers import AutoTokenizer
import matplotlib.pyplot as plt
import os
import warnings
import random
import re
import torch
import heapq
from langchain_google_vertexai import VertexAIEmbeddings
import config_api_key

warnings.filterwarnings("ignore")

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# In case you use an embedding model locally, such as those from Hugging Face
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print('Device used:', device)

# Directory of the Markdown files
md_directory = "./final_md"

# List to store all the documents
splits_all_documents = []

# Iterate over each .md file in the directory
for filename in os.listdir(md_directory):
    if filename.endswith(".md"):
        filepath = os.path.join(md_directory, filename)
        loader = TextLoader(filepath, encoding="utf-8")
        documents = loader.load()

        # The splitter of the documents
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                                                            model_name="gpt-4",
                                                            chunk_size=2500,
                                                            chunk_overlap=300,
                                                        )
        splits = text_splitter.split_documents(documents) 

        # Add metadata such as an index to show the continuity of the documents and the book name
        for i, doc in enumerate(splits, start=1):
            doc.metadata["index"] = i
            doc.metadata['book'] = filename.replace(".md","")
            # Delete the medata "source" because it is redundant
            del doc.metadata['source']

        # Add the documents to the list
        splits_all_documents.extend(splits)

# Preprocessing function to separate equation references
def preprocess_formula(text):
    # Pattern to detect equation references, such as (3.8) or (3-8)
    equation_ref_pattern = r"\((\d+\.\d+|\d+-\d+)\)$"
    # Replace equation references with a much clear type of refeerence. 
    # Output: "[REF: 3.8]"
    processed_text = re.sub(equation_ref_pattern, r" [REF: \g<0>]", text)

    return processed_text

# Apply preprocessing to each fragment
for fragment in splits_all_documents:
    fragment.page_content = preprocess_formula(fragment.page_content)

# Embedding model
embedding_model = VertexAIEmbeddings(model="text-embedding-005")
# dimension 768
# the embedding model choosen doesn't let the acces to the tokenizer
# so a default tokenizer is choosen just to figure if the fragments use less than
# then maximum number of tokens
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2', trust_remote_code=True)

# Maximum number of tokens supported by the embedding model
max_tokens =  3072
# max_tokens = tokenizer.model_max_length
print('Maximum tokens:', max_tokens)
# Count the tokens of each fragment
tokens_counts = [tokenizer(sentence.page_content, padding=False, truncation=False,
                           return_tensors='pt')['input_ids'].shape[1]
                           for sentence in splits_all_documents]
print('Total number of tokens in the documents:', sum(tokens_counts))

max_3 = heapq.nlargest(3, set(tokens_counts))
print('Top 3 fragments with the most tokens:')
for i, maximo in enumerate(max_3):
    print(f'Fragment {i+1}:')
    print(splits_all_documents[tokens_counts.index(maximo)].page_content)
    print(f'\n################################')

min_3 = heapq.nsmallest(3, set(tokens_counts))
print("\nTop 3 fragments with the least tokens:")
for i, min in enumerate(min_3):
    print(f'Fragment {i+1}:')
    print(splits_all_documents[tokens_counts.index(min)].page_content)
    print(f'\n################################')

# Plots the tokens of each fragment and compare to the maximum
plt.plot(tokens_counts, marker='o', color='blue', linestyle='', alpha=0.3)
plt.axhline(y=max_tokens, color='r', linestyle='--', label='Max')
plt.xlabel('Index')
plt.ylabel('Number of tokens')
plt.title('Tokens of each text fragment')
plt.grid(True)
plt.legend()
plt.show()

# max batch size for ChromaDB
batch_size = 5461
# Create the collection initially with a first load of documents
vectorstore = Chroma.from_documents(
    documents=splits_all_documents[:batch_size],  # Process an initial batch within the limit
    embedding=embedding_model,
    collection_name='vectorstore',
    persist_directory="./chroma/",
    # Without collection_metadata, it will give negative similarity_score_thresholds.
    collection_metadata={"hnsw:space": "cosine"}
)

# Add the remaining documents
for i in range(batch_size, len(splits_all_documents), batch_size):
    batch = splits_all_documents[i:i + batch_size]
    vectorstore.add_documents(documents=batch)

if __name__ == '__main__':
    print('First metadata of the documents:')
    for i in range(3):
        print(f'{splits_all_documents[i].metadata}')
        print(f'\n################################')

    print('\nFirst fragments:')
    for i in range(3):
        text = splits_all_documents[i].page_content.replace('\n', ' ')
        print(f'Fragment {i+1}:\n', text)
        print(f'\n################################')

    # In case the selected fragments don't exist
    try:
        print('\nRandom fragments:')
        i = random.randint(400, 800)
        for i in range(i, i+3):
            text = splits_all_documents[i].page_content.replace('\n', ' ')
            print(f'Fragment {i+1}:\n', text)
            print(f'\n################################')
    except IndexError:
        print('Error selecting random fragments:', IndexError)