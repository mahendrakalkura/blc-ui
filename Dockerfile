# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy all project files
COPY . .
COPY static/ ./static

# Install Python dependencies
RUN pip install --no-cache-dir flask

# Install Node.js + BLC
RUN apt-get update && \
    apt-get install -y curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g broken-link-checker

# Expose the port Flask will run on
EXPOSE 5000

# Run Flask app
CMD ["python", "main.py"]