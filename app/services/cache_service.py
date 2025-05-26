"""
Serviço de gerenciamento de cache
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from config.settings import Config


@dataclass
class CacheInfo:
    """Informações sobre o cache"""
    exists: bool
    last_update: Optional[datetime]
    needs_update: bool
    item_count: int


class CacheService:
    """Serviço responsável pelo gerenciamento de cache"""
    
    def __init__(self, cache_ttl_hours: int = 12, detailed_cache_ttl_minutes: int = 5):
        self.cache_ttl_hours = cache_ttl_hours
        self.detailed_cache_ttl_minutes = detailed_cache_ttl_minutes
        self.cache_paths = Config.get_cache_paths()
        self.detailed_cache: Dict[str, Any] = {
            'data': [],
            'last_updated': None
        }
        
        self._ensure_cache_directory()
    
    def _ensure_cache_directory(self) -> None:
        """Garante que o diretório de cache existe"""
        cache_dir = Config.CACHE_DIR
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
            logging.info(f"Diretório de cache criado: {cache_dir}")
    
    def needs_exit_cache_update(self) -> bool:
        """Verifica se o cache de exit nodes precisa ser atualizado"""
        cache_file = self.cache_paths['exit_cache']
        timestamp_file = self.cache_paths['exit_timestamp']
        
        if not os.path.exists(cache_file) or not os.path.exists(timestamp_file):
            return True
        
        try:
            with open(timestamp_file, 'r', encoding='utf-8') as f:
                timestamp = float(f.read().strip())
            
            last_update = datetime.utcfromtimestamp(timestamp)
            time_diff = datetime.utcnow() - last_update
            
            return time_diff > timedelta(hours=self.cache_ttl_hours)
        except (ValueError, IOError) as e:
            logging.warning(f"Erro ao verificar timestamp do cache: {e}")
            return True
    
    def needs_detailed_cache_update(self) -> bool:
        """Verifica se o cache detalhado precisa ser atualizado"""
        if self.detailed_cache['last_updated'] is None:
            return True
        
        time_diff = datetime.utcnow() - self.detailed_cache['last_updated']
        return time_diff > timedelta(minutes=self.detailed_cache_ttl_minutes)
    
    def save_exit_cache(self, ips: List[str], ips_with_timestamp: List[str]) -> None:
        """Salva o cache de exit nodes"""
        try:
            # Cache simples com IPs
            with open(self.cache_paths['exit_cache'], 'w', encoding='utf-8') as f:
                f.write('\n'.join(ips))
            
            # Cache detalhado com timestamps
            with open(self.cache_paths['detailed_cache'], 'w', encoding='utf-8') as f:
                f.write('\n'.join(ips_with_timestamp))
            
            # Timestamp
            with open(self.cache_paths['exit_timestamp'], 'w', encoding='utf-8') as f:
                f.write(str(time.time()))
            
            logging.info(f"Cache de exit nodes salvo: {len(ips)} IPs")
            
        except IOError as e:
            logging.error(f"Erro ao salvar cache de exit nodes: {e}")
            raise
    
    def load_exit_cache(self) -> List[str]:
        """Carrega o cache de exit nodes"""
        try:
            with open(self.cache_paths['exit_cache'], 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except IOError as e:
            logging.error(f"Erro ao carregar cache de exit nodes: {e}")
            return []
    
    def save_detailed_cache(self, nodes: List[Dict[str, Any]]) -> None:
        """Salva o cache detalhado dos nós"""
        self.detailed_cache['data'] = nodes
        self.detailed_cache['last_updated'] = datetime.utcnow()
        logging.info(f"Cache detalhado salvo: {len(nodes)} nós")
    
    def load_detailed_cache(self) -> List[Dict[str, Any]]:
        """Carrega o cache detalhado dos nós"""
        return self.detailed_cache['data']
    
    def get_exit_cache_info(self) -> CacheInfo:
        """Retorna informações sobre o cache de exit nodes"""
        cache_file = self.cache_paths['exit_cache']
        timestamp_file = self.cache_paths['exit_timestamp']
        
        exists = os.path.exists(cache_file)
        last_update = None
        item_count = 0
        
        if exists:
            try:
                # Conta itens
                with open(cache_file, 'r', encoding='utf-8') as f:
                    item_count = len([line for line in f if line.strip()])
                
                # Pega timestamp
                if os.path.exists(timestamp_file):
                    with open(timestamp_file, 'r', encoding='utf-8') as f:
                        timestamp = float(f.read().strip())
                    last_update = datetime.utcfromtimestamp(timestamp)
                    
            except (ValueError, IOError) as e:
                logging.warning(f"Erro ao obter informações do cache: {e}")
        
        return CacheInfo(
            exists=exists,
            last_update=last_update,
            needs_update=self.needs_exit_cache_update(),
            item_count=item_count
        )
    
    def get_detailed_cache_info(self) -> CacheInfo:
        """Retorna informações sobre o cache detalhado"""
        return CacheInfo(
            exists=len(self.detailed_cache['data']) > 0,
            last_update=self.detailed_cache['last_updated'],
            needs_update=self.needs_detailed_cache_update(),
            item_count=len(self.detailed_cache['data'])
        )
