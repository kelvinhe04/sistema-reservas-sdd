# Empaquetado opcional (T-17). Construir: docker build -t reservas .
# Ejecutar: docker run -p 8000:8000 -e ADMIN_KEY=una-clave -v reservas-data:/app/data reservas
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=America/Panama

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

# La base SQLite se crea en /app/data/reservas.db; se monta como volumen para conservarla.
VOLUME /app/data
EXPOSE 8000

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
