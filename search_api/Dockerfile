FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY search_api/ ./search_api
COPY scripts/ ./scripts

EXPOSE 8000

CMD ["uvicorn", "search_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
