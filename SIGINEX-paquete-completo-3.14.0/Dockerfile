FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código y datos que sirve la API (kb.json debe generarse antes: make kb)
COPY siginex_api.py siginex_orchestrator.py kb.json kb-version.json ./
COPY Benchmark_Market_Watch.json ./

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8080/health').status==200 else 1)"

CMD ["uvicorn", "siginex_api:app", "--host", "0.0.0.0", "--port", "8080"]
