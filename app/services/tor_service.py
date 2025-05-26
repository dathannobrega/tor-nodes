"""
Serviço para busca e processamento de dados dos nós Tor
"""

import logging
import threading
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from config.settings import Config
from services.cache_service import CacheService


class TorNodeData:
    """Classe para representar dados de um nó Tor"""
    
    def __init__(self, relay_data: Dict[str, Any]):
        self.nickname = relay_data.get('n', 'Unknown')
        self.fingerprint = relay_data.get('f', '')
        self.addresses = relay_data.get('a', [])
        self.running = relay_data.get('r', False)
        self.flags = relay_data.get('s', [])
        self.bandwidth = relay_data.get('bw', 0)
        self.country = relay_data.get('c', 'Unknown')
        self.as_name = relay_data.get('as_name', 'Unknown')
        self.first_seen = relay_data.get('f_s', '')
        self.last_seen = relay_data.get('l_s', '')
        self.exit_node = 'Exit' in self.flags
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'nickname': self.nickname,
            'fingerprint': self.fingerprint,
            'addresses': self.addresses,
            'running': self.running,
            'flags': self.flags,
            'bandwidth': self.bandwidth,
            'country': self.country,
            'as_name': self.as_name,
            'first_seen': self.first_seen,
            'last_seen': self.last_seen,
            'exit_node': self.exit_node
        }


class TorService:
    """Serviço principal para gerenciamento de dados dos nós Tor"""
    
    def __init__(self, cache_service: CacheService, request_timeout: int = 30):
        self.cache_service = cache_service
        self.request_timeout = request_timeout
        self.sources = Config.get_tor_sources()
        self.session = self._create_session()
        self._background_thread: Optional[threading.Thread] = None
        self._stop_background = threading.Event()
        
        self._start_background_updater()
    
    def _create_session(self) -> requests.Session:
        """Cria uma sessão HTTP com retry e timeout configurados"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=Config.MAX_RETRIES,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _start_background_updater(self) -> None:
        """Inicia thread de atualização em background"""
        self._background_thread = threading.Thread(
            target=self._background_updater,
            daemon=True
        )
        self._background_thread.start()
        logging.info("Background updater iniciado")
    
    def _background_updater(self) -> None:
        """Atualiza caches em background"""
        while not self._stop_background.is_set():
            try:
                if self.cache_service.needs_detailed_cache_update():
                    self.fetch_detailed_nodes()
                
                if self.cache_service.needs_exit_cache_update():
                    self.fetch_exit_nodes()
                    
            except Exception as e:
                logging.error(f"Erro no background updater: {e}")
            
            # Aguarda 60 segundos antes da próxima verificação
            self._stop_background.wait(60)
    
    def stop_background_updater(self) -> None:
        """Para o background updater"""
        self._stop_background.set()
        if self._background_thread:
            self._background_thread.join()
    
    def fetch_exit_nodes(self) -> List[str]:
        """Busca lista de IPs dos nós exit"""
        try:
            logging.info("Buscando dados dos nós exit...")
            
            response = self.session.get(
                self.sources['exit_addresses'],
                timeout=self.request_timeout
            )
            response.raise_for_status()
            
            ips = []
            ips_with_timestamp = []
            
            for line in response.text.splitlines():
                if line.startswith('ExitAddress'):
                    parts = line.split()
                    if len(parts) >= 3:
                        ip = parts[1]
                        timestamp = ' '.join(parts[2:])
                        ips.append(ip)
                        ips_with_timestamp.append(f"{ip} # Last seen: {timestamp}")
            
            self.cache_service.save_exit_cache(ips, ips_with_timestamp)
            logging.info(f"Dados dos nós exit atualizados: {len(ips)} IPs")
            
            return ips
            
        except requests.RequestException as e:
            logging.error(f"Erro ao buscar nós exit: {e}")
            raise
        except Exception as e:
            logging.error(f"Erro inesperado ao buscar nós exit: {e}")
            raise
    
    def fetch_detailed_nodes(self) -> List[Dict[str, Any]]:
        """Busca dados detalhados dos nós Tor"""
        try:
            logging.info("Buscando dados detalhados dos nós Tor...")
            
            response = self.session.get(
                self.sources['onionoo'],
                timeout=self.request_timeout
            )
            response.raise_for_status()
            
            data = response.json()
            nodes = []
            
            if 'relays' in data:
                for relay in data['relays']:
                    node = TorNodeData(relay)
                    nodes.append(node.to_dict())
            
            self.cache_service.save_detailed_cache(nodes)
            logging.info(f"Dados detalhados atualizados: {len(nodes)} nós")
            
            return nodes
            
        except requests.RequestException as e:
            logging.error(f"Erro ao buscar dados detalhados: {e}")
            raise
        except Exception as e:
            logging.error(f"Erro inesperado ao buscar dados detalhados: {e}")
            raise
    
    def get_exit_nodes(self) -> List[str]:
        """Retorna lista de IPs dos nós exit"""
        if self.cache_service.needs_exit_cache_update():
            return self.fetch_exit_nodes()
        return self.cache_service.load_exit_cache()
    
    def get_detailed_nodes(self) -> List[Dict[str, Any]]:
        """Retorna dados detalhados dos nós"""
        if self.cache_service.needs_detailed_cache_update():
            return self.fetch_detailed_nodes()
        return self.cache_service.load_detailed_cache()
    
    def get_running_nodes(self) -> List[Dict[str, Any]]:
        """Retorna apenas nós ativos"""
        nodes = self.get_detailed_nodes()
        return [node for node in nodes if node.get('running', False)]
    
    def get_exit_nodes_detailed(self) -> List[Dict[str, Any]]:
        """Retorna apenas nós exit com dados detalhados"""
        nodes = self.get_detailed_nodes()
        return [node for node in nodes if node.get('exit_node', False)]
    
    def get_nodes_by_country(self, country_code: str) -> List[Dict[str, Any]]:
        """Retorna nós de um país específico"""
        nodes = self.get_detailed_nodes()
        return [
            node for node in nodes 
            if node.get('country', '').upper() == country_code.upper()
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas dos nós"""
        nodes = self.get_detailed_nodes()
        
        total_nodes = len(nodes)
        running_nodes = len([n for n in nodes if n.get('running', False)])
        exit_nodes = len([n for n in nodes if n.get('exit_node', False)])
        
        countries = {}
        total_bandwidth = 0
        flags_count = {}
        
        for node in nodes:
            # Contagem por país
            country = node.get('country', 'Unknown')
            countries[country] = countries.get(country, 0) + 1
            
            # Bandwidth total
            total_bandwidth += node.get('bandwidth', 0)
            
            # Contagem de flags
            for flag in node.get('flags', []):
                flags_count[flag] = flags_count.get(flag, 0) + 1
        
        return {
            'total_nodes': total_nodes,
            'running_nodes': running_nodes,
            'offline_nodes': total_nodes - running_nodes,
            'exit_nodes': exit_nodes,
            'total_bandwidth': total_bandwidth,
            'countries_count': len(countries),
            'top_countries': sorted(
                countries.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10],
            'flags_distribution': flags_count,
            'last_updated': self.cache_service.detailed_cache['last_updated'].isoformat() 
            if self.cache_service.detailed_cache['last_updated'] else None
        }
    
    def initialize_cache(self) -> None:
        """Inicializa os caches se necessário"""
        try:
            if self.cache_service.needs_exit_cache_update():
                logging.info("Inicializando cache de exit nodes...")
                self.fetch_exit_nodes()
            
            if self.cache_service.needs_detailed_cache_update():
                logging.info("Inicializando cache detalhado...")
                self.fetch_detailed_nodes()
                
        except Exception as e:
            logging.error(f"Erro ao inicializar cache: {e}")
            raise
