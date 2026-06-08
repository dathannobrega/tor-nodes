"""Serviço para buscar URLs maliciosas do banco de dados honeypot.

Este serviço degrada graciosamente: quando o banco de dados não está
configurado ou está inacessível, retorna uma lista vazia em vez de propagar
o erro de conexão para o cliente. Detalhes técnicos da falha ficam apenas
no log do servidor, nunca na resposta HTTP.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from urllib.parse import urlparse

import pymysql

from config.settings import Config

logger = logging.getLogger(__name__)


class UrlService:
    """Serviço para consulta de URLs maliciosas recentes."""

    CONNECT_TIMEOUT_SECONDS = 5

    def __init__(self) -> None:
        self.db_config = {
            'host': Config.DB_HOST,
            'port': Config.DB_PORT,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD,
            'database': Config.DB_NAME,
            'cursorclass': pymysql.cursors.DictCursor,
            'connect_timeout': self.CONNECT_TIMEOUT_SECONDS,
            'read_timeout': self.CONNECT_TIMEOUT_SECONDS,
        }
        self.legit_domains = {d.lower() for d in Config.LEGIT_DOMAINS}

    def is_configured(self) -> bool:
        """Indica se há configuração mínima de banco para consultar o honeypot."""
        return bool(Config.DB_NAME and Config.DB_HOST and Config.DB_USER)

    def get_recent_urls(self) -> Tuple[List[str], Optional[datetime]]:
        """Retorna URLs com atividade nos últimos 30 dias, excluindo domínios legítimos.

        Nunca levanta erro de banco para o chamador: se o banco não estiver
        configurado ou acessível, retorna ``([], None)`` e registra o motivo
        no log do servidor.
        """
        if not self.is_configured():
            logger.info("Honeypot DB não configurado; retornando lista vazia.")
            return [], None

        cutoff = datetime.utcnow() - timedelta(days=30)
        query = "SELECT url, last_view FROM urls WHERE last_view >= %s"

        try:
            connection = pymysql.connect(**self.db_config)
        except pymysql.MySQLError as exc:
            logger.warning("Honeypot DB indisponível; retornando lista vazia. Detalhe: %s", exc)
            return [], None

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (cutoff,))
                rows = cursor.fetchall()
        except pymysql.MySQLError as exc:
            logger.warning("Falha ao consultar honeypot DB; retornando lista vazia. Detalhe: %s", exc)
            return [], None
        finally:
            connection.close()

        urls: List[str] = []
        last_update: Optional[datetime] = None
        for row in rows:
            url = row.get('url')
            last_view = row.get('last_view')
            if last_view and (last_update is None or last_view > last_update):
                last_update = last_view
            if not url:
                continue
            domain = urlparse(url).netloc.lower()
            if domain and domain not in self.legit_domains:
                urls.append(url)

        return urls, last_update
