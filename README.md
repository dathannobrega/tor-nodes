# 🧅 Protexion TOR Nodes

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Online-brightgreen.svg)](https://tor.protexion.cloud)

> **Serviço de monitoramento em tempo real de nós Tor exit**

Um serviço web Python que fornece uma lista atualizada dos endereços IP dos nós Tor exit, obtidos diretamente da fonte oficial do Tor Project.

🌐 **Acesse o serviço:** [tor.protexion.cloud](https://tor.protexion.cloud)

## 📋 Índice

- [Características](#-características)
- [Instalação](#-instalação)
- [Uso](#-uso)
- [Endpoints da API](#-endpoints-da-api)
- [Exemplos](#-exemplos)
- [Configuração](#-configuração)
- [Contribuição](#-contribuição)
- [Licença](#-licença)
- [Contato](#-contato)

## ✨ Características

- 🔄 **Atualização Automática**: Cache renovado a cada 10 dias
- 📊 **Fonte Oficial**: Dados obtidos diretamente do Tor Project
- ⚡ **Performance**: Sistema de cache otimizado para respostas rápidas
- 🛡️ **Confiabilidade**: Monitoramento 24/7 com tratamento robusto de erros
- 📱 **API RESTful**: Interface simples e padronizada
- 🎨 **Interface Web**: Página inicial informativa e profissional

## 🚀 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Instalação Local

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/dathannobrega/tor-nodes.git
   cd tor-nodes/app
   ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute o servidor:**
   ```bash
   python main.py
   ```

4. **Acesse o serviço:**
   - Interface web: http://localhost:8000
   - Lista de IPs: http://localhost:8000/tornodes-ip.txt

### Instalação com Docker

```bash
# Build da imagem
docker build -t tor-nodes .

# Executar container
docker run -p 8000:8000 tor-nodes
```

### Produção com Gunicorn

```bash
gunicorn --bind 0.0.0.0:8000 --workers 4 main:app
```

## 📖 Uso

### Acesso Rápido

O serviço fornece uma lista de IPs dos nós Tor exit em formato texto simples:

```bash
curl https://tor.protexion.cloud/tornodes-ip.txt
```

### Integração em Scripts

```bash
# Baixar apenas os IPs (sem comentários)
curl -s https://tor.protexion.cloud/tornodes-ip.txt | grep -v "^#"

# Salvar em arquivo
curl -s https://tor.protexion.cloud/tornodes-ip.txt > tor_nodes.txt
```

## 🔗 Endpoints da API

### GET `/`
**Descrição:** Página inicial com documentação completa  
**Formato:** HTML  
**Exemplo:** [tor.protexion.cloud](https://tor.protexion.cloud)

### GET `/tornodes-ip.txt`
**Descrição:** Lista completa de IPs dos nós Tor exit  
**Formato:** Texto plano  
**Cache:** 10 dias  
**Exemplo:**
```
################################################################
# DataN TOR NODE  (IPs only)                                   #
# Last updated: 2024-01-15 14:30:25 UTC                      #
# Source: https://check.torproject.org/exit-addresses          #
################################################################
#
# DstIP
192.168.1.1
10.0.0.1
...
# END 1234 entries
```

### GET `/status`
**Descrição:** Status do serviço e informações do cache  
**Formato:** JSON  
**Exemplo de resposta:**
```json
{
  "service": "DataN TOR Nodes",
  "status": "online",
  "cache_exists": true,
  "last_update": "2024-01-15T14:30:25.123456",
  "ip_count": 1234,
  "cache_ttl_days": 10,
  "current_time": "2024-01-15T15:45:30.789012"
}
```

## 💡 Exemplos

### Python

```python
import requests

# Obter lista de IPs
response = requests.get('https://tor.protexion.cloud/tornodes-ip.txt')
ips = [line.strip() for line in response.text.split('\\n') 
       if line.strip() and not line.startswith('#')]

print(f"Total de nós Tor: {len(ips)}")
for ip in ips[:5]:  # Primeiros 5 IPs
    print(ip)
```

### Bash/Shell

```bash
#!/bin/bash

# Baixar e processar lista de nós Tor
curl -s https://tor.protexion.cloud/tornodes-ip.txt | \\
grep -v "^#" | \\
while read ip; do
    echo "Processando IP: $ip"
    # Sua lógica aqui
done
```

### JavaScript/Node.js

```javascript
const fetch = require('node-fetch');

async function getTorNodes() {
    try {
        const response = await fetch('https://tor.protexion.cloud/tornodes-ip.txt');
        const text = await response.text();
        
        const ips = text.split('\\n')
            .filter(line => line.trim() && !line.startsWith('#'));
        
        console.log(`Total de nós Tor: \${ips.length}`);
        return ips;
    } catch (error) {
        console.error('Erro ao obter nós Tor:', error);
    }
}

getTorNodes();
```

### PHP

```php
<?php
$url = 'https://tor.protexion.cloud/tornodes-ip.txt';
$content = file_get_contents($url);

$lines = explode("\\n", $content);
$ips = array_filter($lines, function($line) {
    return !empty(trim($line)) && !str_starts_with(trim($line), '#');
});

echo "Total de nós Tor: " . count($ips) . "\\n";
foreach (array_slice($ips, 0, 5) as $ip) {
    echo "IP: " . trim($ip) . "\\n";
}
?>
```

## ⚙️ Configuração

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|---------|
| `CACHE_TTL_DAYS` | Dias para renovação do cache | 10 |
| `PORT` | Porta do servidor | 8000 |
| `HOST` | Host do servidor | 0.0.0.0 |

### Arquivos de Cache

- `/tmp/tor_exit_cache.txt` - Cache dos IPs
- `/tmp/tor_exit_timestamp.txt` - Timestamp da última atualização
- `/tmp/tor_exit_cache_detailed.txt` - Cache com timestamps detalhados

## 🔧 Desenvolvimento

### Estrutura do Projeto

```
datan-tor-nodes/
├── main.py              # Aplicação principal
├── requirements.txt     # Dependências Python
├── README.md           # Documentação
├── LICENSE             # Licença MIT
└── Dockerfile          # Container Docker
```

### Executar em Modo Debug

```bash
export FLASK_ENV=development
python main.py
```

### Testes

```bash
# Testar endpoint principal
curl -I http://localhost:8000/tornodes-ip.txt

# Testar status
curl http://localhost:8000/status | jq
```

## 📊 Fonte dos Dados

Os dados são obtidos diretamente da fonte oficial do Tor Project:

- **URL:** https://check.torproject.org/exit-addresses
- **Formato:** `ExitAddress <IP> <YYYY-MM-DD HH:MM:SS>`
- **Atualização:** Dados atualizados pelo próprio Tor Project
- **Confiabilidade:** Fonte oficial e autoritativa

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. **Fork** o projeto
2. **Crie** uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. **Abra** um Pull Request

### Diretrizes

- Mantenha o código limpo e bem documentado
- Adicione testes para novas funcionalidades
- Siga as convenções de código Python (PEP 8)
- Atualize a documentação quando necessário

## 📝 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Contato

**Dathan Nobrega**

- 🐙 **GitHub:** [@dathannobrega](https://github.com/dathannobrega)
- 💼 **LinkedIn:** [dathannobrega](https://www.linkedin.com/in/dathannobrega/)
- 📧 **Email:** contato@datan.com.br
- 🌐 **Website:** [tor.protexion.cloud](https://tor.protexion.cloud)

---

## 🙏 Agradecimentos

- [Tor Project](https://www.torproject.org/) pela disponibilização dos dados
- Comunidade Python e Flask pelos excelentes frameworks
- Todos os contribuidores e usuários do projeto

---

<div align="center">

**⭐ Se este projeto foi útil para você, considere dar uma estrela!**

[![GitHub stars](https://img.shields.io/github/stars/dathannobrega/datan-tor-nodes.svg?style=social&label=Star)](https://github.com/dathannobrega/tor-nodes)

</div>
