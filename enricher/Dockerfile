FROM python:3.10-slim

WORKDIR /app

COPY enricher/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared /app/shared

COPY enricher /app/enricher

ENV PYTHONPATH=/app

CMD ["python", "enricher/main.py"]