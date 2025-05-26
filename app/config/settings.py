"""
Configurações da aplicação
"""

import os
from typing import Dict, Any


class Config:
    """Configurações base da aplicação"""
    
    # Servidor
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', 8000))
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Cache
    CACHE_TTL_HOURS: int = int(os.getenv('CACHE_TTL_HOURS', 12))
    DETAILED_CACHE_TTL_MINUTES: int = int(os.getenv('DETAILED_CACHE_TTL_MINUTES', 5))
    
    # Requisições
    REQUEST_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', 30))
    MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', 3))
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # Rate Limiting
    RATE_LIMIT_STORAGE: str = os.getenv('RATE_LIMIT_STORAGE', 'memory://')
    
    # Paths
    CACHE_DIR: str = os.getenv('CACHE_DIR', '/tmp')
    
    @classmethod
    def get_cache_paths(cls) -> Dict[str, str]:
        """Retorna os caminhos dos arquivos de cache"""
        return {
            'exit_cache': f"{cls.CACHE_DIR}/tor_exit_cache.txt",
            'exit_timestamp': f"{cls.CACHE_DIR}/tor_exit_timestamp.txt",
            'detailed_cache': f"{cls.CACHE_DIR}/tor_exit_cache_detailed.txt"
        }
    
    @classmethod
    def get_tor_sources(cls) -> Dict[str, str]:
        """Retorna as URLs das fontes de dados Tor"""
        return {
            'onionoo': 'https://onionoo.torproject.org/summary',
            'exit_addresses': 'https://check.torproject.org/exit-addresses'
        }


class ProductionConfig(Config):
    """Configurações para produção"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'


class DevelopmentConfig(Config):
    """Configurações para desenvolvimento"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """Configurações para testes"""
    DEBUG = True
    CACHE_TTL_HOURS = 1
    DETAILED_CACHE_TTL_MINUTES = 1
