# Laboratórios Práticos - Aula 04
## API e Integrações - Zabbix Advanced

Este diretório contém os laboratórios práticos para a Aula 04 do curso Zabbix Advanced.

---

## 📋 Pré-requisitos

### 1. Instalar dependências Python

```bash
pip install pyzabbix
```

### 2. Configurar acesso ao Zabbix

Edite os scripts e ajuste as seguintes variáveis conforme seu ambiente:

```python
ZABBIX_URL = 'http://localhost/zabbix'  # URL do seu Zabbix
USERNAME = 'Admin'                       # Usuário com permissões
PASSWORD = 'zabbix'                      # Senha
```

### 3. Verificar IDs no Zabbix

Antes de executar os scripts, verifique os IDs corretos no seu ambiente:

**Group ID:**
- Acesse: **Data collection → Host groups**
- Anote o ID do grupo desejado (ex: "Linux servers" = 2)

**Template ID:**
- Acesse: **Data collection → Templates**
- Anote o ID do template desejado (ex: "Linux by Zabbix agent" = 10001)

---

## 🔬 Laboratório 1: Criação em Massa de Hosts

### Objetivo
Criar múltiplos hosts no Zabbix a partir de um arquivo CSV.

### Arquivos
- `lab1_create_hosts_bulk.py` - Script de importação
- `servers.csv` - Arquivo com 20 hosts para teste

### Estrutura do CSV

```csv
hostname,name,ip,groupid,templateid
web-prod-01,Web Server Production 01,10.0.1.10,2,10001
web-prod-02,Web Server Production 02,10.0.1.11,2,10001
...
```

**Campos:**
- `hostname` - Nome técnico do host (único)
- `name` - Nome descritivo
- `ip` - Endereço IP
- `groupid` - ID do grupo no Zabbix
- `templateid` - ID do template no Zabbix

### Passo a passo

1. **Ajustar IDs no CSV:**
   ```bash
   # Edite servers.csv e substitua groupid e templateid pelos IDs do seu ambiente
   nano servers.csv
   ```

2. **Executar importação:**
   ```bash
   python lab1_create_hosts_bulk.py servers.csv
   ```

3. **Verificar no Zabbix:**
   - Acesse: **Data collection → Hosts**
   - Verifique se os 20 hosts foram criados

### Resultado esperado

```
🚀 Iniciando importação de hosts do arquivo: servers.csv

✅ Conectado ao Zabbix: http://localhost/zabbix

✅ Criado: web-prod-01 (ID: 10084)
✅ Criado: web-prod-02 (ID: 10085)
...

============================================================
📊 RESULTADO FINAL
============================================================
✅ Hosts criados com sucesso: 20
❌ Erros encontrados: 0
📈 Total processado: 20
============================================================
```

---

## 🔬 Laboratório 2: Sincronização CMDB

### Objetivo
Sincronizar hosts de um CMDB (simulado via JSON) com o Zabbix.

### Funcionalidades
- ✅ Cria hosts que existem no CMDB mas não no Zabbix
- ✅ Desativa hosts que não existem mais no CMDB
- ✅ Detecta hosts já existentes (não duplica)

### Arquivos
- `lab2_sync_cmdb.py` - Script de sincronização
- `cmdb.json` - Arquivo JSON simulando CMDB (10 hosts)

### Estrutura do JSON

```json
[
  {
    "hostname": "app-prod-01",
    "name": "Application Server Production 01",
    "ip": "10.0.2.10",
    "env": "production"
  },
  ...
]
```

**Campos:**
- `hostname` - Nome técnico do host
- `name` - Nome descritivo
- `ip` - Endereço IP
- `env` - Ambiente (production, staging, development)

### Passo a passo

1. **Primeira execução (criar hosts):**
   ```bash
   python lab2_sync_cmdb.py
   ```

2. **Verificar no Zabbix:**
   - Acesse: **Data collection → Hosts**
   - Verifique se os 10 hosts do CMDB foram criados

3. **Modificar CMDB (simular mudanças):**
   ```bash
   # Edite cmdb.json e remova alguns hosts
   nano cmdb.json
   ```

4. **Segunda execução (detectar mudanças):**
   ```bash
   python lab2_sync_cmdb.py
   ```

5. **Verificar desativações:**
   - Os hosts removidos do CMDB devem ser desativados no Zabbix (não deletados)

### Resultado esperado

```
🔄 Iniciando sincronização CMDB → Zabbix

📋 10 servidores encontrados no CMDB

✅ Conectado ao Zabbix: http://localhost/zabbix

🔍 3 hosts existentes no Zabbix

============================================================
✅ Criado: app-prod-01 (ID: 10090, Env: production)
✅ Criado: app-prod-02 (ID: 10091, Env: production)
⏭️  Já existe: api-prod-01
============================================================
⏸️  Desativado: old-host-01 (não encontrado no CMDB)

============================================================
📊 RESUMO DA SINCRONIZAÇÃO
============================================================
✅ Hosts criados: 7
⏭️  Hosts já existentes: 3
⏸️  Hosts desativados: 1
📈 Total no CMDB: 10
============================================================
```

---

## 🎯 Desafio Extra - Lab 2

Implemente melhorias no script `lab2_sync_cmdb.py`:

1. **Atualizar IPs:** Se o IP mudou no CMDB, atualizar no Zabbix
2. **Tags automáticas:** Adicionar tag `env:production` baseado no campo `env`
3. **Inventário:** Preencher campos de inventário (localização, contato)
4. **Logging:** Salvar log das operações em arquivo
5. **Dry-run mode:** Opção `--dry-run` para mostrar o que seria feito sem executar

---

## 📝 Notas Importantes

### Troubleshooting

**Erro: "No permissions to referred object"**
- Verifique se o usuário tem permissões adequadas
- Acesse: **Users → User roles** e verifique as permissões

**Erro: "Host already exists"**
- O script Lab 1 não verifica duplicatas, execute apenas uma vez
- Use o script Lab 2 para sincronização inteligente

**Erro: "Invalid group"**
- Verifique o `groupid` no CSV/JSON
- Use o ID correto do seu ambiente

**Erro: "Invalid template"**
- Verifique o `templateid` no CSV/JSON
- Use o ID correto do seu ambiente

### Boas Práticas

1. **Teste em ambiente dev primeiro**
2. **Faça backup do Zabbix antes de testes**
3. **Use grupos dedicados para laboratórios** (ex: "Lab-Hosts")
4. **Documente os IDs utilizados** no seu ambiente
5. **Valide o CSV/JSON** antes de executar scripts em produção

---

## 🔗 Documentação Adicional

- [Zabbix API Documentation](https://www.zabbix.com/documentation/current/en/manual/api)
- [PyZabbix Documentation](https://github.com/lukecyca/pyzabbix)
- [Zabbix Host Object](https://www.zabbix.com/documentation/current/en/manual/api/reference/host)

---

## 📧 Suporte

Em caso de dúvidas durante o laboratório, consulte o instrutor.

**Bons estudos! 🚀**
