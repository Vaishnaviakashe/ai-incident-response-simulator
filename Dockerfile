
FROM python:3.11-slim

# Required for some env dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=$PYTHONPATH:/app/server:/app
ENV API_BASE_URL="https://router.huggingface.co/v1"
ENV MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"
ENV HF_TOKEN=""


# Open the port Hugging Face expects
EXPOSE 7860

# Run using the module path to avoid import errors
CMD ["uvicorn", "inference:app", "--host", "0.0.0.0", "--port", "7860"]
# CMD ["python", "server/app.py"]