import os
import time
from datetime import datetime, timedelta
from flask import Flask, render_template_string, Response
import requests

CACHE_FILE = '/tmp/tor_exit_cache.txt'
CACHE_TIMESTAMP = '/tmp/tor_exit_timestamp.txt'
CACHE_TTL_HOUR = 12

app = Flask(__name__)

HEADER = """################################################################
# TOR NODE  (IPs only)                                         #
# Last updated: {updated} UTC                                 #
# Source: https://check.torproject.org/exit-addresses          #
#                                                              #
# Social media: https://www.linkedin.com/in/dathannobrega/     #
# For questions please contact contato@datan.com.br            #
################################################################
#
# DstIP
"""

TEMPLATE = HEADER + """{ips}
# END {count} entries
"""

def needs_update() -> bool:
    if not os.path.exists(CACHE_FILE) or not os.path.exists(CACHE_TIMESTAMP):
        return True
    with open(CACHE_TIMESTAMP, 'r') as f:
        ts = float(f.read().strip())
    last = datetime.utcfromtimestamp(ts)
    return datetime.utcnow() - last > timedelta(hours=CACHE_TTL_HOUR)

def update_cache():
    print(f"[{datetime.utcnow()}] Atualizando cache dos nós Tor...")
    try:
        url = 'https://check.torproject.org/exit-addresses'
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        
        ips = []
        ips_with_timestamp = []
        
        for line in resp.text.splitlines():
            if line.startswith('ExitAddress'):
                parts = line.split()
                if len(parts) >= 3:
                    ip = parts[1]
                    timestamp = ' '.join(parts[2:])  # YYYY-MM-DD HH:MM:SS
                    ips.append(ip)
                    ips_with_timestamp.append(f"{ip} # Last seen: {timestamp}")
        
        # grava cache apenas com IPs (formato original)
        with open(CACHE_FILE, 'w') as f:
            f.write('\n'.join(ips))
        
        # grava cache com timestamps para uso futuro
        with open('/tmp/tor_exit_cache_detailed.txt', 'w') as f:
            f.write('\n'.join(ips_with_timestamp))
            
        with open(CACHE_TIMESTAMP, 'w') as f:
            f.write(str(time.time()))
        
        print(f"[{datetime.utcnow()}] Cache atualizado com {len(ips)} IPs")
        print(f"[{datetime.utcnow()}] Fonte: Tor Project Official - {url}")
        
    except Exception as e:
        print(f"[{datetime.utcnow()}] Erro ao atualizar cache: {e}")
        raise

def load_ips():
    if needs_update():
        update_cache()
    with open(CACHE_FILE, 'r') as f:
        return [l.strip() for l in f if l.strip()]

@app.route('/')
def index():
    """Página inicial com informações completas sobre o projeto"""
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Protexion TOR Nodes - Monitoramento de Nós Tor</title>
        <meta name="description" content="Serviço de monitoramento e listagem de nós Tor exit em tempo real">
        <meta name="keywords" content="tor, nodes, exit, ip, security, privacy, monitoring">
        <meta name="author" content="Dathan Nobrega">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Courier New', monospace;
                background: linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 100%);
                color: #00ff00;
                line-height: 1.6;
                min-height: 100vh;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .header {
                text-align: center;
                padding: 40px 0;
                border-bottom: 2px solid #00ff00;
                margin-bottom: 40px;
                background: rgba(0, 255, 0, 0.05);
                border-radius: 10px;
            }
            
            .ascii-art {
                font-size: 10px;
                color: #00ff00;
                margin: 20px 0;
                white-space: pre;
                overflow-x: auto;
            }
            
            .main-title {
                font-size: 2.5em;
                margin: 20px 0;
                text-shadow: 0 0 10px #00ff00;
            }
            
            .subtitle {
                font-size: 1.2em;
                color: #00ffff;
                margin-bottom: 10px;
            }
            
            .domain-info {
                background: rgba(0, 255, 255, 0.1);
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                border-left: 4px solid #00ffff;
            }
            
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 30px;
                margin: 40px 0;
            }
            
            .card {
                background: rgba(0, 0, 0, 0.8);
                border: 2px solid #00ff00;
                border-radius: 10px;
                padding: 25px;
                transition: all 0.3s ease;
            }
            
            .card:hover {
                border-color: #00ffff;
                box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
                transform: translateY(-5px);
            }
            
            .card h3 {
                color: #00ffff;
                margin-bottom: 15px;
                font-size: 1.4em;
                border-bottom: 1px solid #333;
                padding-bottom: 10px;
            }
            
            .endpoint {
                background: rgba(0, 255, 0, 0.1);
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #00ff00;
                border-radius: 5px;
            }
            
            .social-links {
                display: flex;
                justify-content: center;
                gap: 20px;
                margin: 30px 0;
                flex-wrap: wrap;
            }
            
            .social-link {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 12px 20px;
                background: rgba(0, 255, 0, 0.1);
                border: 1px solid #00ff00;
                border-radius: 25px;
                color: #00ff00;
                text-decoration: none;
                transition: all 0.3s ease;
                font-weight: bold;
            }
            
            .social-link:hover {
                background: rgba(0, 255, 255, 0.2);
                border-color: #00ffff;
                color: #00ffff;
                transform: scale(1.05);
            }
            
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            
            .stat-item {
                text-align: center;
                padding: 20px;
                background: rgba(0, 255, 0, 0.05);
                border-radius: 10px;
                border: 1px solid #333;
            }
            
            .stat-number {
                font-size: 2em;
                color: #00ffff;
                font-weight: bold;
            }
            
            .stat-label {
                color: #00ff00;
                margin-top: 5px;
            }
            
            .footer {
                text-align: center;
                margin-top: 50px;
                padding: 30px 0;
                border-top: 2px solid #00ff00;
                background: rgba(0, 255, 0, 0.05);
                border-radius: 10px;
            }
            
            .tech-stack {
                display: flex;
                justify-content: center;
                gap: 15px;
                margin: 20px 0;
                flex-wrap: wrap;
            }
            
            .tech-item {
                padding: 8px 15px;
                background: rgba(0, 255, 255, 0.1);
                border: 1px solid #00ffff;
                border-radius: 15px;
                font-size: 0.9em;
                color: #00ffff;
            }
            
            a {
                color: #00ffff;
                text-decoration: none;
            }
            
            a:hover {
                text-decoration: underline;
                color: #ffffff;
            }
            
            .status-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                background: #00ff00;
                border-radius: 50%;
                margin-right: 8px;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
            
            @media (max-width: 768px) {
                .main-title {
                    font-size: 1.8em;
                }
                
                .ascii-art {
                    font-size: 8px;
                }
                
                .grid {
                    grid-template-columns: 1fr;
                }
                
                .social-links {
                    flex-direction: column;
                    align-items: center;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="ascii-art">
████████╗ ██████╗ ██████╗     ███╗   ██╗ ██████╗ ██████╗ ███████╗███████╗
╚══██╔══╝██╔═══██╗██╔══██╗    ████╗  ██║██╔═══██╗██╔══██╗██╔════╝██╔════╝
   ██║   ██║   ██║██████╔╝    ██╔██╗ ██║██║   ██║██║  ██║█████╗  ███████╗
   ██║   ██║   ██║██╔══██╗    ██║╚██╗██║██║   ██║██║  ██║██╔══╝  ╚════██║
   ██║   ╚██████╔╝██║  ██║    ██║ ╚████║╚██████╔╝██████╔╝███████╗███████║
   ╚═╝    ╚═════╝ ╚═╝  ╚═╝    ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚══════╝╚══════╝
                </div>
                
                <h1 class="main-title">🧅 Protexion TorNodes</h1>
                <p class="subtitle">Monitoramento em Tempo Real de Nós Tor Exit</p>
                
                <div class="domain-info">
                    <strong>🌐 Hospedado em:</strong> <a href="https://tor.protexion.cloud" target="_blank">tor.protexion.cloud</a>
                </div>
                
                <p><span class="status-indicator"></span><strong>Status:</strong> Online e Funcionando</p>
            </div>
            
            <div class="grid">
                <div class="card">
                    <h3>📋 Sobre o Projeto</h3>
                    <p>O <strong>Protexion TorNodes</strong> é um serviço de monitoramento que fornece uma lista atualizada dos endereços IP dos nós Tor exit em tempo real.</p>
                    <br>
                    <p>Este projeto foi desenvolvido para auxiliar administradores de sistema, pesquisadores de segurança e profissionais de TI que precisam identificar e monitorar o tráfego proveniente da rede Tor.</p>
                    <br>
                    </ul>
                </div>
                
                <div class="card">
                    <h3>🔗 Endpoints da API</h3>
                    
                    <div class="endpoint">
                        <strong>GET <a href="/tornodes-ip.txt">/tornodes-ip.txt</a></strong><br>
                        <small>Lista completa de IPs dos nós Tor exit em formato texto</small>
                    </div>
                    
                    <div class="endpoint">
                        <strong>GET <a href="/status">/status</a></strong><br>
                        <small>Status do serviço e informações do cache em JSON</small>
                    </div>
                    
                    <p style="margin-top: 15px;"><strong>Exemplo de uso:</strong></p>
                    <code style="background: rgba(0,0,0,0.5); padding: 10px; display: block; margin-top: 10px; border-radius: 5px;">
curl https://tor.protexion.cloud/tornodes-ip.txt
                    </code>
                </div>
                
                <div class="card">
                    <h3>⚙️ Especificações Técnicas</h3>
                    
                    <div class="tech-stack">
                        <span class="tech-item">Python 3.x</span>
                        <span class="tech-item">Flask</span>
                        <span class="tech-item">Requests</span>
                        <span class="tech-item">Gunicorn</span>
                    </div>
                    
                    <p><strong>📊 Fonte dos Dados:</strong><br>
                    <a href="https://check.torproject.org/exit-addresses" target="_blank">Tor Project Official API</a></p>
                    
                    <p><strong>🔄 Frequência de Atualização:</strong><br>
                    Cache renovado automaticamente a cada 12 horas</p>
                    
                    <p><strong>📈 Performance:</strong><br>
                    Resposta em milissegundos com sistema de cache otimizado</p>
                </div>
                
                <div class="card">
                    <h3>👨‍💻 Sobre o Desenvolvedor</h3>
                    <p><strong>Dathan Nobrega</strong></p>
                    <p>Especialista em Segurança da Informação</p>
                    
                    <div class="social-links">
                        <a href="https://github.com/dathannobrega" target="_blank" class="social-link">
                            <span>🐙</span> GitHub
                        </a>
                        <a href="https://www.linkedin.com/in/dathannobrega/" target="_blank" class="social-link">
                            <span>💼</span> LinkedIn
                        </a>
                        <a href="mailto:dathan.nobrega@datan.com.br" class="social-link">
                            <span>📧</span> Email
                        </a>
                    </div>
                </div>
            </div>
            
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-number">24/7</div>
                    <div class="stat-label">Monitoramento</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">12</div>
                    <div class="stat-label">Horas de Cache</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">99.9%</div>
                    <div class="stat-label">Uptime</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">API</div>
                    <div class="stat-label">RESTful</div>
                </div>
            </div>
            
            <div class="footer">
                <h3>🚀 Como Usar</h3>
                <p>Integre facilmente em seus sistemas de segurança, firewalls, ou ferramentas de monitoramento:</p>
                <br>
                
                <div style="text-align: left; max-width: 600px; margin: 0 auto;">
                    <p><strong>Bash/Shell:</strong></p>
                    <code style="background: rgba(0,0,0,0.7); padding: 15px; display: block; margin: 10px 0; border-radius: 5px;">
curl -s https://tor.protexion.cloud/tornodes-ip.txt | grep -v "^#"
                    </code>
                    
                    <p><strong>Python:</strong></p>
                    <code style="background: rgba(0,0,0,0.7); padding: 15px; display: block; margin: 10px 0; border-radius: 5px;">
import requests
response = requests.get('https://tor.protexion.cloud/tornodes-ip.txt')
ips = [line for line in response.text.split('\\n') if not line.startswith('#')]
                    </code>
                </div>
                
                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #333;">
                    <p>🛡️ <strong>Protexion TorNodes Service</strong> - Desenvolvido por <strong>Dathan Nobrega</strong></p>
                    <p>🌐 Hospedado em <a href="https://tor.protexion.cloud" target="_blank">tor.protexion.cloud</a></p>
                    <p style="margin-top: 15px; color: #666;">
                        © 2024 DataN. Este serviço é fornecido "como está" para fins educacionais e de pesquisa.
                    </p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

@app.route('/tornodes-ip.txt')
def tornodes_ip():
    """Endpoint principal que retorna os IPs dos nós Tor em formato texto"""
    try:
        ips = load_ips()
        
        # Carrega timestamp do cache
        if os.path.exists(CACHE_TIMESTAMP):
            with open(CACHE_TIMESTAMP, 'r') as f:
                timestamp = float(f.read().strip())
            updated = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        else:
            updated = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        # Gera o conteúdo formatado
        content = TEMPLATE.format(
            updated=updated,
            ips='\n'.join(ips),
            count=len(ips)
        )
        
        # Retorna como texto plano
        return Response(content, mimetype='text/plain')
        
    except Exception as e:
        error_content = f"""################################################################
# DataN TOR NODE  (IPs only) - ERRO                           #
# Error occurred: {str(e)}                                    #
# Last attempt: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC                     #
#                                                              #
# Social media: https://www.linkedin.com/in/dathannobrega/     #
# For questions please contact contato@datan.com.br            #
################################################################
#
# Erro ao carregar dados dos nós Tor
# Tente novamente em alguns minutos
#
# END 0 entries
"""
        return Response(error_content, mimetype='text/plain', status=500)

@app.route('/status')
def status():
    """Endpoint de status do serviço"""
    try:
        cache_exists = os.path.exists(CACHE_FILE)
        timestamp_exists = os.path.exists(CACHE_TIMESTAMP)
        
        if timestamp_exists:
            with open(CACHE_TIMESTAMP, 'r') as f:
                timestamp = float(f.read().strip())
            last_update = datetime.utcfromtimestamp(timestamp)
            needs_update_flag = needs_update()
        else:
            last_update = None
            needs_update_flag = True
        
        if cache_exists:
            with open(CACHE_FILE, 'r') as f:
                ip_count = len([l for l in f if l.strip()])
        else:
            ip_count = 0
        
        status_info = {
            'service': 'Protexion TorNodes',
            'status': 'online',
            'cache_exists': cache_exists,
            'timestamp_exists': timestamp_exists,
            'last_update': last_update.isoformat() if last_update else None,
            'needs_update': needs_update_flag,
            'ip_count': ip_count,
            'cache_ttl_days': CACHE_TTL_DAYS,
            'current_time': datetime.utcnow().isoformat()
        }
        
        from flask import jsonify
        return jsonify(status_info)
        
    except Exception as e:
        from flask import jsonify
        return jsonify({
            'service': 'Protexion TorNodes',
            'status': 'error',
            'error': str(e),
            'current_time': datetime.utcnow().isoformat()
        }), 500

if __name__ == '__main__':
    print("🧅 Iniciando Protexion TorNodes Service...")
    print("📡 Verificando cache inicial...")
    
    try:
        # Verifica se precisa atualizar o cache na inicialização
        if needs_update():
            print("🔄 Cache desatualizado, buscando dados...")
            update_cache()
        else:
            print("✅ Cache válido encontrado")
            
        ips = load_ips()
        print(f"📊 {len(ips)} IPs carregados no cache")
        
    except Exception as e:
        print(f"⚠️ Erro na inicialização: {e}")
        print("🚀 Servidor será iniciado mesmo assim...")
    
    print("🚀 Servidor iniciado em http://localhost:8000")
    print("📋 Endpoints disponíveis:")
    print("   - GET / (página inicial)")
    print("   - GET /tornodes-ip.txt (lista de IPs)")
    print("   - GET /status (status do serviço)")
    
    app.run(host='0.0.0.0', port=8000, debug=True)
