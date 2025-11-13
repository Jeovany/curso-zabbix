#!/usr/bin/env python3
"""
Script para criar triggers automaticamente para Web Scenarios no Zabbix 7.0
Versão: 1.0 - Com listagem de Web Scenarios
Autor: Jeovany Batista
"""

import requests
import json
import sys

ZABBIX_URL = "https://seu.zabbix/api_jsonrpc.php"
ZABBIX_USER = "Admin"
ZABBIX_PASSWORD = "zabbix"

# Desabilitar verificação SSL (use apenas se necessário)
VERIFY_SSL = False  # Mude para True em produção com certificado válido

# Nome EXATO do host onde estão os Web Scenarios
HOST_NAME = "Zabbix server"

# Lista dos nomes EXATOS dos seus Web Scenarios
# DEIXE VAZIO [] para o script listar os nomes automaticamente
WEB_SCENARIOS = []

# Configurações da trigger
TRIGGER_PRIORITY = 4  # 0=Not classified, 1=Info, 2=Warning, 3=Average, 4=High, 5=Disaster
TRIGGER_DESCRIPTION = """O Web Scenario "{SCENARIO}" apresentou falha após 2 verificações consecutivas.

Ação recomendada:
1. Verificar conectividade com o endpoint
2. Validar se o serviço web está respondendo
3. Checar logs da aplicação
4. Verificar certificado SSL (se aplicável)"""


class ZabbixAPI:
    def __init__(self, url, user, password, verify_ssl=True):
        self.url = url
        self.user = user
        self.password = password
        self.verify_ssl = verify_ssl
        self.auth_token = None
        self.request_id = 1
        
        # Desabilita warnings de SSL se verify_ssl=False
        if not verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
    def _call(self, method, params=None):
        """Faz uma chamada à API do Zabbix"""
        headers = {'Content-Type': 'application/json'}
        
        data = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self.request_id
        }
        
        if self.auth_token:
            data["auth"] = self.auth_token
            
        self.request_id += 1
        
        try:
            response = requests.post(self.url, json=data, headers=headers, 
                                    timeout=30, verify=self.verify_ssl)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                raise Exception(f"Erro da API: {result['error']}")
                
            return result.get("result")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro de conexão: {e}")
    
    def login(self):
        """Autentica na API do Zabbix"""
        print(f"Conectando ao Zabbix em {self.url}...")
        result = self._call("user.login", {
            "username": self.user,
            "password": self.password
        })
        self.auth_token = result
        print("✓ Autenticação bem-sucedida")
        return True
    
    def logout(self):
        """Faz logout da API"""
        if self.auth_token:
            self._call("user.logout")
            self.auth_token = None
    
    def get_host_id(self, hostname):
        """Obtém o ID do host pelo nome"""
        result = self._call("host.get", {
            "filter": {"host": hostname},
            "output": ["hostid", "host"]
        })
        
        if not result:
            raise Exception(f"Host '{hostname}' não encontrado")
            
        return result[0]["hostid"]
    
    def get_web_scenarios_with_items(self, hostid):
        """Lista todos os Web Scenarios com seus itens"""
        result = self._call("httptest.get", {
            "hostids": hostid,
            "output": ["httptestid", "name"],
            "selectSteps": "extend"
        })
        return result
    
    def get_web_scenario_item_by_name(self, hostid, scenario_name):
        """Busca o item 'Failed step' de um Web Scenario específico"""
        
        item_key = f"web.test.fail[{scenario_name}]"
        
        # Tenta buscar com webitems=True para pegar itens de web monitoring
        result = self._call("item.get", {
            "hostids": hostid,
            "webitems": True,  # CRITICAL: busca itens de web monitoring
            "filter": {"key_": item_key},
            "output": ["itemid", "key_", "name"]
        })
        
        return result[0] if result else None
    
    def get_web_scenario_items(self, hostid, scenario_name):
        """Lista todos os itens relacionados a um Web Scenario"""
        result = self._call("item.get", {
            "hostids": hostid,
            "search": {"key_": f"web.test"},
            "searchByAny": True,
            "output": ["itemid", "key_", "name"],
            "sortfield": "name"
        })
        
        # Filtra apenas itens do Web Scenario específico
        items = [item for item in result if f"[{scenario_name}" in item['key_'] or f"[{scenario_name}]" in item['key_']]
        return items
    
    def get_item(self, hostid, item_key):
        """Obtém um item específico do host - incluindo itens de Web monitoring"""
        
        scenario_name = item_key.replace('web.test.fail[', '').replace(']', '')
        
        print(f"    [DEBUG] Buscando item web.test.fail[{scenario_name}]")
        
        # Usa o método especializado que busca itens de web monitoring
        item = self.get_web_scenario_item_by_name(hostid, scenario_name)
        
        if item:
            print(f"    [DEBUG] ✓ Item encontrado: {item['name']}")
            print(f"    [DEBUG]   Key: {item['key_']}")
            return item
        
        print(f"    [DEBUG] ✗ Item não encontrado")
        return None
    
    def check_trigger_exists(self, hostid, scenario_name):
        """Verifica se já existe uma trigger para o Web Scenario"""
        trigger_name = f"O endpoint {scenario_name} está down"

        existing = self._call("trigger.get", {
            "hostids": hostid,
            "filter": {"description": trigger_name},
            "output": ["triggerid"]
        })

        return existing[0]['triggerid'] if existing else None

    def create_trigger(self, hostid, scenario_name):
        """Cria uma trigger para um Web Scenario"""

        # No Zabbix 7.0, procura pelo item "Failed step of scenario"
        item_key = f"web.test.fail[{scenario_name}]"

        # Verifica se o item existe
        item = self.get_item(hostid, item_key)
        if not item:
            print(f"  ✗ Item 'Failed step of scenario \"{scenario_name}\"' não encontrado")
            return False

        # Usa a key REAL do item encontrado
        real_item_key = item['key_']

        # Expressão da trigger (2 falhas consecutivas)
        expression = f"min(/{HOST_NAME}/{real_item_key},#2)>0"
        recovery_expression = f"last(/{HOST_NAME}/{real_item_key})=0"

        # Nome da trigger
        trigger_name = f"O endpoint {scenario_name} está down"

        # Descrição personalizada
        description = TRIGGER_DESCRIPTION.replace("{SCENARIO}", scenario_name)

        # Verifica se a trigger já existe
        existing = self._call("trigger.get", {
            "hostids": hostid,
            "filter": {"description": trigger_name},
            "output": ["triggerid"]
        })

        if existing:
            print(f"  ⚠ Trigger '{trigger_name}' já existe (ID: {existing[0]['triggerid']})")
            return None

        # Cria a trigger
        try:
            result = self._call("trigger.create", {
                "description": trigger_name,
                "expression": expression,
                "recovery_mode": 1,  # Recovery expression
                "recovery_expression": recovery_expression,
                "priority": TRIGGER_PRIORITY,
                "manual_close": 1,
                "comments": description,
                "tags": [
                    {"tag": "Application", "value": "WebScenarios"},
                    {"tag": "Endpoint", "value": scenario_name},
                    {"tag": "Scope", "value": "availability"}
                ]
            })

            trigger_id = result["triggerids"][0]
            print(f"  ✓ Trigger criada: '{trigger_name}' (ID: {trigger_id})")
            return True

        except Exception as e:
            print(f"  ✗ Erro ao criar trigger para '{scenario_name}': {e}")
            return False


def main():
    """Função principal"""
    
    print("=" * 70)
    print("CRIADOR AUTOMÁTICO DE TRIGGERS PARA WEB SCENARIOS")
    print("Zabbix 7.0 LTS")
    print("=" * 70)
    print()
    
    print(f"Host alvo: {HOST_NAME}")
    print()
    
    # Conecta ao Zabbix
    zapi = ZabbixAPI(ZABBIX_URL, ZABBIX_USER, ZABBIX_PASSWORD, VERIFY_SSL)
    
    try:
        # Login
        zapi.login()
        
        # Obtém ID do host
        print(f"Buscando host '{HOST_NAME}'...")
        hostid = zapi.get_host_id(HOST_NAME)
        print(f"✓ Host encontrado (ID: {hostid})")
        print()
        
        # Lista Web Scenarios existentes
        print("Listando Web Scenarios existentes no host:")
        print("-" * 70)
        web_scenarios = zapi.get_web_scenarios_with_items(hostid)
        
        if not web_scenarios:
            print("⚠ AVISO: Nenhum Web Scenario encontrado neste host!")
            print("Certifique-se de que o host possui Web Scenarios configurados.")
            zapi.logout()
            sys.exit(1)
        
        print(f"Total de Web Scenarios encontrados: {len(web_scenarios)}")
        print()
        
        # Mostra os nomes
        for i, ws in enumerate(web_scenarios, 1):
            print(f"  {i:2d}. '{ws['name']}' (ID: {ws['httptestid']})")
        print()
        print("-" * 70)
        print()
        
        # Se WEB_SCENARIOS estiver vazio, usa os encontrados
        global WEB_SCENARIOS
        if not WEB_SCENARIOS:
            print("Lista WEB_SCENARIOS está vazia. Usando todos os Web Scenarios encontrados.")
            WEB_SCENARIOS = [ws['name'] for ws in web_scenarios]

        # Verifica quais Web Scenarios já têm triggers criadas
        print("Verificando triggers existentes:")
        print("-" * 70)

        with_trigger = []
        without_trigger = []

        for scenario in WEB_SCENARIOS:
            trigger_id = zapi.check_trigger_exists(hostid, scenario)
            if trigger_id:
                with_trigger.append((scenario, trigger_id))
                print(f"  ✓ '{scenario}' - Trigger já existe (ID: {trigger_id})")
            else:
                without_trigger.append(scenario)
                print(f"  ✗ '{scenario}' - Sem trigger")

        print()
        print("-" * 70)
        print(f"Total: {len(with_trigger)} com trigger | {len(without_trigger)} sem trigger")
        print("-" * 70)
        print()

        # Se todos já têm triggers
        if not without_trigger:
            print("✓ Todos os Web Scenarios já possuem triggers criadas!")
            print("Nenhuma ação necessária.")
            zapi.logout()
            sys.exit(0)

        # Se há Web Scenarios sem trigger
        print(f"Os seguintes Web Scenarios NÃO possuem triggers ({len(without_trigger)}):")
        for i, scenario in enumerate(without_trigger, 1):
            print(f"  {i:2d}. '{scenario}'")
        print()

        resposta = input(f"Deseja criar triggers para estes {len(without_trigger)} Web Scenarios? (sim/nao): ").lower()

        if resposta not in ['sim', 's', 'yes', 'y']:
            print("\nOperação cancelada pelo usuário.")
            zapi.logout()
            sys.exit(0)

        print()
        print("Criando triggers:")
        print("-" * 70)

        created = 0
        skipped = 0
        errors = 0

        # Cria triggers apenas para os que não têm
        for scenario in without_trigger:
            result = zapi.create_trigger(hostid, scenario)
            if result is True:
                created += 1
            elif result is None:
                skipped += 1
            else:
                errors += 1
        
        # Resumo
        print()
        print("=" * 70)
        print("RESUMO:")
        print(f"  Triggers criadas com sucesso: {created}")
        print(f"  Triggers já existentes (ignoradas): {skipped}")
        print(f"  Erros: {errors}")
        print("=" * 70)
        
        # Logout
        zapi.logout()
        print()
        print("✓ Script concluído com sucesso!")
        
    except Exception as e:
        print(f"\n✗ ERRO: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
