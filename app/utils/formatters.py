"""Funções de formatação de dados.

Os feeds em texto nunca expõem detalhes internos de erro (stack traces,
mensagens de conexão de banco, etc.) ao cliente. Em caso de indisponibilidade,
retornam um cabeçalho limpo com uma mensagem neutra e ``END 0 entries``.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional

SERVICE_URL = "https://cti.segark.com"
SERVICE_CONTACT = "contato@segark.com"


def _now_utc() -> str:
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')


def format_exit_nodes_text(
    ips: List[str],
    last_update: Optional[datetime],
    unavailable: bool = False,
) -> str:
    """Formata a lista de IPs dos nós Tor exit em texto plano."""

    updated = last_update.strftime('%Y-%m-%d %H:%M:%S') if last_update else _now_utc()

    header = (
        "################################################################\n"
        "# CTI Protexion by Segark - Tor Exit Nodes (IPs only)\n"
        f"# Last updated: {updated} UTC\n"
        "# Source: https://check.torproject.org/exit-addresses\n"
        f"# Service: {SERVICE_URL} | {SERVICE_CONTACT}\n"
        "################################################################\n"
        "#\n"
    )

    if unavailable:
        return (
            header
            + "# Feed temporariamente indisponivel. Tente novamente em alguns minutos.\n"
            + "#\n# END 0 entries\n"
        )

    if not ips:
        return header + "# DstIP\n#\n# END 0 entries\n"

    return header + "# DstIP\n" + "\n".join(ips) + f"\n# END {len(ips)} entries\n"


def format_url_list_text(
    urls: List[str],
    last_update: Optional[datetime],
    unavailable: bool = False,
) -> str:
    """Formata a lista de URLs maliciosas do honeypot em texto plano."""

    updated = last_update.strftime('%Y-%m-%d %H:%M:%S') if last_update else _now_utc()

    header = (
        "################################################################\n"
        "# CTI Protexion by Segark - Honeypot URLs\n"
        f"# Last updated: {updated} UTC\n"
        "# Source: Honeypot (Cowrie)\n"
        f"# Service: {SERVICE_URL} | {SERVICE_CONTACT}\n"
        "################################################################\n"
        "#\n"
    )

    if unavailable:
        return (
            header
            + "# Feed temporariamente indisponivel. Tente novamente em alguns minutos.\n"
            + "#\n# END 0 entries\n"
        )

    if not urls:
        return (
            header
            + "# URL\n"
            + "# Nenhuma URL maliciosa registrada nos ultimos 30 dias.\n"
            + "#\n# END 0 entries\n"
        )

    return header + "# URL\n" + "\n".join(urls) + f"\n# END {len(urls)} entries\n"


def format_rss_feed(nodes: List[Dict[str, Any]], last_update: Optional[datetime]) -> str:
    """Formata o feed RSS dos nós Tor."""

    last_updated_str = last_update.strftime('%a, %d %b %Y %H:%M:%S GMT') if last_update else ''

    items = ""
    for node in nodes:
        status = 'Ativo' if node.get('running', False) else 'Inativo'
        exit_status = ' (Exit Node)' if node.get('exit_node', False) else ''

        item = f"""
        <item>
            <title>{node.get('nickname', 'Unknown')} ({node.get('country', 'Unknown')}){exit_status}</title>
            <description>No Tor: {node.get('fingerprint', '')[:16]}... | Bandwidth: {node.get('bandwidth', 0)} | Status: {status}</description>
            <guid>{node.get('fingerprint', '')}</guid>
            <pubDate>{last_updated_str}</pubDate>
        </item>"""
        items += item

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>CTI Protexion by Segark - Tor Nodes Feed</title>
        <description>Feed dos nos Tor ativos - CTI Protexion by Segark</description>
        <link>{SERVICE_URL}</link>
        <lastBuildDate>{last_updated_str}</lastBuildDate>
        {items}
    </channel>
</rss>"""
