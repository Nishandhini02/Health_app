# # Use a slim Python image
# FROM python:3.10-slim

# # Install system dependencies (Tesseract and its libraries)
# RUN apt-get update && apt-get install -y \
#     tesseract-ocr \
#     libtesseract-dev \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# # Set the working directory
# WORKDIR /app

# # Copy and install Python requirements
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy the rest of your app
# COPY . .

# # Command to run your app
# CMD ["streamlit", "run", "app.py", "--server.port", "10000", "--server.address", "0.0.0.0"]
# Dockerfile - CORRECTED
FROM python:3.11-slim

# Install system dependencies in one layer to save space
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Use shell form so $PORT env var is expanded at runtime
CMD sh -c "streamlit run app.py \
    --server.port=${PORT:-10000} \
    --server.address=0.0.0.0 \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --server.headless=true"