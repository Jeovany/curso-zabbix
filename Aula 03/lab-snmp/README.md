# 🐳 Laboratório SNMP Docker
## Zabbix Advanced - Aula 03

> Ambiente completo com 7 containers SNMP simulando infraestrutura de rede e servidores

---

## 📦 Conteúdo do Pacote

| Arquivo | Descrição | Tamanho |
|---------|-----------|---------|
| `lab-snmp-image.tar.gz` | Imagem Docker pré-construída | ~4.5 MB |
| `docker-compose.yml` | Configuração dos containers | - |
| `setup.sh` | Script automático para Linux/Mac | - |
| `setup.bat` | Script automático para Windows | - |
| `README.md` | Este arquivo | - |

---

## 🚀 Instalação Rápida

### Linux / macOS

```bash
# 1. Dar permissão de execução
chmod +x setup.sh

# 2. Executar setup
./setup.sh

# 3. Aguardar (~30 segundos)
# Pronto! ✅
```

### Windows

```cmd
# 1. Abrir PowerShell ou CMD nesta pasta
# 2. Executar:
setup.bat

# 3. Aguardar (~30 segundos)
# Pronto! ✅
```

### Manual (Todos os sistemas)

```bash
# 1. Carregar imagem Docker
docker load -i lab-snmp-image.tar.gz

# 2. Iniciar containers
docker compose up -d

# 3. Aguardar 30 segundos para ficarem "healthy"
docker compose ps
```

---

## ✅ Verificação

### Verificar Status dos Containers

```bash
docker compose ps
```

**Esperado:** Todos os 7 containers com status `healthy`

| Container | Porta | Status Esperado |
|-----------|-------|-----------------|
| `snmp-switch-core` | 10161 | ✅ Up (healthy) |
| `snmp-switch-access` | 10162 | ✅ Up (healthy) |
| `snmp-server-web` | 10163 | ✅ Up (healthy) |
| `snmp-server-db` | 10164 | ✅ Up (healthy) |
| `snmp-firewall` | 10165 | ✅ Up (healthy) |
| `snmp-printer` | 10166 | ✅ Up (healthy) |
| `snmp-ups` | 10167 | ✅ Up (healthy) |

### Testar Conectividade SNMP

```bash
# Teste simples
snmpwalk -v2c -c public localhost:10161 system

# Testar todos os containers
for port in {10161..10167}; do
  echo "=== Porta $port ==="
  snmpget -v2c -c public localhost:$port SNMPv2-MIB::sysName.0
done
```

**Resultado esperado:**
```
=== Porta 10161 ===
SNMPv2-MIB::sysName.0 = STRING: switch-core-01
=== Porta 10162 ===
SNMPv2-MIB::sysName.0 = STRING: switch-access-01
...
```

---

## 🔧 Pré-requisitos

### Obrigatórios

- ✅ **Docker** instalado e funcionando
  - **Linux:** `curl -fsSL https://get.docker.com | sh`
  - **Windows/Mac:** [Docker Desktop](https://www.docker.com/products/docker-desktop)

- ✅ **Docker Compose** disponível
  - Já incluído no Docker Desktop
  - **Linux:** `sudo apt-get install docker-compose-plugin`

### Opcional (Recomendado)

- ⚠️ **snmpwalk** para testes manuais
  - **Linux:** `sudo apt-get install snmp snmp-mibs-downloader`
  - **Mac:** `brew install net-snmp`
  - **Windows:** Incluído no WSL ou [baixar aqui](https://sourceforge.net/projects/net-snmp/)

### Verificar Instalação

```bash
# Verificar Docker
docker --version
docker ps

# Verificar Docker Compose
docker compose version

# Verificar snmpwalk (opcional)
snmpwalk -V
```

---

## 📊 Informações dos Containers

### Configuração SNMP

| Parâmetro | Valor |
|-----------|-------|
| **Community** | `public` |
| **Versão SNMP** | v2c |
| **Rede Docker** | 172.25.0.0/16 |

### Dispositivos Disponíveis

| # | Nome | Hostname | IP Interno | Porta Local | Tipo |
|---|------|----------|------------|-------------|------|
| 1 | Switch Core | switch-core-01 | 172.25.0.10 | **10161** | Switch |
| 2 | Switch Access | switch-access-01 | 172.25.0.11 | **10162** | Switch |
| 3 | Web Server | web-server-01 | 172.25.0.20 | **10163** | Servidor |
| 4 | Database Server | db-server-01 | 172.25.0.21 | **10164** | Servidor |
| 5 | Firewall | firewall-01 | 172.25.0.5 | **10165** | Firewall |
| 6 | Printer | printer-01 | 172.25.0.30 | **10166** | Impressora |
| 7 | UPS | ups-01 | 172.25.0.31 | **10167** | No-break |

### Diagrama de Rede

```
                    172.25.0.0/16
                          │
         ┌────────────────┼────────────────┐
         │                │                │
    172.25.0.5       172.25.0.10      172.25.0.11
   ┌──────────┐     ┌──────────┐     ┌──────────┐
   │ Firewall │     │  Switch  │────►│  Switch  │
   │   (5)    │     │  Core (1)│     │ Access(2)│
   └──────────┘     └──────────┘     └──────────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
               172.25.0.20            172.25.0.21            172.25.0.30
              ┌──────────┐           ┌──────────┐           ┌──────────┐
              │   Web    │           │ Database │           │ Printer  │
              │ Server(3)│           │ Server(4)│           │   (6)    │
              └──────────┘           └──────────┘           └──────────┘

                                                            172.25.0.31
                                                           ┌──────────┐
                                                           │   UPS    │
                                                           │   (7)    │
                                                           └──────────┘
```

---

## 💡 Comandos Úteis

### Gerenciamento dos Containers

```bash
# Ver status dos containers
docker compose ps

# Ver logs de todos containers
docker compose logs

# Ver logs de um container específico
docker compose logs snmp-switch-core
docker compose logs -f snmp-printer  # -f para follow (tempo real)

# Parar todos containers
docker compose down

# Reiniciar todos containers
docker compose restart

# Reiniciar um container específico
docker compose restart snmp-switch-core

# Iniciar novamente (depois de parar)
docker compose up -d

# Reconstruir e iniciar (após mudanças)
docker compose up -d --build

# Remover tudo (containers + rede)
docker compose down -v
docker rmi lab-snmp:1.0
```

### Acesso aos Containers

```bash
# Entrar em um container (shell)
docker exec -it snmp-switch-core sh

# Executar comando específico
docker exec snmp-switch-core ps aux
docker exec snmp-switch-core cat /etc/snmp/snmpd.conf

# Ver processos em execução
docker exec snmp-switch-core ps -ef | grep snmpd
```

---

## 🧪 Testes e Laboratórios

### Teste 1: Conectividade Básica

```bash
# Testar todos os containers de uma vez
for port in {10161..10167}; do
  echo "=== Testando porta $port ==="
  snmpget -v2c -c public localhost:$port SNMPv2-MIB::sysName.0
done
```

### Teste 2: System Group (MIB-II)

```bash
# Informações completas do sistema
snmpwalk -v2c -c public localhost:10161 system

# OIDs específicos
snmpget -v2c -c public localhost:10161 \
  SNMPv2-MIB::sysDescr.0 \
  SNMPv2-MIB::sysUpTime.0 \
  SNMPv2-MIB::sysContact.0 \
  SNMPv2-MIB::sysName.0 \
  SNMPv2-MIB::sysLocation.0
```

### Teste 3: Interfaces

```bash
# Listar todas interfaces
snmpwalk -v2c -c public localhost:10161 IF-MIB::ifDescr

# Status operacional das interfaces
snmpwalk -v2c -c public localhost:10161 IF-MIB::ifOperStatus

# Estatísticas de tráfego
snmpwalk -v2c -c public localhost:10161 IF-MIB::ifInOctets
snmpwalk -v2c -c public localhost:10161 IF-MIB::ifOutOctets
```

### Teste 4: Comparação GET vs GET-BULK

```bash
# Método tradicional (GET-NEXT)
echo "=== SNMPWALK (GET-NEXT) ==="
time snmpwalk -v2c -c public localhost:10161 1.3.6.1.2.1.2.2.1 > /dev/null

# Método otimizado (GET-BULK) - até 70% mais rápido!
echo "=== SNMPBULKWALK (GET-BULK) ==="
time snmpbulkwalk -v2c -c public localhost:10161 1.3.6.1.2.1.2.2.1 > /dev/null
```

### Teste 5: OIDs Numéricos vs Nomes

```bash
# Usando nome da MIB
snmpwalk -v2c -c public localhost:10161 IF-MIB::ifDescr

# Usando OID numérico (mesmo resultado!)
snmpwalk -v2c -c public localhost:10161 1.3.6.1.2.1.2.2.1.2

# Traduzir entre nome e número
snmptranslate -On IF-MIB::ifDescr
snmptranslate .1.3.6.1.2.1.2.2.1.2
```

### Teste 6: Monitorar em Tempo Real

```bash
# Monitorar mudanças no uptime
watch -n 1 'snmpget -v2c -c public localhost:10161 SNMPv2-MIB::sysUpTime.0'

# Monitorar tráfego de interface
watch -n 1 'snmpwalk -v2c -c public localhost:10161 IF-MIB::ifInOctets'
```

---

## 🔗 Integração com Zabbix

### Adicionar Hosts no Zabbix

**Configuration → Hosts → Create host**

#### Exemplo: Switch Core

| Campo | Valor |
|-------|-------|
| **Host name** | Switch-Core-Lab |
| **Visible name** | Switch Core (Laboratório) |
| **Groups** | Network devices, Lab |
| **Interface** | SNMP |
| **IP address** | 127.0.0.1 |
| **Port** | 10161 |
| **SNMP version** | SNMPv2 |
| **SNMP community** | public |

**Templates:** `Linux by SNMP` ou `Generic by SNMP`

### Configuração Rápida (Todos os Hosts)

| Host | IP | Porta | Template Sugerido |
|------|-----|-------|-------------------|
| Switch-Core-Lab | 127.0.0.1 | 10161 | Linux by SNMP |
| Switch-Access-Lab | 127.0.0.1 | 10162 | Linux by SNMP |
| WebServer-Lab | 127.0.0.1 | 10163 | Linux by SNMP |
| DBServer-Lab | 127.0.0.1 | 10164 | Linux by SNMP |
| Firewall-Lab | 127.0.0.1 | 10165 | Linux by SNMP |
| Printer-Lab | 127.0.0.1 | 10166 | Printer Generic by SNMP |
| UPS-Lab | 127.0.0.1 | 10167 | UPS Generic by SNMP |

### Criar Item SNMP Customizado

**Configuration → Hosts → [Host] → Items → Create item**

```
Name: System Uptime
Type: SNMP agent
Key: system.uptime
SNMP OID: 1.3.6.1.2.1.1.3.0
  (ou: SNMPv2-MIB::sysUpTime.0)
Type of information: Numeric (unsigned)
Units: uptime
Update interval: 60s
```

---

## ❓ Troubleshooting

### Problema: "Cannot connect to Docker daemon"

**Sintoma:** Erro ao executar comandos Docker

**Solução:**
```bash
# Verificar se Docker está rodando
sudo systemctl status docker

# Iniciar Docker (Linux)
sudo systemctl start docker

# Windows/Mac: Abrir Docker Desktop
```

---

### Problema: "port is already allocated"

**Sintoma:** Erro ao iniciar containers - porta em uso

**Diagnóstico:**
```bash
# Ver o que está usando a porta
sudo lsof -i :10161
sudo netstat -tulpn | grep 10161
```

**Solução 1:** Parar o processo que está usando a porta
```bash
# Encontrar PID e matar
sudo kill <PID>
```

**Solução 2:** Mudar porta no docker-compose.yml
```yaml
ports:
  - "20161:161/udp"  # Usar porta 20161 ao invés de 10161
```

---

### Problema: "network already exists"

**Sintoma:** Erro ao criar rede Docker

**Solução:**
```bash
# Parar containers
docker compose down

# Limpar redes não utilizadas
docker network prune -f

# Iniciar novamente
docker compose up -d
```

---

### Problema: Containers reiniciando constantemente

**Sintoma:** Status "Restarting" no `docker compose ps`

**Diagnóstico:**
```bash
# Ver logs do container problemático
docker compose logs snmp-switch-core

# Ver últimas 20 linhas
docker compose logs --tail=20 snmp-switch-core
```

**Soluções comuns:**
- Aguardar 1 minuto (pode estar inicializando)
- Verificar RAM disponível: `free -h` (mínimo 500MB)
- Verificar se imagem foi carregada: `docker images | grep lab-snmp`
- Recriar containers: `docker compose down && docker compose up -d`

---

### Problema: SNMP não responde (Timeout)

**Sintoma:** `snmpwalk` não retorna dados

**Diagnóstico:**
```bash
# Verificar se container está rodando
docker compose ps | grep snmp-switch-core

# Verificar se porta está aberta
nc -vuz localhost 10161

# Ver logs SNMP
docker compose logs snmp-switch-core | grep -i error
```

**Soluções:**
```bash
# 1. Reiniciar container específico
docker compose restart snmp-switch-core

# 2. Verificar configuração SNMP dentro do container
docker exec snmp-switch-core cat /etc/snmp/snmpd.conf

# 3. Testar SNMP localmente no container
docker exec snmp-switch-core snmpget -v2c -c public localhost 1.3.6.1.2.1.1.1.0
```

---

### Problema: "snmpwalk: command not found"

**Sintoma:** Comandos SNMP não funcionam

**Solução - Linux (Debian/Ubuntu):**
```bash
sudo apt-get update
sudo apt-get install snmp snmp-mibs-downloader -y

# Habilitar MIBs
sudo sed -i 's/^mibs :/#mibs :/g' /etc/snmp/snmp.conf
```

**Solução - macOS:**
```bash
brew install net-snmp
```

**Solução - Windows:**
- Instalar WSL2 e seguir passos Linux
- OU baixar Net-SNMP: https://sourceforge.net/projects/net-snmp/

---

### Problema: Imagem não carrega

**Sintoma:** Erro ao executar `docker load`

**Diagnóstico:**
```bash
# Verificar integridade do arquivo
ls -lh lab-snmp-image.tar.gz
file lab-snmp-image.tar.gz
```

**Solução:**
```bash
# Re-descompactar se necessário
gunzip lab-snmp-image.tar.gz

# Carregar imagem descompactada
docker load -i lab-snmp-image.tar

# Verificar se foi carregada
docker images | grep lab-snmp
```

---

## 📚 Referências Úteis

### OIDs Essenciais

#### System Group (1.3.6.1.2.1.1)

| OID | Nome | Descrição |
|-----|------|-----------|
| .1.3.6.1.2.1.1.1.0 | sysDescr | Descrição do sistema |
| .1.3.6.1.2.1.1.3.0 | sysUpTime | Tempo de atividade |
| .1.3.6.1.2.1.1.4.0 | sysContact | Contato administrativo |
| .1.3.6.1.2.1.1.5.0 | sysName | Nome do host |
| .1.3.6.1.2.1.1.6.0 | sysLocation | Localização física |

#### Interfaces (1.3.6.1.2.1.2.2.1)

| OID | Nome | Descrição |
|-----|------|-----------|
| .1.3.6.1.2.1.2.2.1.2.X | ifDescr | Descrição da interface X |
| .1.3.6.1.2.1.2.2.1.8.X | ifOperStatus | Status operacional (1=up, 2=down) |
| .1.3.6.1.2.1.2.2.1.10.X | ifInOctets | Bytes recebidos (32-bit) |
| .1.3.6.1.2.1.2.2.1.16.X | ifOutOctets | Bytes enviados (32-bit) |

### Links Úteis

- 📖 [Documentação Zabbix SNMP](https://www.zabbix.com/documentation/current/en/manual/config/items/itemtypes/snmp)
- 🔍 [OID Repository](http://www.oid-info.com/)
- 📚 [RFC 1213 (MIB-II)](https://www.ietf.org/rfc/rfc1213.txt)
- 🐳 [Docker Documentation](https://docs.docker.com/)
- 🌐 [Net-SNMP](http://www.net-snmp.org/)

---

## 🎯 Próximos Passos

1. ✅ **Concluir setup** - Todos containers rodando e healthy
2. 🔍 **Explorar MIBs** - Usar snmpwalk para descobrir OIDs
3. 📊 **Configurar Zabbix** - Adicionar hosts e criar items
4. 📈 **Criar gráficos** - Visualizar métricas coletadas
5. 🚨 **Configurar triggers** - Alertas para problemas

---

## 🎓 Suporte

**Durante a aula:**
- 🙋 Chamar o instrutor
- 📋 Consultar logs: `docker compose logs`
- 🔍 Verificar status: `docker compose ps`

**Após a aula:**
- 📧 Email: [instrutor@4linux.com.br]
- 💬 Grupo do curso
- 📚 Consultar este README

---

## 📝 Notas Finais

### Características do Ambiente

- ✅ **Leve:** ~4.5 MB total, ~8 MB RAM por container
- ✅ **Rápido:** Setup em 30 segundos
- ✅ **Realista:** Simula infraestrutura real
- ✅ **Isolado:** Não interfere com sistema host
- ✅ **Reproduzível:** Mesmo ambiente para todos

### Limitações

- ❌ **Não possui MIBs de fabricantes** (Cisco, HP, Dell)
  - Use MIBs padrão (RFC1213, IF-MIB, HOST-RESOURCES-MIB)
- ❌ **SNMPv3 não configurado** (apenas SNMPv2c)
  - Community string "public" sem autenticação
- ❌ **Não monitora hardware físico**
  - Sem temperatura, ventiladores, etc.

### Boas Práticas

- 🔄 **Sempre use `docker compose ps`** antes de testar
- 📊 **Verifique logs em caso de erro**: `docker compose logs`
- 🧹 **Limpe ambiente após uso**: `docker compose down`
- 💾 **Mantenha backup do pacote** para reinstalar se necessário

---

<div align="center">

## 🎉 Bom Laboratório!

**Zabbix Advanced - Aula 03**

</div>
