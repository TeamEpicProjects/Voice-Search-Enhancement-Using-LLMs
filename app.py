# Main Script for running the Streamlit application
# Use command 'streamlit run app.py' to run the app using CLI (Command Prompt or Terminal)
# NOTE: Make sure you update the API Keys in the .env file before proceeding to run the script.

import torch
from transformers import pipeline
from speech_to_text import get_transcript
from get_search_dict import get_clean_prod_info
from streamlit_carousel import carousel
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import base64

def get_base64_placeholder_image():
    # Create a simple placeholder image
    img = Image.new('RGB', (200, 200), color=(211, 211, 211))  # Light gray background
    draw = ImageDraw.Draw(img)

    # Load a default font
    font = ImageFont.load_default()

    # Add text
    text = "Image URL\nBroken"
    text_color = (255, 0, 0)  # Red color

    # Get text size
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Calculate position to center the text
    position = ((200 - text_width) / 2, (200 - text_height) / 2)

    # Draw the text
    draw.text(position, text, font=font, fill=text_color, align="center")

    # Save the image to a buffer
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


# Generate the base64 string
base64_placeholder = get_base64_placeholder_image()

def load_image(url, base64_placeholder):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        img.load()  # This line will verify that the image can be loaded
        return url
    except Exception as e:
        print(f"Failed to load image from {url}: {str(e)}")
        return f"data:image/png;base64,{base64_placeholder}"
    

    
# Streamlit UI
st.set_page_config(page_title="E-commerce Search Enhancer", layout="wide")

# Read and inject custom CSS
def inject_css(css_file_path):
    with open(css_file_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

inject_css('./styles.css')

# Page title
st.markdown("<h1 style='text-align: center;'>Flipkart Products Voice-Based Search Enhancement</h1>", unsafe_allow_html=True)

# Using columns for centering
_, col2, _ = st.columns([1, 2, 1])

with col2:
    st.markdown('<div class="centered-image">', unsafe_allow_html=True)
    st.image("mic_logo.png")
    st.markdown('</div>', unsafe_allow_html=True)

    # Create a button
    mic_button = st.button('Click to Speak', key="mic_button")

# Initialize session state
if 'query_results' not in st.session_state:
    st.session_state['query_results'] = None

if 'model_initialized' not in st.session_state:
    st.session_state['model_initialized'] = False

if 'recording_stopped' not in st.session_state:
    st.session_state['recording_stopped'] = True

# Display messages
if not st.session_state['model_initialized']:
    with col2:
        st.markdown('<div style="text-align: center;">Good things take time! Please wait while we warm-up our models...</div>', unsafe_allow_html=True)
        with st.spinner('Initializing models...'):
            model_name = "openai/whisper-small"
            device = "cuda" if torch.cuda.is_available() else "cpu"
            whisper_pipeline = pipeline("automatic-speech-recognition", model=model_name, device=device)
        st.session_state['whisper_pipeline'] = whisper_pipeline
        st.session_state['model_initialized'] = True
        st.rerun()

whisper_pipeline = st.session_state['whisper_pipeline']

# Handle the click event
if mic_button:
    st.session_state['recording_stopped'] = False
    with col2:
        st.markdown('<div class="message-bar">Speak Now...</div>', unsafe_allow_html=True)
        
        transcript = get_transcript(whisper_pipeline)
        st.session_state['query_results'] = get_clean_prod_info(transcript)


# Creating a results container   
results_container = st.empty()

# Displaying the quey search results
if st.session_state['query_results']:
    with results_container.container():
        st.markdown('<div class="message-bar">Your results:</div>', unsafe_allow_html=True)
        
        for index, product in enumerate(st.session_state['query_results']):
            with st.container():
                left, right = st.columns([1, 2])
                with left:
                    carousel_items = []
                    images = product["images"]

                    if not images:
                        carousel_items.append(dict(
                            title = "No Image Available",
                            text = "No images available for this product.",
                            img = f"data:image/png;base64,{base64_placeholder}"
                        ))
                    
                    else:
                        for i, image_url in enumerate(images):
                            
                            loaded_image = load_image(image_url, base64_placeholder)
                            
                            carousel_items.append(dict(
                                title = "",
                                text = "",
                                img = loaded_image
                            ))
                    
                    st.markdown('<div class="carousel-container">', unsafe_allow_html=True)
                    carousel(items=carousel_items, key=f"carousel_{index}")
                    st.markdown('</div>', unsafe_allow_html=True)

                with right:
                    st.markdown('<div class="product-details">', unsafe_allow_html=True)
                    st.markdown(f'<p class="product-name"><strong>Product Name:</strong> {product.get("name", "N/A")}</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="product-price"><strong>Price:</strong> {product.get("price", "N/A")}</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="product-category"><strong>Category:</strong> {product.get("category", "N/A")}</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="product-description"><strong>Description:</strong></p>', unsafe_allow_html=True)
                    st.markdown(f'<div class="description">{product.get("description", "N/A")}</div>', unsafe_allow_html=True)
                    st.markdown(f'<p class="product-specifications"><strong>Specifications:</strong></p>', unsafe_allow_html=True)
                    
                    specifications_html = product.get("specifications", "N/A").replace('\n', '<br>')
                    st.markdown(f'<div class="specifications">{specifications_html}</div>', unsafe_allow_html=True)
                    
                    st.markdown(f'<p class="product-url"><strong>Buy Now:</strong> <a href="{product.get("url", "#")}">{product.get("url", "N/A")}</a></p>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
else:
    with col2:
        st.markdown('<div class="message-bar">Your results will appear here...</div>', unsafe_allow_html=True)