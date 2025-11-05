# Labs da Aula 03 para Ambiente Docker

## 📋 Resumo da Compatibilidade

*========================================
LABORATÓRIO SNMP DOCKER - SETUP RÁPIDO
Zabbix Advanced - Aula 03
========================================

📦 CONTEÚDO DO PACOTE:

- lab-snmp-image.tar.gz  (Imagem Docker - 4.5MB)
- docker-compose.yml     (Configuração dos 7 containers)
- setup.sh               (Script automático Linux/Mac)
- setup.bat              (Script automático Windows)
- README.md              (Documentação completa)
- INSTRUCOES.txt         (Este arquivo)

========================================
🚀 INSTALAÇÃO RÁPIDA
========================================

LINUX/MAC:
----------
1. Abrir terminal nesta pasta
2. Executar: chmod +x setup.sh
3. Executar: ./setup.sh
4. Pronto! ✅

WINDOWS:
--------
1. Abrir PowerShell ou CMD nesta pasta
2. Executar: setup.bat
3. Pronto! ✅

MANUAL (Todos os sistemas):
----------------------------
1. docker load -i lab-snmp-image.tar.gz
2. docker compose up -d
3. Aguardar 30 segundos
4. docker compose ps

========================================
✅ VERIFICAÇÃO
========================================

Todos os 7 containers devem estar "healthy":

- snmp-switch-core     (porta 10161)
- snmp-switch-access   (porta 10162)
- snmp-server-web      (porta 10163)
- snmp-server-db       (porta 10164)
- snmp-firewall        (porta 10165)
- snmp-printer         (porta 10166)
- snmp-ups             (porta 10167)

Testar SNMP (se tiver snmpwalk instalado):
  snmpwalk -v2c -c public localhost:10161 system

========================================
🔧 PRÉ-REQUISITOS
========================================

✅ Docker instalado e funcionando
   - Linux: https://get.docker.com
   - Windows/Mac: https://www.docker.com/products/docker-desktop

✅ Docker Compose disponível
   - Vem junto com Docker Desktop
   - Linux: sudo apt-get install docker-compose-plugin

⚠️ Opcional (recomendado):
   - snmpwalk para testes
   - Linux: sudo apt-get install snmp
   - Mac: brew install net-snmp

========================================
📊 INFORMAÇÕES DOS CONTAINERS
========================================

Community SNMP: public
Versão SNMP: v2c
Rede Docker: 172.25.0.0/16

DISPOSITIVOS:
--------------
1. Switch Core       - 172.25.0.10:161 / localhost:10161
2. Switch Access     - 172.25.0.11:161 / localhost:10162
3. Web Server        - 172.25.0.20:161 / localhost:10163
4. Database Server   - 172.25.0.21:161 / localhost:10164
5. Firewall          - 172.25.0.5:161  / localhost:10165
6. Printer           - 172.25.0.30:161 / localhost:10166
7. UPS               - 172.25.0.31:161 / localhost:10167

========================================
💡 COMANDOS ÚTEIS
========================================

Ver status:
  docker compose ps

Ver logs:
  docker compose logs
  docker compose logs snmp-switch-core

Parar tudo:
  docker compose down

Reiniciar:
  docker compose restart

Iniciar novamente:
  docker compose up -d

Remover tudo:
  docker compose down -v
  docker rmi lab-snmp:1.0

========================================
🧪 TESTES BÁSICOS
========================================

Testar todos os containers:
  for port in {10161..10167}; do
    echo "=== Porta $port ==="
    snmpget -v2c -c public localhost:$port SNMPv2-MIB::sysName.0
  done

Listar interfaces:
  snmpwalk -v2c -c public localhost:10161 IF-MIB::ifDescr

Ver informações do sistema:
  snmpwalk -v2c -c public localhost:10161 system

Comparar GET vs GET-BULK:
  time snmpwalk -v2c -c public localhost:10161 1.3.6.1.2.1.2
  time snmpbulkwalk -v2c -c public localhost:10161 1.3.6.1.2.1.2

========================================
❓ TROUBLESHOOTING
========================================

PROBLEMA: "Cannot connect to Docker daemon"
SOLUÇÃO:
  - Certifique-se que Docker está rodando
  - Linux: sudo systemctl start docker
  - Windows/Mac: Inicie Docker Desktop

PROBLEMA: "port is already allocated"
SOLUÇÃO:
  - Porta já está em uso
  - Verifique: sudo lsof -i :10161
  - Pare o processo ou mude porta no docker-compose.yml

PROBLEMA: "network already exists"
SOLUÇÃO:
  - docker compose down
  - docker network prune
  - docker compose up -d

PROBLEMA: Containers reiniciando
SOLUÇÃO:
  - Ver logs: docker compose logs
  - Aguardar 1 minuto (pode estar iniciando)
  - Verificar RAM disponível (mínimo 500MB)

========================================
📧 SUPORTE
========================================

Em caso de problemas durante a aula:
1. Chamar o instrutor
2. Verificar logs: docker compose logs
3. Consultar README.md para mais detalhes

========================================
🎓 BOM LABORATÓRIO!
========================================