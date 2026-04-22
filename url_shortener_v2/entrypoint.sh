#!/bin/bash
set -e

echo "Iniciando URL Shortener API v2..."

# Aguardar banco de dados ficar disponível
echo "Aguardando banco de dados..."
while ! nc -z db 5432; do
  echo "Banco ainda não está pronto... aguardando 1 segundo"
  sleep 1
done
echo "Banco de dados disponível!"

# Executar migrations (se houver alembic configurado)
# alembic upgrade head

# Popular banco com dados iniciais (opcional, comentado por segurança)
# python seed.py

echo "Iniciando servidor FastAPI..."
exec uvicorn main:app --host 0.0.0.0 --port 5000 --reload
