"""
Funções de validação
"""

import re
from typing import Any


def validate_country_code(country_code: str) -> bool:
    """Valida código de país (2 letras)"""
    if not isinstance(country_code, str):
        return False
    
    # Código de país deve ter exatamente 2 letras
    pattern = r'^[A-Za-z]{2}$'
    return bool(re.match(pattern, country_code))


def validate_ip_address(ip: str) -> bool:
    """Valida endereço IP"""
    if not isinstance(ip, str):
        return False
    
    # Regex simples para IPv4
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False
    
    # Verifica se cada octeto está no range válido
    octets = ip.split('.')
    return all(0 <= int(octet) <= 255 for octet in octets)


def sanitize_input(value: Any, max_length: int = 100) -> str:
    """Sanitiza entrada do usuário"""
    if not isinstance(value, str):
        value = str(value)
    
    # Remove caracteres perigosos
    sanitized = re.sub(r'[<>"\']', '', value)
    
    # Limita o tamanho
    return sanitized[:max_length]
