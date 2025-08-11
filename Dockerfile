# Start from the Python 3.9 slim base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies including build tools, tor, and ffmpeg
# Using --no-install-recommends keeps the image smaller
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tor \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker's layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code and the startup script
COPY . .

# Make the startup script executable
RUN chmod +x ./start.sh

# Expose ports for the app and Tor
EXPOSE 8080 9050

# Set the startup script as the container's command
CMD ["./start.sh"]
