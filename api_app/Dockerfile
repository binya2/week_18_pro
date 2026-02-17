FROM python:3.10-slim

WORKDIR /app

COPY api_app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared /app/shared
COPY api_app /app/api_app

ENV PYTHONPATH=/app

CMD ["python", "api_app/app/main.py"]