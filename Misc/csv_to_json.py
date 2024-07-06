# Script for converting CSV file to JSON format
import pandas as pd
import json

csv_file_path = './flipkart_product_catalogue_cleaned.csv'

json_destination_file = './flipkart_product_catalogue_cleaned.json'

#Loading the CSV data
data = pd.read_csv(csv_file_path)

#Convert the dataframe to JSON
json_data = data.to_json(orient='records')

#Parse JSON Data
parsed_json = json.loads(json_data)

#Saving the converted JSON file
with open(json_destination_file, 'w') as f:
    json.dump(parsed_json, f, indent=4)

    
