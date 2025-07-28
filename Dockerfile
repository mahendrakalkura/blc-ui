# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install Node.js first
RUN apt-get update && \
    apt-get install -y curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g broken-link-checker && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy package files first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose the port Flask will run on
EXPOSE 5000

# Set environment variables for development
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1
ENV PYTHONUNBUFFERED=1

# Run Flask app with debug mode enabled
CMD ["python", "main.py"]
