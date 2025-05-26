"""
Configuração de logging
"""

import logging
import sys
from typing import Optional


def setup_logger(log_level: str = 'INFO') -> None:
    """Configura o sistema de logging"""
    
    # Converter string para nível de logging
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Formato das mensagens
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configuração básica
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('/tmp/tor_nodes.log', mode='a')
        ]
    )
    
    # Configurar loggers específicos
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    logging.info(f"Sistema de logging configurado - Nível: {log_level}")
