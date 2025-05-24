import requests
import json
import time
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template_string
import threading
from urllib.parse import urlparse

app = Flask(__name__)

# Cache global para armazenar dados dos nós Tor
tor_nodes_cache = {
    'data': [],
    'last_updated': None,
    'update_interval': 300  # 5 minutos
}

class TorNodesFetcher:
    def __init__(self):
        # URLs conhecidas para obter informações dos nós Tor
        self.sources = {
            'onionoo': 'https://onionoo.torproject.org/summary',
            'consensus': 'https://collector.torproject.org/recent/relay-descriptors/consensuses/',
        }
    
    def fetch_tor_nodes(self):
        """Busca informações dos nós Tor da API Onionoo"""
        try:
            print(f"[{datetime.now()}] Buscando dados dos nós Tor...")
            
            # Usando a API Onionoo do Tor Project
            response = requests.get(self.sources['onionoo'], timeout=30)
            response.raise_for_status()
            
            data = response.json()
            nodes = []
            
            if 'relays' in data:
                for relay in data['relays'][:100]:  # Limitando a 100 nós para exemplo
                    node_info = {
                        'nickname': relay.get('n', 'Unknown'),
                        'fingerprint': relay.get('f', ''),
                        'addresses': relay.get('a', []),
                        'running': relay.get('r', False),
                        'flags': relay.get('s', []),
                        'bandwidth': relay.get('bw', 0),
                        'country': relay.get('c', 'Unknown'),
                        'as_name': relay.get('as_name', 'Unknown'),
                        'first_seen': relay.get('f_s', ''),
                        'last_seen': relay.get('l_s', ''),
                    }
                    nodes.append(node_info)
            
            # Atualiza o cache
            tor_nodes_cache['data'] = nodes
            tor_nodes_cache['last_updated'] = datetime.now()
            
            print(f"[{datetime.now()}] Dados atualizados: {len(nodes)} nós encontrados")
            return nodes
            
        except requests.RequestException as e:
            print(f"Erro ao buscar dados dos nós Tor: {e}")
            return []
        except Exception as e:
            print(f"Erro inesperado: {e}")
            return []

    def should_update_cache(self):
        """Verifica se o cache precisa ser atualizado"""
        if tor_nodes_cache['last_updated'] is None:
            return True
        
        time_diff = datetime.now() - tor_nodes_cache['last_updated']
        return time_diff.total_seconds() > tor_nodes_cache['update_interval']

# Instância do fetcher
fetcher = TorNodesFetcher()

def background_updater():
    """Função para atualizar dados em background"""
    while True:
        if fetcher.should_update_cache():
            fetcher.fetch_tor_nodes()
        time.sleep(60)  # Verifica a cada minuto

# Inicia thread de atualização
update_thread = threading.Thread(target=background_updater, daemon=True)
update_thread.start()

@app.route('/')
def index():
    """Página inicial com informações sobre a API"""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tor Nodes Feed Server</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
            .status { color: green; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>🧅 Tor Nodes Feed Server</h1>
        <p class="status">Servidor ativo e funcionando!</p>
        
        <h2>Endpoints Disponíveis:</h2>
        
        <div class="endpoint">
            <strong>GET /api/nodes</strong><br>
            Retorna todos os nós Tor em formato JSON
        </div>
        
        <div class="endpoint">
            <strong>GET /api/nodes/running</strong><br>
            Retorna apenas os nós Tor ativos
        </div>
        
        <div class="endpoint">
            <strong>GET /api/nodes/country/&lt;country_code&gt;</strong><br>
            Retorna nós Tor de um país específico (ex: /api/nodes/country/US)
        </div>
        
        <div class="endpoint">
            <strong>GET /api/stats</strong><br>
            Retorna estatísticas dos nós Tor
        </div>
        
        <div class="endpoint">
            <strong>GET /api/feed/rss</strong><br>
            Feed RSS dos nós Tor (formato XML)
        </div>
        
        <h2>Status do Cache:</h2>
        <p>Última atualização: {{ last_updated }}</p>
        <p>Total de nós: {{ total_nodes }}</p>
    </body>
    </html>
    """
    
    last_updated = tor_nodes_cache['last_updated']
    last_updated_str = last_updated.strftime('%Y-%m-%d %H:%M:%S') if last_updated else 'Nunca'
    
    return render_template_string(
        html_template, 
        last_updated=last_updated_str,
        total_nodes=len(tor_nodes_cache['data'])
    )

@app.route('/api/nodes')
def get_all_nodes():
    """Retorna todos os nós Tor"""
    if fetcher.should_update_cache():
        fetcher.fetch_tor_nodes()
    
    return jsonify({
        'status': 'success',
        'total_nodes': len(tor_nodes_cache['data']),
        'last_updated': tor_nodes_cache['last_updated'].isoformat() if tor_nodes_cache['last_updated'] else None,
        'nodes': tor_nodes_cache['data']
    })

@app.route('/api/nodes/running')
def get_running_nodes():
    """Retorna apenas os nós Tor ativos"""
    if fetcher.should_update_cache():
        fetcher.fetch_tor_nodes()
    
    running_nodes = [node for node in tor_nodes_cache['data'] if node.get('running', False)]
    
    return jsonify({
        'status': 'success',
        'total_running_nodes': len(running_nodes),
        'last_updated': tor_nodes_cache['last_updated'].isoformat() if tor_nodes_cache['last_updated'] else None,
        'nodes': running_nodes
    })

@app.route('/api/nodes/country/<country_code>')
def get_nodes_by_country(country_code):
    """Retorna nós Tor de um país específico"""
    if fetcher.should_update_cache():
        fetcher.fetch_tor_nodes()
    
    country_nodes = [node for node in tor_nodes_cache['data'] 
                    if node.get('country', '').upper() == country_code.upper()]
    
    return jsonify({
        'status': 'success',
        'country': country_code.upper(),
        'total_nodes': len(country_nodes),
        'last_updated': tor_nodes_cache['last_updated'].isoformat() if tor_nodes_cache['last_updated'] else None,
        'nodes': country_nodes
    })

@app.route('/api/stats')
def get_stats():
    """Retorna estatísticas dos nós Tor"""
    if fetcher.should_update_cache():
        fetcher.fetch_tor_nodes()
    
    nodes = tor_nodes_cache['data']
    
    # estatísticas
    total_nodes = len(nodes)
    running_nodes = len([n for n in nodes if n.get('running', False)])
    countries = {}
    total_bandwidth = 0
    
    for node in nodes:
        country = node.get('country', 'Unknown')
        countries[country] = countries.get(country, 0) + 1
        total_bandwidth += node.get('bandwidth', 0)
    
    return jsonify({
        'status': 'success',
        'statistics': {
            'total_nodes': total_nodes,
            'running_nodes': running_nodes,
            'offline_nodes': total_nodes - running_nodes,
            'total_bandwidth': total_bandwidth,
            'countries_count': len(countries),
            'top_countries': sorted(countries.items(), key=lambda x: x[1], reverse=True)[:10],
            'last_updated': tor_nodes_cache['last_updated'].isoformat() if tor_nodes_cache['last_updated'] else None
        }
    })

@app.route('/api/feed/rss')
def get_rss_feed():
    """Retorna feed RSS dos nós Tor"""
    if fetcher.should_update_cache():
        fetcher.fetch_tor_nodes()
    
    # Gera RSS
    rss_template = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Tor Nodes Feed</title>
        <description>Feed dos nós Tor ativos</description>
        <link>http://localhost:5000</link>
        <lastBuildDate>{{ last_updated }}</lastBuildDate>
        {% for node in nodes[:20] %}
        <item>
            <title>{{ node.nickname }} ({{ node.country }})</title>
            <description>Nó Tor: {{ node.fingerprint[:16] }}... | Bandwidth: {{ node.bandwidth }} | Status: {{ 'Ativo' if node.running else 'Inativo' }}</description>
            <guid>{{ node.fingerprint }}</guid>
            <pubDate>{{ last_updated }}</pubDate>
        </item>
        {% endfor %}
    </channel>
</rss>"""
    
    from flask import Response
    
    last_updated = tor_nodes_cache['last_updated']
    last_updated_str = last_updated.strftime('%a, %d %b %Y %H:%M:%S GMT') if last_updated else ''
    
    rss_content = rss_template.replace('{{ last_updated }}', last_updated_str)
    
    # Adiciona itens dos nós
    items = ""
    for node in tor_nodes_cache['data'][:20]:  # first 20 nós
        item = f"""
        <item>
            <title>{node.get('nickname', 'Unknown')} ({node.get('country', 'Unknown')})</title>
            <description>Nó Tor: {node.get('fingerprint', '')[:16]}... | Bandwidth: {node.get('bandwidth', 0)} | Status: {'Ativo' if node.get('running', False) else 'Inativo'}</description>
            <guid>{node.get('fingerprint', '')}</guid>
            <pubDate>{last_updated_str}</pubDate>
        </item>"""
        items += item
    
    final_rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Tor Nodes Feed</title>
        <description>Feed dos nós Tor ativos</description>
        <link>http://localhost:5000</link>
        <lastBuildDate>{last_updated_str}</lastBuildDate>
        {items}
    </channel>
</rss>"""
    
    return Response(final_rss, mimetype='application/rss+xml')

if __name__ == '__main__':
    print("🧅 Iniciando Tor Nodes Feed Server...")
    print("📡 Buscando dados iniciais dos nós Tor...")
    
    fetcher.fetch_tor_nodes()
    
    print("🚀 Servidor iniciado em http://localhost:5000")
    print("📊 Endpoints disponíveis:")
    print("   - GET / (página inicial)")
    print("   - GET /api/nodes (todos os nós)")
    print("   - GET /api/nodes/running (nós ativos)")
    print("   - GET /api/nodes/country/<code> (nós por país)")
    print("   - GET /api/stats (estatísticas)")
    print("   - GET /api/feed/rss (feed RSS)")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
