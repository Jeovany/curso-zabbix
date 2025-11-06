#!/usr/bin/env python3
"""
Laboratório 2 - Sincronização CMDB → Zabbix
Zabbix Advanced - Aula 04

Descrição:
    Script para sincronizar hosts de um CMDB (simulado via JSON) com o Zabbix.
    - Cria hosts que existem no CMDB mas não no Zabbix
    - Desativa hosts que não existem mais no CMDB

Uso:
    python lab2_sync_cmdb.py

Requisitos:
    pip install pyzabbix
"""

import json
from pyzabbix import ZabbixAPI

# Configurações - Ajuste conforme seu ambiente
ZABBIX_URL = 'http://localhost/zabbix'
USERNAME = 'Admin'
PASSWORD = 'zabbix'
CMDB_FILE = 'cmdb.json'

# Mapeamento de ambiente para template
TEMPLATE_MAP = {
    'production': '10001',   # Linux by Zabbix agent
    'staging': '10001',
    'development': '10001'
}

# Mapeamento de ambiente para grupo
GROUP_MAP = {
    'production': '2',       # Linux servers
    'staging': '2',
    'development': '2'
}


def load_cmdb():
    """Carrega dados do CMDB (arquivo JSON)"""
    try:
        with open(CMDB_FILE, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Arquivo {CMDB_FILE} não encontrado!")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao ler JSON: {e}")
        return []


def main():
    """Sincroniza CMDB com Zabbix"""

    print("🔄 Iniciando sincronização CMDB → Zabbix\n")

    # Ler CMDB
    cmdb_servers = load_cmdb()
    if not cmdb_servers:
        print("❌ Nenhum servidor encontrado no CMDB")
        return

    print(f"📋 {len(cmdb_servers)} servidores encontrados no CMDB\n")

    # Conectar Zabbix
    try:
        zapi = ZabbixAPI(ZABBIX_URL)
        zapi.login(USERNAME, PASSWORD)
        print(f"✅ Conectado ao Zabbix: {ZABBIX_URL}\n")
    except Exception as e:
        print(f"❌ Erro ao conectar ao Zabbix: {e}")
        return

    # Buscar hosts existentes no Zabbix
    existing_hosts = zapi.host.get(output=['hostid', 'host', 'status'])
    existing_dict = {h['host']: h for h in existing_hosts}
    cmdb_hostnames = {s['hostname'] for s in cmdb_servers}

    print(f"🔍 {len(existing_hosts)} hosts existentes no Zabbix\n")
    print("="*60)

    created_count = 0
    skipped_count = 0
    disabled_count = 0

    # Criar novos hosts
    for server in cmdb_servers:
        hostname = server['hostname']

        if hostname not in existing_dict:
            # Host não existe, criar
            try:
                template_id = TEMPLATE_MAP.get(server['env'], '10001')
                group_id = GROUP_MAP.get(server['env'], '2')

                result = zapi.host.create(
                    host=hostname,
                    name=server.get('name', hostname),
                    interfaces=[{
                        'type': 1,
                        'main': 1,
                        'useip': 1,
                        'ip': server['ip'],
                        'port': '10050',
                        'dns': ''
                    }],
                    groups=[{'groupid': group_id}],
                    templates=[{'templateid': template_id}]
                )

                hostid = result['hostids'][0]
                print(f"✅ Criado: {hostname} (ID: {hostid}, Env: {server['env']})")
                created_count += 1

            except Exception as e:
                print(f"❌ Erro ao criar {hostname}: {e}")

        else:
            print(f"⏭️  Já existe: {hostname}")
            skipped_count += 1

    print("="*60)

    # Desativar hosts que não existem mais no CMDB
    for hostname, host in existing_dict.items():
        if hostname not in cmdb_hostnames and host['status'] == '0':
            # Host não está no CMDB e está ativo
            try:
                zapi.host.update(hostid=host['hostid'], status=1)
                print(f"⏸️  Desativado: {hostname} (não encontrado no CMDB)")
                disabled_count += 1
            except Exception as e:
                print(f"❌ Erro ao desativar {hostname}: {e}")

    # Resumo
    print(f"\n{'='*60}")
    print(f"📊 RESUMO DA SINCRONIZAÇÃO")
    print(f"{'='*60}")
    print(f"✅ Hosts criados: {created_count}")
    print(f"⏭️  Hosts já existentes: {skipped_count}")
    print(f"⏸️  Hosts desativados: {disabled_count}")
    print(f"📈 Total no CMDB: {len(cmdb_servers)}")
    print(f"{'='*60}\n")

    # Logout
    zapi.user.logout()


if __name__ == '__main__':
    main()
