# Etapa única: app + nginx juntos
FROM python:3.11-slim

# Instala o nginx
RUN apt-get update && \
    apt-get install -y nginx && \
    rm -rf /var/lib/apt/lists/*

# Cria diretório da aplicação
WORKDIR /app

# Copia requirements e instala (Flask, requests, gunicorn)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY main.py index.html tor_nodes_server.py /app

# Substitui configuração do nginx
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Garante permissão de execução se precisar
RUN chmod +x /usr/sbin/nginx

# Expõe a porta 80
EXPOSE 80

# CMD inicia Gunicorn (no 127.0.0.1:8000) e, em paralelo, o nginx
CMD ["sh", "-c", "\
    gunicorn --bind 127.0.0.1:8000 main:app & \
    nginx -g 'daemon off;' \
"]
