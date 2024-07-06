# Script for enabling prompt chaining and leveraging LLMs for cleaner results
# NOTE: Make sure you update the API Keys in the .env file before proceeding to run the script.
from prompts import re_searcher_dict, quarry_prompt_new
from query_processing import search_index
from groq import Groq
from dotenv import load_dotenv
import os
import ast
import openai
import streamlit as st

# Loading the API key from the .env file
load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")
openai.api_key = os.getenv("PERSONAL_OPENAI_KEY")

# Function for performing LLM API Calls - Groq
def get_llm_output(system_prompt, user_prompt):

    client = Groq(api_key = groq_key)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role":"system",
                "content": system_prompt,
            },

            {
                "role":"user",
                "content": user_prompt,
            },
        ],
        model="llama3-70b-8192",
        temperature=0.3,  # Low temperature for less randomness
        top_p=0.8,  # Moderate top-p for some diversity
    )

    return chat_completion.choices[0].message.content

# Function for performing LLM API Calls - OpenAI
# Uncomment the below function if you wish to use OpenAI's API. When doing so, make sure you comment the above function to avoid any confusion.
# def get_llm_output(system_prompt, user_prompt):

#   response = openai.ChatCompletion.create(
#     model="gpt-3.5-turbo",
#     temperature=0.3,  # Low temperature for less randomness
#     top_p=0.8,  # Moderate top-p for some diversity
#     messages=[
#             {
#                 "role":"system",
#                 "content": system_prompt,
#             },

#             {
#                 "role":"user",
#                 "content": user_prompt,
#             },
#         ],)

#   response_content = response.choices[0].message.content
  
#   return response_content

# Enabling audio input from the user
# user_input_transcript = get_transcript()

def get_clean_prod_info(user_input_transcript):

    print("Converting user transcript to crisp search...")
    # Converting the transcript to crisp and short search query
    user_search_query = get_llm_output(quarry_prompt_new, user_input_transcript)

    print("Query Generated - ", user_search_query)

    # Next, getting the results from the Vector Database matching the user's query
    # Loading required catalogue files"
    flipkart_product_index = "./flipkart_products_cleaned.index"
    flipkart_product_json = "./flipkart_products_cleaned.json"

    print("Getting search query results...")
    # Running the query on the loaded files
    query_results = search_index(flipkart_product_index, flipkart_product_json, user_search_query)

    print("Got the query results! Prettyfying...")
    # Finally, prettifying the results with LLM
    search_results = get_llm_output(re_searcher_dict, query_results)

    try:
        search_results_list = ast.literal_eval(search_results)
        return search_results_list

    except Exception as e:
       print(e) #Print the error on the CLI
       st.warning('Oops! An internal error has occured, please try again :(', icon="⚠️") 