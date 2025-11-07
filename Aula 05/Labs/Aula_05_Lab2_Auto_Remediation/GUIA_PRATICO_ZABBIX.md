# Guia Prático - Laboratório 2: Auto-Remediation
## Aula 05 - Zabbix Advanced

---

## 📋 Visão Geral

Quando um serviço (Apache, MySQL ou SSH) cair:
1. ✅ Zabbix detecta o problema automaticamente
2. ✅ Executa script de remediation no host
3. ✅ Serviço é reiniciado automaticamente
4. ✅ Notificação é enviada confirmando recuperação

---

## 🔧 PARTE 1: Preparação do Host Monitorado

### Passo 1.1: Copiar Script de Remediation

```bash
# 1. Criar diretório
sudo mkdir -p /usr/lib/zabbix/alertscripts

# 2. Copiar script (use o arquivo restart_service.sh fornecido)
sudo cp restart_service.sh /usr/lib/zabbix/alertscripts/

# 3. Dar permissões corretas
sudo chmod +x /usr/lib/zabbix/alertscripts/restart_service.sh
sudo chown zabbix:zabbix /usr/lib/zabbix/alertscripts/restart_service.sh

# 4. Verificar
ls -la /usr/lib/zabbix/alertscripts/restart_service.sh
# Deve mostrar: -rwxr-xr-x ... zabbix zabbix ... restart_service.sh
```

### Passo 1.2: Criar Arquivo de Log

```bash
# Criar arquivo de log
sudo touch /var/log/zabbix-remediation.log
sudo chown zabbix:zabbix /var/log/zabbix-remediation.log

# Verificar
ls -la /var/log/zabbix-remediation.log
```

### Passo 1.3: Configurar Sudoers

```bash
# Editar sudoers do Zabbix
sudo visudo -f /etc/sudoers.d/zabbix
```

**Adicionar a seguinte linha:**
```
zabbix ALL=(ALL) NOPASSWD: /usr/lib/zabbix/alertscripts/restart_service.sh
```

**Salvar e validar:**
```bash
sudo visudo -c -f /etc/sudoers.d/zabbix
# Deve retornar: /etc/sudoers.d/zabbix: parsed OK
```

### Passo 1.4: Habilitar Comandos Remotos no Zabbix Agent

```bash
# Editar configuração do agent
sudo nano /etc/zabbix/zabbix_agentd.conf
```

**Adicionar ou descomentar as linhas:**
```ini
EnableRemoteCommands=1
LogRemoteCommands=1
AllowRoot=0
```

**Reiniciar o agent:**
```bash
sudo systemctl restart zabbix-agent
sudo systemctl status zabbix-agent
# Verificar que está "active (running)"
```

### Passo 1.5: Testar Script Manualmente (Opcional mas Recomendado)

```bash
# Testar se o script funciona
sudo -u zabbix /usr/lib/zabbix/alertscripts/restart_service.sh apache2

# Verificar log
tail -10 /var/log/zabbix-remediation.log
```

**Output esperado:**
```
[2025-01-07 10:30:45] 🔄 Tentando reiniciar apache2...
[2025-01-07 10:30:50] ✅ apache2 reiniciado com sucesso
```

---

## 🖥️ PARTE 2: Configuração no Zabbix Server

### Passo 2.1: Criar Itens de Monitoramento

**Acesse:** Data collection → Hosts → web-prod-01 → Items → Create item

**Item 1: Apache Service Status**
```
Name: Apache service status
Type: Simple check
Key: net.tcp.service[http]
Type of information: Numeric (unsigned)
Update interval: 1m
Description: Monitora disponibilidade do Apache na porta 80
```

**Item 2: MySQL Service Status**
```
Name: MySQL service status
Type: Simple check
Key: net.tcp.service[mysql]
Type of information: Numeric (unsigned)
Update interval: 1m
Description: Monitora disponibilidade do MySQL na porta 3306
```

**Item 3: SSH Service Status**
```
Name: SSH service status
Type: Simple check
Key: net.tcp.service[ssh]
Type of information: Numeric (unsigned)
Update interval: 1m
Description: Monitora disponibilidade do SSH na porta 22
```

**Click: Add** para cada item

---

### Passo 2.2: Criar Triggers com Tags

**Acesse:** Data collection → Hosts → web-prod-01 → Triggers → Create trigger

**Trigger 1: Apache is down**
```
Name: Apache is down
Severity: High

Expression:
  last(/web-prod-01/net.tcp.service[http])=0

Description: Apache HTTP service não está respondendo na porta 80

Tags:
  - Tag name: service
    Tag value: apache2
  - Tag name: component
    Tag value: webserver
```

**Trigger 2: MySQL is down**
```
Name: MySQL is down
Severity: High

Expression:
  last(/web-prod-01/net.tcp.service[mysql])=0

Description: MySQL database service não está respondendo na porta 3306

Tags:
  - Tag name: service
    Tag value: mysql
  - Tag name: component
    Tag value: database
```

**Trigger 3: SSH is down**
```
Name: SSH is down
Severity: High

Expression:
  last(/web-prod-01/net.tcp.service[ssh])=0

Description: SSH service não está respondendo na porta 22

Tags:
  - Tag name: service
    Tag value: ssh
  - Tag name: component
    Tag value: system
```

**⚠️ IMPORTANTE:** As tags `service:apache2`, `service:mysql`, `service:ssh` são **cruciais** para o auto-remediation funcionar!

**Click: Add** para cada trigger

---

### Passo 2.3: Criar Action de Auto-Remediation

**Acesse:** Alerts → Actions → Trigger actions → Create action

**Nome:** `Auto-restart Services`

**Tab: Operations**

#### Conditions (Condições)

Click em **Add** para cada condição:

**Condição 1:**
```
Type: Trigger severity
Operator: >=
Severity: High
```

**Condição 2:**
```
Type: Tag name
Operator: equals
Tag name: service
```

**Evaluation type:** And/Or (deixar padrão: And)

---

#### Operations (Operações)

**Operation 1: Enviar Notificação**

Click em **Add** (Operations):
```
Operation type: Send message

Send to:
  Users: Admin

Send only to: Email (ou seu media type configurado)

Default subject:
  🔄 Auto-Remediation Iniciada

Default message:
  Host: {HOST.NAME}
  Problema: {EVENT.NAME}
  Serviço: {EVENT.TAGS.service}
  Hora: {EVENT.TIME} - {EVENT.DATE}

  Executando reinício automático do serviço...

  Dashboard: {$ZABBIX.URL}/zabbix.php?action=problem.view
```

**Operation 2: Executar Comando Remoto**

Click em **Add** novamente:
```
Operation type: Remote command

Target list: Current host

Type: Custom script

Execute on: Zabbix agent

Commands:
  /usr/lib/zabbix/alertscripts/restart_service.sh {EVENT.TAGS.service}
```

**⚠️ Atenção:** `{EVENT.TAGS.service}` será substituído por `apache2`, `mysql` ou `ssh` dependendo da trigger!

---

#### Recovery Operations (Operações de Recuperação)

**Tab: Recovery operations**

Click em **Add**:
```
Operation type: Send message

Send to:
  Users: Admin

Send only to: Email

Default subject:
  ✅ Serviço Recuperado Após Auto-Remediation

Default message:
  Host: {HOST.NAME}
  Problema: {EVENT.NAME}
  Serviço: {EVENT.TAGS.service}
  Duração: {EVENT.DURATION}

  O serviço foi recuperado com sucesso após auto-remediation!

  Resolução: {EVENT.RECOVERY.TIME} - {EVENT.RECOVERY.DATE}
```

**Click: Add** (na action)

**Status: Enabled ✅**

---

## 🧪 PARTE 3: Testando o Sistema

### Passo 3.1: Monitorar Logs em Tempo Real

Abra um terminal no host monitorado:

```bash
# Terminal 1: Monitorar log de remediation
tail -f /var/log/zabbix-remediation.log

# Terminal 2: Monitorar log do Zabbix Agent
sudo tail -f /var/log/zabbix/zabbix_agentd.log | grep -i command
```

### Passo 3.2: Simular Falha do Serviço

```bash
# Parar o Apache para simular problema
sudo systemctl stop apache2

# Verificar status (deve estar stopped/inactive)
systemctl status apache2
```

### Passo 3.3: Aguardar Auto-Remediation

**Timeline esperada:**

```
00:00 - Apache parado manualmente
00:60 - Zabbix detecta problema (próximo check, 1 minuto)
01:00 - Trigger "Apache is down" dispara
01:05 - Action executa comando remoto
01:10 - Script reinicia Apache
01:15 - Apache volta ao normal
01:16 - Trigger recupera automaticamente
01:20 - Notificação de recuperação enviada
```

### Passo 3.4: Verificar Resultados

**1. Verificar se serviço voltou:**
```bash
systemctl status apache2
# Deve mostrar: active (running)
```

**2. Verificar log de remediation:**
```bash
cat /var/log/zabbix-remediation.log
```

**Output esperado:**
```
[2025-01-07 14:35:10] 🔄 Iniciando verificação do serviço: apache2
[2025-01-07 14:35:10] ⚠️ Serviço apache2 está INATIVO. Tentando reiniciar...
[2025-01-07 14:35:15] ✅ SUCESSO: apache2 reiniciado com sucesso
```

**3. Verificar no Zabbix:**
```
Monitoring → Problems

Deve mostrar:
  ✅ Problema: "Apache is down" - RESOLVED
  Duração: ~1-2 minutos
  Actions: 2 operações executadas
```

**4. Verificar histórico de actions:**
```
Reports → Action log

Deve mostrar:
  - Message sent (notificação inicial)
  - Remote command (script executado)
  - Message sent (notificação de recuperação)
```

---

## 🔍 Troubleshooting

### Problema 1: Script não executa

**Sintoma:** Serviço não reinicia automaticamente

**Verificações:**

```bash
# 1. Verificar permissões do script
ls -la /usr/lib/zabbix/alertscripts/restart_service.sh
# Deve ser: -rwxr-xr-x zabbix zabbix

# 2. Testar sudoers
sudo -u zabbix sudo /usr/lib/zabbix/alertscripts/restart_service.sh apache2
# Se pedir senha, sudoers está incorreto!

# 3. Verificar logs do Zabbix Agent
sudo grep -i "remote command" /var/log/zabbix/zabbix_agentd.log
```

**Solução:**
- Corrigir permissões: `sudo chown zabbix:zabbix restart_service.sh`
- Reconfigurar sudoers conforme Passo 1.3

---

### Problema 2: Trigger não dispara

**Sintoma:** Apache para mas trigger não detecta

**Verificações:**

```bash
# 1. Testar item manualmente
zabbix_get -s web-prod-01 -k net.tcp.service[http]
# Deve retornar: 0 (se Apache está stopped)

# 2. Verificar Latest Data
Monitoring → Hosts → web-prod-01 → Latest data
  Procurar: "Apache service status"
  Valor atual deve ser: 0
```

**Solução:**
- Verificar firewall (porta 10050 aberta)
- Verificar conectividade: `telnet web-prod-01 10050`

---

### Problema 3: Tag não funciona

**Sintoma:** Action não executa comando remoto

**Verificações:**

```bash
# 1. Verificar tags na trigger
Data collection → Hosts → Triggers → [trigger] → Tags
  Deve ter: service = apache2 (exato, case-sensitive!)

# 2. Verificar conditions na action
Alerts → Actions → [action] → Conditions
  Deve ter: "Tag name equals service"
```

**Solução:**
- Tags são **case-sensitive**: `service` ≠ `Service`
- Valor da tag deve ser exato: `apache2` ≠ `Apache2`

---

### Problema 4: Comando executa mas serviço não sobe

**Sintoma:** Log mostra tentativa mas falha

**Verificações:**

```bash
# 1. Ver erro detalhado no log
cat /var/log/zabbix-remediation.log

# 2. Testar manualmente
sudo systemctl restart apache2
sudo systemctl status apache2

# 3. Verificar logs do serviço
sudo journalctl -u apache2 -n 50
```

**Solução comum:**
- Erro de configuração no Apache: `sudo apachectl configtest`
- Porta já em uso: `sudo netstat -tlnp | grep :80`

---

## 📊 Validação Final

### Checklist de Sucesso

- [ ] ✅ Script está em `/usr/lib/zabbix/alertscripts/` com permissões corretas
- [ ] ✅ Sudoers configurado (`visudo -c` retorna OK)
- [ ] ✅ Comandos remotos habilitados no agent (EnableRemoteCommands=1)
- [ ] ✅ Itens criados e coletando dados (Latest Data mostra valores)
- [ ] ✅ Triggers criadas com **tags corretas** (service:apache2, etc)
- [ ] ✅ Action criada com **2 conditions** (severity + tag)
- [ ] ✅ Action tem **2 operations** (message + remote command)
- [ ] ✅ Action tem **recovery operation** (message)
- [ ] ✅ Teste manual funcionou (parar Apache → auto-reinicia)
- [ ] ✅ Log de remediation mostra sucesso
- [ ] ✅ Monitoring → Problems mostra problema resolvido

---

## 🎯 Desafios Extras

Após completar o laboratório básico, tente:

### Desafio 1: Adicionar Nginx
Crie trigger e configure auto-remediation para Nginx também.

### Desafio 2: Limitar Tentativas
Modifique o script para não tentar reiniciar mais de 3 vezes em 15 minutos.

### Desafio 3: Notificação no Telegram
Configure notificações via Telegram ao invés de email.

### Desafio 4: Escalar Após Falha
Se auto-remediation falhar 2 vezes, criar escalamento para coordenador.

---

## 📚 Recursos Adicionais

**Documentação Oficial:**
- [Zabbix Remote Commands](https://www.zabbix.com/documentation/current/en/manual/config/notifications/action/operation/remote_command)
- [Zabbix Agent Configuration](https://www.zabbix.com/documentation/current/en/manual/appendix/config/zabbix_agentd)
- [Event Tags](https://www.zabbix.com/documentation/current/en/manual/config/triggers/trigger#event-tags)

**Arquivos do Lab:**
- `restart_service.sh` - Script principal
- `INSTRUCOES.md` - Guia técnico completo
- `sudoers_zabbix` - Configuração sudoers pronta
- `zabbix_agentd_remotecommands.conf` - Config do agent

---

## ⚠️ Notas de Segurança

**IMPORTANTE - Leia antes de usar em produção:**

1. ✅ **Whitelist de serviços**: Script só permite serviços específicos
2. ✅ **Validação de entrada**: Protege contra command injection
3. ✅ **Logging completo**: Todas ações são auditadas
4. ✅ **Permissões mínimas**: Script roda como usuário zabbix
5. ❌ **NUNCA** permitir comandos destrutivos (rm, drop, delete)
6. ❌ **NUNCA** usar AllowRoot=1 no agent
7. ⚠️ **Testar extensivamente** antes de produção

---

**4Linux - Zabbix Advanced**
*Laboratório 2 - Aula 05*
