FROM python:3.10-slim

WORKDIR /app

COPY text/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared /app/shared

COPY text /app/text

ENV PYTHONPATH=/app

CMD ["python", "text/text_worker.py"]