FROM python:3.11-slim

# Evita arquivos .pyc e força logs do Python em tempo real no console
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala dependências do Python primeiro para aproveitar o cache de build do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do bot para o container
COPY . .

# Comando de inicialização do bot
CMD ["python", "main.py"]
