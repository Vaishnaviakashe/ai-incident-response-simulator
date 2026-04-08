# FROM python:3.11-slim

# # Metadata
# LABEL org.opencontainers.image.title="AI Incident Response Environment"
# LABEL org.opencontainers.image.description="OpenEnv RL environment for cybercrime and legal incident handling"
# LABEL tags="openenv"

# # System deps
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# # App directory
# WORKDIR /app

# # Install Python deps first (layer caching)
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy project
# COPY . .

# # Environment variable defaults (HF_TOKEN must be provided at runtime)
# ENV API_BASE_URL="https://api.openai.com/v1"
# ENV MODEL_NAME="gpt-4.1-mini"
# ENV PYTHONUNBUFFERED=1
# ENV PYTHONPATH=/app

# # Expose port for HuggingFace Spaces (optional HTTP server)
# EXPOSE 7860

# # Default: run inference baseline
# CMD ["python", "inference.py"]

FROM python:3.11-slim

LABEL tags="openenv"

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV API_BASE_URL="https://router.huggingface.co/v1"
ENV MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 7860

# Run Gradio dashboard (HF Spaces) — inference.py still works standalone
CMD ["python", "app.py"]
