FROM python:3.10-slim

WORKDIR /app

COPY preprocessor/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared /app/shared

COPY preprocessor /app/preprocessor

ENV PYTHONPATH=/app

CMD ["python", "preprocessor/preprocessor.py"]