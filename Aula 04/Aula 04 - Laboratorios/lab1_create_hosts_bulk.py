#!/usr/bin/env python3
"""
Laboratório 1 - Criação em Massa de Hosts via API
Zabbix Advanced - Aula 04

Descrição:
    Script para criar múltiplos hosts no Zabbix a partir de um arquivo CSV.

Uso:
    python lab1_create_hosts_bulk.py servers.csv

Requisitos:
    pip install pyzabbix
"""

import csv
import sys
from pyzabbix import ZabbixAPI

# Configurações - Ajuste conforme seu ambiente
ZABBIX_URL = 'http://localhost/zabbix'
USERNAME = 'Admin'
PASSWORD = 'zabbix'


def main(csv_file):
    """Cria hosts no Zabbix a partir de arquivo CSV"""

    print(f"🚀 Iniciando importação de hosts do arquivo: {csv_file}\n")

    # Conectar ao Zabbix
    try:
        zapi = ZabbixAPI(ZABBIX_URL)
        zapi.login(USERNAME, PASSWORD)
        print(f"✅ Conectado ao Zabbix: {ZABBIX_URL}\n")
    except Exception as e:
        print(f"❌ Erro ao conectar ao Zabbix: {e}")
        sys.exit(1)

    created = 0
    errors = 0

    # Processar CSV
    with open(csv_file, encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                # Criar host
                result = zapi.host.create(
                    host=row['hostname'],
                    name=row['name'],
                    interfaces=[{
                        'type': 1,          # 1 = Agent
                        'main': 1,          # Interface principal
                        'useip': 1,         # Usar IP
                        'ip': row['ip'],
                        'port': '10050',
                        'dns': ''
                    }],
                    groups=[{'groupid': row['groupid']}],
                    templates=[{'templateid': row['templateid']}]
                )

                hostid = result['hostids'][0]
                print(f"✅ Criado: {row['hostname']} (ID: {hostid})")
                created += 1

            except Exception as e:
                print(f"❌ Erro ao criar {row['hostname']}: {e}")
                errors += 1

    # Resumo
    print(f"\n{'='*60}")
    print(f"📊 RESULTADO FINAL")
    print(f"{'='*60}")
    print(f"✅ Hosts criados com sucesso: {created}")
    print(f"❌ Erros encontrados: {errors}")
    print(f"📈 Total processado: {created + errors}")
    print(f"{'='*60}\n")

    # Logout
    zapi.user.logout()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python lab1_create_hosts_bulk.py <arquivo.csv>")
        print("Exemplo: python lab1_create_hosts_bulk.py servers.csv")
        sys.exit(1)

    main(sys.argv[1])
