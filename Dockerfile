# Build stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Buat direktori untuk data & logs
RUN mkdir -p data logs

# Environment
ENV PYTHONUNBUFFERED=1

# Run bot
CMD ["python", "main.py"]