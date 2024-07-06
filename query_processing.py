# Script for extracting top-k matching elements from the catalogue index (FAISS)

from sentence_transformers import SentenceTransformer
import os
import json
import faiss


def search_index(index_file, json_file, user_query):

    # Loading the saved FAISS index
    index = faiss.read_index(index_file)

    # Load a pre-trained model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Set environment variable to suppress TensorFlow warning (optional)
    os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

    #Loading the converted JSON Data
    with open(json_file, 'r') as file:
        product_data = json.load(file)

    # Convert query to embedding
    query_embedding = model.encode([user_query])

    # Search the index for similar embeddings
    k = 5  # Number of top results to retrieve

    distances, indices = index.search(query_embedding, k)

    # Retrieve the top products
    top_products = [product_data[idx] for idx in indices[0]]

    results = "The following products match the query: \n" + "\n".join(
        # [json.dumps(product, indent=2) for product in top_products]
        [json.dumps(product) for product in top_products]
    )

    return results




