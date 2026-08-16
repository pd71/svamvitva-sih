FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV and spatial graphics
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create writable directories for uploads and model weight caching
RUN mkdir -p /app/uploaded_images /app/app/ml/weights /app/svamitva_dataset_repository

COPY . .

ENV PORT=10000
EXPOSE 10000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]

