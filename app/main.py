"""
Protexion TorNodes Service
Serviço de monitoramento de nós Tor com API RESTful
"""

import logging
from datetime import datetime
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config.settings import Config
from services.tor_service import TorService
from services.cache_service import CacheService
from api.routes import create_routes
from utils.logger import setup_logger


def create_app() -> Flask:
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Setup logging
    setup_logger(app.config['LOG_LEVEL'])
    
    # Rate limiting
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
    
    # Inicializar serviços
    cache_service = CacheService(
        cache_ttl_hours=app.config['CACHE_TTL_HOURS'],
        detailed_cache_ttl_minutes=app.config['DETAILED_CACHE_TTL_MINUTES']
    )
    
    tor_service = TorService(
        cache_service=cache_service,
        request_timeout=app.config['REQUEST_TIMEOUT']
    )
    
    # Registrar rotas
    create_routes(app, tor_service, limiter)
    
    # Inicializar cache
    try:
        logging.info("Inicializando cache dos nós Tor...")
        tor_service.initialize_cache()
        logging.info("Cache inicializado com sucesso")
    except Exception as e:
        logging.error(f"Erro ao inicializar cache: {e}")
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    print("🧅 Iniciando Protexion TorNodes Service...")
    print(f"🚀 Servidor iniciado em http://localhost:{Config.PORT}")
    print("📋 Endpoints disponíveis:")
    print("   - GET / (página inicial)")
    print("   - GET /tornodes-ip.txt (lista de IPs)")
    print("   - GET /status (status do serviço)")
    print("   - GET /api/nodes (todos os nós detalhados)")
    print("   - GET /api/nodes/running (nós ativos)")
    print("   - GET /api/stats (estatísticas detalhadas)")
    print("   - GET /api/feed/rss (feed RSS)")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
