FROM python:3.10-slim

WORKDIR /app

COPY kitchen/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared /app/shared

COPY kitchen /app/kitchen

ENV PYTHONPATH=/app

CMD ["python", "kitchen/kitchen_worker.py"]