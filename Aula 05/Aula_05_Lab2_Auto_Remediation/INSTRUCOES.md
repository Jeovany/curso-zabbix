# Laboratório 2 - Auto-Remediation com Zabbix

## Objetivo
Implementar um sistema de **auto-remediation** onde o Zabbix detecta serviços down e executa reinício automático via comando remoto.

---

## Pré-requisitos

- Zabbix Server 7.0 LTS configurado
- Zabbix Agent instalado no host monitorado
- Acesso sudo no host monitorado
- Serviços para monitorar (Apache, MySQL, SSH, etc)

---

## Parte 1: Configuração do Host Monitorado

### 1.1 Copiar script de remediation

```bash
# Criar diretório
sudo mkdir -p /usr/lib/zabbix/alertscripts

# Copiar script
sudo cp restart_service.sh /usr/lib/zabbix/alertscripts/

# Dar permissões
sudo chmod +x /usr/lib/zabbix/alertscripts/restart_service.sh
sudo chown zabbix:zabbix /usr/lib/zabbix/alertscripts/restart_service.sh
```

### 1.2 Criar arquivo de log

```bash
sudo touch /var/log/zabbix-remediation.log
sudo chown zabbix:zabbix /var/log/zabbix-remediation.log
```

### 1.3 Configurar sudoers

```bash
sudo visudo -f /etc/sudoers.d/zabbix
```

**Adicionar a linha:**
```
zabbix ALL=(ALL) NOPASSWD: /usr/lib/zabbix/alertscripts/restart_service.sh
```

**Salvar e validar:**
```bash
sudo visudo -c -f /etc/sudoers.d/zabbix
```

### 1.4 Habilitar comandos remotos no Zabbix Agent

```bash
sudo nano /etc/zabbix/zabbix_agentd.conf
```

**Descomentar ou adicionar:**
```ini
EnableRemoteCommands=1
LogRemoteCommands=1
AllowRoot=0
```

**Reiniciar agent:**
```bash
sudo systemctl restart zabbix-agent
sudo systemctl status zabbix-agent
```

---

## Parte 2: Configuração no Zabbix Server

### 2.1 Criar itens de monitoramento

Acesse: **Data collection → Hosts → [seu-host] → Items → Create item**

**Item 1: Apache**
```
Name: Apache service status
Type: Simple check
Key: net.tcp.service[http]
Type of information: Numeric (unsigned)
Update interval: 1m
```

**Item 2: MySQL**
```
Name: MySQL service status
Type: Simple check
Key: net.tcp.service[mysql]
Type of information: Numeric (unsigned)
Update interval: 1m
```

**Item 3: SSH**
```
Name: SSH service status
Type: Simple check
Key: net.tcp.service[ssh]
Type of information: Numeric (unsigned)
Update interval: 1m
```

### 2.2 Criar triggers

Acesse: **Data collection → Hosts → [seu-host] → Triggers → Create trigger**

**Trigger 1: Apache down**
```
Name: Apache is down
Expression: last(/[host]/net.tcp.service[http])=0
Severity: High
Tags:
  - Tag name: service
    Tag value: apache2
```

**Trigger 2: MySQL down**
```
Name: MySQL is down
Expression: last(/[host]/net.tcp.service[mysql])=0
Severity: High
Tags:
  - Tag name: service
    Tag value: mysql
```

**Trigger 3: SSH down**
```
Name: SSH is down
Expression: last(/[host]/net.tcp.service[ssh])=0
Severity: High
Tags:
  - Tag name: service
    Tag value: ssh
```

### 2.3 Criar Action de Auto-Remediation

Acesse: **Alerts → Actions → Trigger actions → Create action**

**Name:** Auto-restart Services

**Conditions:**
```
A: Trigger severity >= High
B: Tag name = service
```

**Operations:**

**Operation 1: Send message**
```
Send to users: Admin
Send only to: Email (ou seu media type)
Default subject: 🔄 Auto-remediation iniciada
Default message:
Host: {HOST.NAME}
Problema: {EVENT.NAME}
Serviço: {EVENT.TAGS.service}
Hora: {EVENT.TIME} - {EVENT.DATE}

Executando reinício automático do serviço...
```

**Operation 2: Run remote command**
```
Target list: Current host
Type: Custom script
Execute on: Zabbix agent
Commands: /usr/lib/zabbix/alertscripts/restart_service.sh {EVENT.TAGS.service}
```

**Recovery Operations:**

**Operation 1: Send message**
```
Send to users: Admin
Send only to: Email
Default subject: ✅ Serviço recuperado
Default message:
Host: {HOST.NAME}
Problema: {EVENT.NAME}
Serviço: {EVENT.TAGS.service}
Duração: {EVENT.DURATION}

O serviço foi recuperado com sucesso após auto-remediation!
```

---

## Parte 3: Testando o Sistema

### 3.1 Teste manual do script

```bash
# Testar o script diretamente
sudo -u zabbix /usr/lib/zabbix/alertscripts/restart_service.sh apache2

# Verificar log
tail -f /var/log/zabbix-remediation.log
```

### 3.2 Simular problema real

```bash
# Parar o serviço Apache
sudo systemctl stop apache2

# Verificar status
systemctl status apache2

# Aguardar ~1-2 minutos para:
# 1. Zabbix detectar problema
# 2. Trigger disparar
# 3. Action executar remediation
# 4. Serviço ser reiniciado

# Monitorar em tempo real
tail -f /var/log/zabbix-remediation.log
```

### 3.3 Validar resultado

**No Zabbix:**
- Acesse **Monitoring → Problems**
- Verifique se trigger disparou
- Verifique se problema foi resolvido automaticamente

**No host:**
```bash
# Verificar se serviço está rodando
systemctl status apache2

# Verificar log de remediation
cat /var/log/zabbix-remediation.log

# Verificar log do Zabbix Agent
sudo tail -100 /var/log/zabbix/zabbix_agentd.log | grep -i command
```

---

## Resolução de Problemas

### Problema: Script não executa

**Verificar permissões:**
```bash
ls -la /usr/lib/zabbix/alertscripts/restart_service.sh
# Deve mostrar: -rwxr-xr-x zabbix zabbix
```

**Verificar sudoers:**
```bash
sudo -u zabbix sudo /usr/lib/zabbix/alertscripts/restart_service.sh apache2
# Se pedir senha, sudoers está errado
```

### Problema: Comandos remotos não habilitados

**Verificar configuração:**
```bash
grep -i EnableRemoteCommands /etc/zabbix/zabbix_agentd.conf
# Deve retornar: EnableRemoteCommands=1

sudo systemctl restart zabbix-agent
```

### Problema: Serviço não na whitelist

**Editar script e adicionar serviço:**
```bash
sudo nano /usr/lib/zabbix/alertscripts/restart_service.sh

# Linha 18:
ALLOWED_SERVICES="apache2 httpd mysql mariadb postgresql ssh sshd nginx redis-server mongodb seu-servico-aqui"
```

---

## Segurança

⚠️ **IMPORTANTE: Boas práticas de segurança**

1. ✅ **Whitelist**: Apenas serviços específicos podem ser reiniciados
2. ✅ **Validação**: Script valida entrada antes de executar
3. ✅ **Logging**: Todas ações são registradas
4. ✅ **Permissões mínimas**: Script roda como usuário zabbix
5. ✅ **Sudoers restrito**: Apenas script específico tem sudo
6. ❌ **NUNCA** permitir comandos destrutivos (rm, drop, delete)
7. ❌ **NUNCA** usar AllowRoot=1

---

## Desafios Extras

### Desafio 1: Adicionar notificação no Telegram
Integre notificações via Telegram quando auto-remediation for executada.

### Desafio 2: Limitar tentativas
Modifique o script para não tentar reiniciar mais de 3 vezes em 15 minutos.

### Desafio 3: Escalar após falha
Se auto-remediation falhar, criar escalamento para equipe de suporte.

### Desafio 4: Backup antes de reiniciar
Para banco de dados, criar snapshot antes de reiniciar.

---

## Recursos Adicionais

- [Zabbix Remote Commands Documentation](https://www.zabbix.com/documentation/current/en/manual/config/notifications/action/operation/remote_command)
- [Zabbix Agent Configuration](https://www.zabbix.com/documentation/current/en/manual/appendix/config/zabbix_agentd)
- [Security Best Practices](https://www.zabbix.com/documentation/current/en/manual/installation/requirements/best_practices)

---

**4Linux - Zabbix Advanced**
📧 Dúvidas: suporte@4linux.com.br
