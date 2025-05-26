"""
Funções de formatação de dados
"""

from datetime import datetime
from typing import List, Dict, Any, Optional


def format_exit_nodes_text(ips: List[str], last_update: Optional[datetime], error: Optional[str] = None) -> str:
    """Formata lista de IPs para formato texto"""
    
    if error:
        return f"""################################################################
# DataN TOR NODE  (IPs only) - ERRO                           #
# Error occurred: {error}                                     #
# Last attempt: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC            #
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
    
    updated = last_update.strftime('%Y-%m-%d %H:%M:%S') if last_update else datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
    header = f"""################################################################
# TOR NODE  (IPs only)                                         #
# Last updated: {updated} UTC                        #
# Source: https://check.torproject.org/exit-addresses          #
#                                                              #
# Social media: https://www.linkedin.com/in/dathannobrega/     #
# For questions please contact contato@datan.com.br            #
################################################################
#
# DstIP
"""
    
    return header + '\n'.join(ips) + f'\n# END {len(ips)} entries\n'


def format_rss_feed(nodes: List[Dict[str, Any]], last_update: Optional[datetime]) -> str:
    """Formata feed RSS dos nós Tor"""
    
    last_updated_str = last_update.strftime('%a, %d %b %Y %H:%M:%S GMT') if last_update else ''
    
    items = ""
    for node in nodes:
        status = 'Ativo' if node.get('running', False) else 'Inativo'
        exit_status = ' (Exit Node)' if node.get('exit_node', False) else ''
        
        item = f"""
        <item>
            <title>{node.get('nickname', 'Unknown')} ({node.get('country', 'Unknown')}){exit_status}</title>
            <description>Nó Tor: {node.get('fingerprint', '')[:16]}... | Bandwidth: {node.get('bandwidth', 0)} | Status: {status}</description>
            <guid>{node.get('fingerprint', '')}</guid>
            <pubDate>{last_updated_str}</pubDate>
        </item>"""
        items += item
    
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Protexion Tor Nodes Feed</title>
        <description>Feed dos nós Tor ativos - Protexion TorNodes</description>
        <link>https://tor.protexion.cloud</link>
        <lastBuildDate>{last_updated_str}</lastBuildDate>
        {items}
    </channel>
</rss>"""
