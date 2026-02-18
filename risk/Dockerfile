FROM python:3.10-slim

WORKDIR /app

COPY risk/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared /app/shared

COPY risk /app/risk

ENV PYTHONPATH=/app

CMD ["python", "risk/risk_evaluator.py"]