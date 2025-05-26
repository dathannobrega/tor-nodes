"""
Definição das rotas da API
"""

import logging
from datetime import datetime
from typing import Dict, Any

from flask import Flask, render_template, Response, jsonify, request
from flask_limiter import Limiter

from services.tor_service import TorService
from utils.validators import validate_country_code
from utils.formatters import format_exit_nodes_text, format_rss_feed


def create_routes(app: Flask, tor_service: TorService, limiter: Limiter) -> None:
    """Cria e registra todas as rotas da aplicação"""
    
    @app.route('/')
    @limiter.limit("10 per minute")
    def index():
        """Página inicial com informações completas sobre o projeto"""
        try:
            exit_cache_info = tor_service.cache_service.get_exit_cache_info()
            detailed_cache_info = tor_service.cache_service.get_detailed_cache_info()
            
            stats = {
                'ip_count': exit_cache_info.item_count,
                'total_detailed_nodes': detailed_cache_info.item_count,
                'running_nodes': len(tor_service.get_running_nodes()),
                'exit_nodes': len(tor_service.get_exit_nodes_detailed()),
                'cache_exists': exit_cache_info.exists,
                'detailed_cache_exists': detailed_cache_info.exists,
                'last_update': exit_cache_info.last_update,
                'detailed_last_update': detailed_cache_info.last_update
            }
            
            return render_template('index.html', stats=stats)
            
        except Exception as e:
            logging.error(f"Erro na página inicial: {e}")
            return render_template('index.html', stats={})
    
    @app.route('/tornodes-ip.txt')
    @limiter.limit("30 per minute")
    def tornodes_ip():
        """Endpoint principal que retorna os IPs dos nós Tor em formato texto"""
        try:
            ips = tor_service.get_exit_nodes()
            cache_info = tor_service.cache_service.get_exit_cache_info()
            
            content = format_exit_nodes_text(ips, cache_info.last_update)
            return Response(content, mimetype='text/plain')
            
        except Exception as e:
            logging.error(f"Erro ao buscar tornodes-ip.txt: {e}")
            error_content = format_exit_nodes_text([], None, str(e))
            return Response(error_content, mimetype='text/plain', status=500)
    
    @app.route('/status')
    @limiter.limit("60 per minute")
    def status():
        """Endpoint de status do serviço"""
        try:
            exit_cache_info = tor_service.cache_service.get_exit_cache_info()
            detailed_cache_info = tor_service.cache_service.get_detailed_cache_info()
            
            status_info = {
                'service': 'Protexion TorNodes',
                'status': 'online',
                'cache_exists': exit_cache_info.exists,
                'last_update': exit_cache_info.last_update.isoformat() 
                if exit_cache_info.last_update else None,
                'needs_update': exit_cache_info.needs_update,
                'ip_count': exit_cache_info.item_count,
                'detailed_cache_exists': detailed_cache_info.exists,
                'detailed_last_update': detailed_cache_info.last_update.isoformat() 
                if detailed_cache_info.last_update else None,
                'total_detailed_nodes': detailed_cache_info.item_count,
                'current_time': datetime.utcnow().isoformat()
            }
            
            return jsonify(status_info)
            
        except Exception as e:
            logging.error(f"Erro no endpoint de status: {e}")
            return jsonify({
                'service': 'Protexion TorNodes',
                'status': 'error',
                'error': str(e),
                'current_time': datetime.utcnow().isoformat()
            }), 500
    
    @app.route('/api/nodes')
    @limiter.limit("20 per minute")
    def get_all_nodes():
        """Retorna todos os nós Tor detalhados"""
        try:
            nodes = tor_service.get_detailed_nodes()
            cache_info = tor_service.cache_service.get_detailed_cache_info()
            
            return jsonify({
                'status': 'success',
                'total_nodes': len(nodes),
                'last_updated': cache_info.last_update.isoformat() 
                if cache_info.last_update else None,
                'nodes': nodes
            })
            
        except Exception as e:
            logging.error(f"Erro ao buscar todos os nós: {e}")
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500
    
    @app.route('/api/nodes/running')
    @limiter.limit("20 per minute")
    def get_running_nodes():
        """Retorna apenas os nós Tor ativos"""
        try:
            running_nodes = tor_service.get_running_nodes()
            cache_info = tor_service.cache_service.get_detailed_cache_info()
            
            return jsonify({
                'status': 'success',
                'total_running_nodes': len(running_nodes),
                'last_updated': cache_info.last_update.isoformat() 
                if cache_info.last_update else None,
                'nodes': running_nodes
            })
            
        except Exception as e:
            logging.error(f"Erro ao buscar nós ativos: {e}")
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500

    
    @app.route('/api/stats')
    @limiter.limit("30 per minute")
    def get_detailed_stats():
        """Retorna estatísticas detalhadas dos nós Tor"""
        try:
            statistics = tor_service.get_statistics()
            
            return jsonify({
                'status': 'success',
                'statistics': statistics
            })
            
        except Exception as e:
            logging.error(f"Erro ao buscar estatísticas: {e}")
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500
    
    @app.route('/api/feed/rss')
    @limiter.limit("10 per minute")
    def get_rss_feed():
        """Retorna feed RSS dos nós Tor"""
        try:
            nodes = tor_service.get_detailed_nodes()[:20]  # Primeiros 20 nós
            cache_info = tor_service.cache_service.get_detailed_cache_info()
            
            rss_content = format_rss_feed(nodes, cache_info.last_update)
            return Response(rss_content, mimetype='application/rss+xml')
            
        except Exception as e:
            logging.error(f"Erro ao gerar RSS feed: {e}")
            return Response(
                "<?xml version='1.0'?><rss><channel><title>Error</title></channel></rss>",
                mimetype='application/rss+xml',
                status=500
            )
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        """Handler para rate limit excedido"""
        logging.warning(f"Rate limit excedido para IP: {request.remote_addr}")
        return jsonify({
            'status': 'error',
            'error': 'Rate limit excedido. Tente novamente mais tarde.',
            'retry_after': str(e.retry_after)
        }), 429
    
    @app.errorhandler(500)
    def internal_error_handler(e):
        """Handler para erros internos"""
        logging.error(f"Erro interno: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Erro interno do servidor'
        }), 500
