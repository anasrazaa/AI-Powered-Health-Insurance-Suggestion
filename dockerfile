# Use official Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LANGCHAIN_TRACING_V2=false \
    LANGCHAIN_ENDPOINT="https://api.langchain.com"

# Create app directory
WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy app code into the container
COPY . .

# Install additional optimized dependencies
RUN pip install langchain-openai langchain-chroma

# Set the OpenAI API key here or pass it as a runtime env variable
ENV OPENAI_API_KEY=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

# Run the optimized application
CMD ["python", "app_optimized.py"]
