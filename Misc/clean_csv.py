# Script used to clean the CSV file for better conversion in later stages

import pandas as pd

# Load the original CSV
file_path = './flipkart_product_catalogue.csv'
product_data = pd.read_csv(file_path)

# Clean the data
product_data['retail_price'].fillna(0, inplace=True)
product_data['discounted_price'].fillna(0, inplace=True)
product_data['image'].fillna('[]', inplace=True)
product_data['description'].fillna('No description available', inplace=True)
product_data['brand'].fillna('Unknown', inplace=True)
product_data['product_specifications'].fillna('{}', inplace=True)

# Save the cleaned data to a new CSV file
cleaned_file_path_updated = './cleaned_flipkart_product_catalogue_updated.csv'
product_data.to_csv(cleaned_file_path_updated, index=False)
