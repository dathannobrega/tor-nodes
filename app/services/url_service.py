"""Serviço para buscar URLs maliciosas do banco de dados honeypot"""

from datetime import datetime, timedelta
from typing import List, Tuple
from urllib.parse import urlparse

import pymysql

from config.settings import Config


class UrlService:
    """Serviço para consulta de URLs recentes"""

    def __init__(self) -> None:
        self.db_config = {
            'host': Config.DB_HOST,
            'port': Config.DB_PORT,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD,
            'database': Config.DB_NAME,
            'cursorclass': pymysql.cursors.DictCursor,
        }
        self.legit_domains = {d.lower() for d in Config.LEGIT_DOMAINS}

    def get_recent_urls(self) -> Tuple[List[str], datetime]:
        """Retorna URLs com atividade nos últimos 30 dias excluindo domínios legítimos"""
        cutoff = datetime.utcnow() - timedelta(days=30)
        query = "SELECT url, last_view FROM urls WHERE last_view >= %s"
        connection = pymysql.connect(**self.db_config)
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (cutoff,))
                rows = cursor.fetchall()
        finally:
            connection.close()

        urls: List[str] = []
        last_update = cutoff
        for row in rows:
            url = row.get('url')
            last_view = row.get('last_view')
            if last_view and last_view > last_update:
                last_update = last_view
            domain = urlparse(url).netloc.lower()
            if domain and domain not in self.legit_domains:
                urls.append(url)

        return urls, last_update
