# Base image
FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    tor \
    ffmpeg \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the application code
WORKDIR /app
COPY . /app
COPY index.html /app/index.html

# Expose ports for the app and Tor
EXPOSE 8080 9050

# Start Tor and the application
CMD service tor start && python main.py
