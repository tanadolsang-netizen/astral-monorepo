FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl && \
    apt-get install -y gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY backend/ /app/backend/

ENV PYTHONPATH=/app/backend
CMD ["sh", "-c", "cd backend && uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
