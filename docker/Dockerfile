FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 1. Criação de usuário não-root para rodar o serviço
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# 2. Definir diretório de trabalho
WORKDIR /app

# 3. Instalar dependências antes de copiar o código para aproveitar cache de build
COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar o restante do código da aplicação
COPY app/ ./

# 5. Ajustar permissões para o usuário não-root
RUN chown -R appuser:appuser /app

# 6. Mudar para o usuário não-root
USER appuser

# 7. Expor porta
EXPOSE 8000

# 8. Healthcheck (usa Python para não depender de curl, ausente na imagem slim)
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health', timeout=3).status == 200 else 1)" || exit 1

# 9. Inicia o WebServer
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "main:app"]
