# Script for creating a FAISS (Facebook AI Similarity Search) index from the JSON dataset of the product catalogue. 
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
import os

# Set environment variable to suppress TensorFlow warning (optional)
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

#Loading the converted JSON Data
with open('./flipkart_product_catalogue_cleaned.json', 'r') as file:
    product_data = json.load(file)

#Load a pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

#Extract relevant text data for embeddings
text_data = [
    '{} {} {} {} {} {} {} {}'.format(
        item['product_name'],
        item['product_category_tree'],
        item['description'],
        item['product_rating'],
        item['overall_rating'],
        item['brand'],
        item['product_specifications'],
        item['is_FK_Advantage_product']
    ) for item in product_data
]

#Generate the embeddings
embeddings = model.encode(text_data, show_progress_bar=True)

#Convert embeddings to a numpy array
embeddings_np = np.array(embeddings)

#Initialize FAISS Index
dimension = embeddings_np.shape[1]
index = faiss.IndexFlatL2(dimension)

#Add the embeddings to the index
index.add(embeddings_np)

#Saving the index for later use
faiss.write_index(index, './flipkart_products_cleaned.index')