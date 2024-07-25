# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install system dependencies for ffmpeg
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the frozen requirements file first to leverage Docker cache
COPY frozen_requirements.txt /app

# Upgrade pip, setuptools, and wheel
RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies
RUN pip install --no-cache-dir -r frozen_requirements.txt

# Install Python dependencies with retries and timeout
RUN pip install --no-cache-dir --retries 5 --timeout 30 -r frozen_requirements.txt

# Copy the rest of the application code
COPY . /app

# Expose the Streamlit port
EXPOSE 8501

# Run the Streamlit application
CMD ["streamlit", "run", "app.py"]
