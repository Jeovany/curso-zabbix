---
marp: true
theme: default
paginate: true
backgroundColor: #fff
backgroundImage: url('https://marp.app/assets/hero-background.svg')
header: 'Zabbix Advanced - Aula 06'
footer: 'Supressão e Correlação de Incidentes | 4Linux'
---

<!-- _class: lead -->
<!-- _paginate: false -->

# Zabbix Advanced
## Aula 06: Supressão e Correlação de Incidentes

### 4Linux - Curso Avançado

---

# Agenda do Dia

1. **Fundamentos da Supressão de Eventos**
   - Conceitos, tipos, impactos

2. **Event Correlation - Fundamentos**
   - Correlação temporal, por tags, por padrões

3. **Supressão Durante Manutenção**
   - Planejamento, boas práticas

---

# Agenda do Dia (cont.)

4. **Laboratórios Práticos**
   - Event Correlation via GUI
   - Maintenance Periods
   - Validação de eficácia

5. **Troubleshooting e Métricas**
   - Problemas comuns, indicadores de sucesso

---

<!-- _class: lead -->

# PARTE 1
## Fundamentos da Supressão de Eventos

---

# O Que É Supressão de Eventos?

**Supressão** = Controle de **quando e como** alertas são notificados

<style scoped>
pre { font-size: 0.6em; }
</style>

```
┌─────────────────────────────────────────┐
│  Evento Detectado (Trigger)             │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Filtro Inteligente (Supressão)         │
│  - Avaliar contexto                     │
│  - Verificar dependências               │
│  - Analisar correlação                  │
└─────────────┬───────────────────────────┘
              │
      ┌───────┴────────┐
      ▼                ▼
┌──────────┐    ┌──────────────┐
│ Notificar│    │ Suprimir     │
│ Equipe   │    │ (Registrar)  │
└──────────┘    └──────────────┘
```

**Eventos continuam registrados, mas não geram notificações desnecessárias**

---

# Cenário Real - O Problema

**Sem supressão:**

```
Switch core fica offline ➜

  → 1 alerta: Switch core unreachable
  → 50 alertas: Servidores conectados unreachable
  → 200 alertas: Serviços nestes servidores down
  → 100 alertas: Websites inacessíveis
  ─────────────────────────────────────────
  = 351 notificações para 1 problema! 🔥
```

---

# Cenário Real - O Problema (cont.)

**Com supressão:**

```
Switch core fica offline ➜

  → 1 alerta: Switch core unreachable
  → 350 alertas suprimidos ✅
  = Foco no problema real!
```

---

# Por Que Supressão É Importante?

**Problemas causados por falta de supressão:**

- 🔴 **Fadiga de alertas**: Operadores ignoram notificações
- ⏱️ **Tempo de resposta aumentado**: Triagem de alertas redundantes
- 💰 **Custo operacional**: Horas desperdiçadas
- 📉 **Impacto no SLA**: Demora em identificar causa raiz

---

# Benefícios de Supressão

**Benefícios da supressão bem implementada:**

- ✅ **Redução de 60-80%** no volume de notificações
- ✅ **MTTR reduzido em 40-50%**: Identificação mais rápida
- ✅ **Melhoria na qualidade de vida** da equipe
- ✅ **ROI mensurável**: 2-3 horas/dia economizadas (ambientes 500+ hosts)

---

# Tipos de Supressão no Zabbix

**1. Supressão por Dependência (Trigger Dependencies)**
- Relacionamentos hierárquicos entre hosts/serviços
- Trigger A depende de Trigger B → suprime A quando B está em problema

**2. Supressão por Manutenção (Maintenance Periods)**
- Janelas programadas de trabalho
- Evita alertas durante atualizações/patches

**3. Supressão por Correlação (Event Correlation)**
- Regras lógicas complexas
- Analisa múltiplos eventos em tempo real
- Decisões inteligentes sobre notificações

---

# Supressão por Dependência

<style scoped>
pre { font-size: 0.8em; }
</style>

**Como funciona:**

```
┌────────────────────┐
│   Switch Core      │ ◄─── Problema aqui!
│   (unreachable)    │
└──────────┬─────────┘
           │ Dependência
      ┌────┴────┬─────────┬─────────┐
      ▼         ▼         ▼         ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ Web-01  │ │ Web-02  │ │ App-01  │ │ DB-01   │
│ (down)  │ │ (down)  │ │ (down)  │ │ (down)  │
└─────────┘ └─────────┘ └─────────┘ └─────────┘
   ❌ Suprimido   ❌ Suprimido   ❌ Suprimido
```

---

# Quando Usar Dependência?
**Quando usar:**
- Infraestrutura com dependências claras (rede, storage, DB)
- Arquiteturas hierárquicas (LB → Web → App → DB)
- Serviços compartilhados (DNS, authentication)

---

# Configurando Dependência

<style scoped>
pre { font-size: 0.68em; }
</style>

**Data collection → Hosts → [host] → Triggers → [trigger] → Dependencies**

```yaml
# Exemplo conceitual

Host: servidor-web-01
Trigger: "HTTP service is down"

Dependencies (Add):
  1. Host: switch-core-01
     Trigger: "Network device is unreachable"

  2. Host: firewall-01
     Trigger: "Firewall is not responding"
```

**Resultado:**
- Se switch ou firewall caírem, alerta HTTP é suprimido
- Equipe recebe apenas alerta do switch/firewall (causa raiz)

---

# Supressão por Manutenção

**Maintenance Periods** = Janelas programadas de supressão

**Tipos:**

1. **With data collection**
   - Suprime notificações
   - **Continua coletando dados**
   - Host online com problemas esperados

2. **Without data collection**
   - **Para completamente** a coleta
   - Host estará desligado/offline

---

# Quando Usar Manutenção

| Cenário | Tipo | Duração |
|---------|------|---------|
| Security patches | With data | 2-4h |
| OS updates | With data | 3-6h |
| Hardware replacement | Without data | 1-8h |
| App deployment | With data | 30min-2h |
| Database optimization | With data | 2-4h |
| Network maintenance | With data | 2-3h |
| DR test | With data | 4-8h |
| Ambiente dev (contínuo) | With data | Permanente |

---

# Boas Práticas - Manutenção

<style scoped>
pre { font-size: 0.72em; }
</style>

✅ **Duração apropriada:**
- 2-4 horas para manutenção típica
- Adicionar buffer de 25-50%
- Evitar janelas de 12-24h

✅ **Timing correto:**
- Fora de horário comercial
- Evitar janelas de backup (01:00-03:00)
- Evitar fechamento mensal (dias 28-3)
- Evitar picos de negócio (9-11h, 14-16h)

---

# Boas Práticas - Manutenção (cont.)

✅ **Escopo específico:**
```yaml
# ❌ EVITAR
scope: ALL_HOSTS

# ✅ CORRETO
scope: GROUP_web_servers
hosts: ["web-prod-01", "web-prod-02"]
tags: ["application:web-portal", "environment:production"]
```

---

# Boas Práticas - Manutenção (cont.)

✅ **Notificação prévia:**
- 7 dias antes: stakeholders, management
- 48 horas antes: ops, dev, support teams
- 24 horas antes: todos os usuários afetados
- 1 hora antes: ops-team (confirmação)
- Ao completar: todos previamente notificados

✅ **Exceções críticas:**
- **NUNCA** suprimir eventos de segurança
- **NUNCA** suprimir severity "Disaster"
- Configurar exceções explícitas

---

# Supressão por Correlação

**Event Correlation** = Identificar relacionamentos entre eventos

**Tipos de correlação:**

1. **Correlação Temporal**
   - Eventos próximos no tempo (ex: múltiplos alertas CPU em 5 min)

2. **Correlação por Tags**
   - Eventos com tags relacionadas (ex: mesma aplicação, mesmo datacenter)

---

# Quando Usar Correlação

3. **Correlação por Padrão**
   - Eventos que seguem sequência conhecida (ex: DB slow → App timeout → User complaints)

4. **Correlação por Dependência**
   - Similar ao trigger dependency, mas mais flexível

---

# Quando Usar Correlação

✅ **Quando usar Event Correlation:**

- Ambientes complexos com **>100 hosts**
- Necessidade de agrupar eventos relacionados
- Identificação automática de root cause
- Redução de ruído em arquiteturas distribuídas
- Microserviços e containers (eventos dispersos)

**Exemplo:**
```
10 alertas "CPU alta" no mesmo cluster em 5 minutos
   ↓ Correlação
1 evento agregado "Cluster overload"
```

---

# Tabela de Decisão - Quando Suprimir

<style scoped>
table { font-size: 0.72em; }
</style>

| Cenário | Usar Supressão? | Tipo Recomendado | Observações |
|---------|-----------------|------------------|-------------|
| Manutenção programada | ✅ Sim | Maintenance Period | 2-4h, escopo específico |
| Falha em cascata de rede | ✅ Sim | Dependencies ou Correlation | Suprimir downstream |
| **Evento de segurança** | ❌ **NÃO** | **Nenhum** | **NUNCA suprimir** |
| **Severity "Disaster"** | ❌ **NÃO** | **Nenhum** | **Sempre notificar** |
| Ambiente dev | ✅ Sim | Maintenance | Contínuo |
| Deploy de aplicação | ✅ Sim | Maintenance | Janela conhecida |
| Testes de carga | ✅ Sim | Maintenance | Evitar alertas perf |
| Performance correlacionada | ✅ Sim | Event Correlation | CPU+Mem+Disk |
| Horário comercial crítico | ❌ Não | Nenhum | Visibilidade total |

---

# Impactos da Supressão Mal Configurada

**Problema 1: Over-Suppression (Supressão Excessiva)**

**Sintomas:**
- 🔴 Problemas críticos não são notificados
- 🔴 Incidentes descobertos apenas quando usuários reclamam
- 🔴 Métricas de disponibilidade não refletem realidade

**Exemplo ERRADO:**
```yaml
maintenance_period:
  scope: ALL_HOSTS              # ❌ Muito abrangente!
  duration: 48_HOURS            # ❌ Muito longa!
  type: without_data_collection # ❌ Para tudo!
```

---

# Corrigindo Over-Suppression

<style scoped>
pre { font-size: 0.8em; }
</style>

**Configuração CORRETA:**

```yaml
maintenance_period:
  name: "Web Servers Patching"
  scope: GROUP_web_servers      # ✅ Específico
  duration: 3_HOURS             # ✅ Apropriado
  type: with_data_collection    # ✅ Mantém dados

  exceptions:
    - security_triggers         # ✅ Exceção importante
    - severity: Disaster        # ✅ Sempre notificar
    - tags:
        - "business_critical:true"
```

---
**Como evitar:**
- Escopo específico (hosts, grupos ou tags)
- Duração limitada (2-4h típico)
- Exceções para eventos críticos
- Revisar periodicamente manutenções ativas

---

# Under-Suppression

**Problema 2: Supressão Insuficiente**

**Sintomas:**
- Equipe recebe centenas de alertas para um único problema
- Fadiga de alertas (equipe ignora notificações)
- Tempo desperdiçado triando alertas redundantes

---

**Solução:**
```yaml
# Configurar dependency chain
network_dependencies:
  core_switch:
    trigger: "Network device is unreachable"
    suppresses:
      - all_connected_hosts      # 50 servidores
      - all_services_on_hosts    # 200 serviços
      - all_websites             # 100 websites

# Resultado:
#   1 alerta: Switch core
#   350 alertas suprimidos ✅
```

---

# Timing Incorreto

**Problema 3: Janelas que conflitam com operações críticas**

**Períodos críticos a EVITAR:**

| Período | Quando | Impacto |
|---------|--------|---------|
| Fechamento mensal | Dias 28-3 | VERY HIGH |
| Janelas de backup | 01:00-03:00 | MEDIUM |
| Picos de negócio | 9-11h, 14-16h | HIGH |
| Black Friday | Nov 25 - Dez 2 | VERY HIGH |
| Natal/Ano Novo | Dez 15-31 | VERY HIGH |

---

# Checklist - Planejamento de Manutenção

<style scoped>
ul { font-size: 0.9em; }
</style>

Antes de criar uma janela de manutenção, verificar:

- [ ] Não conflita com horário comercial crítico
- [ ] Não conflita com janela de backup
- [ ] Não conflita com fechamento mensal
- [ ] Não conflita com eventos de negócio (Black Friday, etc)
- [ ] Equipe foi notificada com 24-48h de antecedência
- [ ] Plano de rollback está definido
- [ ] Duração é realista (inclui margem de segurança 25-50%)
- [ ] Escopo está claramente definido
- [ ] Exceções para eventos críticos estão configuradas
- [ ] Aprovação formal obtida (ticket/change request)

---

<!-- _class: lead -->

# PARTE 2
## Event Correlation - Fundamentos

---

# O Que É Event Correlation?

**Event Correlation** = Identificar relacionamentos entre eventos

**Analogia de trânsito:**
- Um semáforo quebrado → Congestionamento em 1 rua
- Vários semáforos quebrados na mesma avenida → Problema na central de controle
- Correlação identifica que não são 5 problemas, mas 1 só (central)

---

# Event Correlation

**No Zabbix permite:**
- **Agrupar eventos relacionados**: 10 alertas CPU → 1 evento "Cluster overload"
- **Identificar root cause**: DB slow + App timeout + User complaints → "DB performance issue"
- **Reduzir ruído**: Falha de rede + 50 hosts down → Alertar apenas rede
- **Ações context-aware**: Diferentes ações baseadas no padrão

---

# Impacto Mensurável

<style scoped>
table { font-size: 0.6em; }
</style>

**Comparação: Com vs Sem Correlação**

| Métrica | Sem Correlação | Com Correlação | Melhoria |
|---------|----------------|----------------|----------|
| Alertas por dia | 200-300 | 40-60 | **-75%** |
| Tempo p/ root cause | 15-30 min | 2-5 min | **-80%** |
| Falsos positivos | 30-40% | 5-10% | **-75%** |
| Satisfação equipe | Baixa | Alta | ↑↑↑ |
| MTTR (Mean Time To Repair) | 45 min | 20 min | **-55%** |

**ROI:** Ambiente com 500 hosts economiza:
- 2-3 horas/dia de trabalho operacional
- 10-15 horas/mês de análise de incidentes
- Redução de 60-80% em notificações desnecessárias

---

# Correlação Temporal

**Eventos próximos no tempo são frequentemente relacionados**

**Janelas temporais recomendadas:**

| Tipo de Problema | Janela | Razão |
|------------------|--------|-------|
| Rede | 2-10 min | Falhas propagam rapidamente |
| Performance (CPU/Mem) | 5-15 min | Degradação gradual |
| Segurança | 30-60 min | Ataques coordenados espaçados |
| Aplicações | 10-20 min | Dependências entre serviços |

---

**Exemplo:**
```
5 servidores com CPU > 90% dentro de 5 minutos
  ↓ Correlação temporal
Provável causa comum: Carga de trabalho, DDoS, job agendado
```

---

# Correlação por Tags

<style scoped>
pre { font-size: 0.7em; }
</style>

**Tags permitem agrupar eventos relacionados**

**Taxonomia de tags úteis:**

```yaml
tags:
  component: [cpu, memory, disk, network, application]
  location: [datacenter-sp, datacenter-rj, aws-us-east]
  environment: [production, staging, development]
  tier: [frontend, backend, database, cache]
  application: [api-auth, api-payment, web-portal]
  severity: [low, medium, high, disaster]
  business_unit: [sales, finance, operations]
  criticality: [critical, high, medium, low]
```

---

# Correlação por Tags (cont.)

**Exemplo de regra:**
```yaml
correlation_rule:
  name: "Backend Performance Correlation"
  conditions:
    - new_event_tag: "tier" equals "backend"
    - new_event_tag: "component" equals "cpu"
    - time_window: 10_minutes
  action: create_composite_event
```

---

# Correlação por Padrões

**Padrões comuns de problemas:**

<style scoped>
table { font-size: 0.72em; }
</style>

| Padrão | Sequência de Eventos | Root Cause |
|--------|---------------------|------------|
| Database Cascade | DB slow → App timeout → HTTP 500 | Database performance |
| Network Failure | Switch down → Hosts unreachable → Services unavailable | Network infrastructure |
| Resource Exhaustion | Disk 80% → 90% → 95% → App crash | Disk space management |
| Memory Leak | Memory 60% → 80% → 95% → OOM killer | Application memory leak |
| DDoS Attack | Traffic spike → CPU high → Connection refused | Network attack |

**Benefício:** Identificação automática de causa raiz

---

# Exemplo de Padrão - Database Cascade

<style scoped>
pre { font-size: 0.58em; }
</style>

```yaml
correlation_pattern:
  name: "Database Performance Cascade"

  pattern_sequence:
    - event: "Database query time > 5s"
      max_age: 5min

    - event: "Application response time > 10s"
      max_age: 3min

    - event: "HTTP 500 errors increasing"
      max_age: 2min

  confidence_threshold: 80%

  actions:
    - suppress_downstream_events: true
    - create_incident:
        severity: high
        assigned_to: database-team
        title: "Database Performance Cascade Detected"
    - run_diagnostic_script: "/usr/local/bin/diagnose_db_performance.sh"
    - notify_escalation:
        level: 2
        delay: 10min
```

---

# Configurando Event Correlation

**Caminho no Zabbix 7.0:**

```
Data collection → Event correlation → Create event correlation
```

**⚠️ Importante:** Event Correlation compara eventos EXISTENTES (old) com NOVOS (new)

---

# Passo 1: Informações Básicas

```
Name: Suppress Hosts When Switch Fails
Enabled: (checked)
Description: Fecha eventos de hosts quando switch core está down
```

**Name:** Nome descritivo da regra
**Enabled:** Ativar/desativar regra

---

# Passo 2: Conditions (Condições)

<style scoped>
table { font-size: 0.84em; }
</style>

**Tipos de condição disponíveis:**

| Type | Descrição | Quando Usar |
|------|-----------|-------------|
| **Old event tag** | Tag do evento JÁ existente | Comparar com eventos anteriores |
| **New event tag** | Tag do evento NOVO que chegou | Filtrar novos eventos |
| **New event host group** | Grupo do host do novo evento | Correlacionar por localização |
| **Event tag pair** | Par de tags entre old/new | Relacionar eventos por tags iguais |
| **Old event tag value** | Valor específico de tag antiga | Comparação avançada |
| **New event tag value** | Valor específico de tag nova | Comparação avançada |

---

# Operador: AND vs OR vs Custom

**Type of calculation:**

```
AND: TODAS as condições devem ser verdadeiras
OR:  QUALQUER condição verdadeira já basta
And/Or: Combinar (A AND B) OR C
Custom expression: Fórmula customizada
```

**Recomendado:** Começar com AND (mais restritivo)

---

# Exemplo Prático 1: Tags Simples

**Cenário:** Suprimir hosts quando switch core falha

**Pré-requisito - Configurar tags nas triggers:**

```
Trigger do Switch:
  Name: Switch Core is unreachable
  Tags:
    device: switch-core-01
    component: network

Trigger dos Hosts:
  Name: Host is unreachable
  Tags:
    upstream: switch-core-01
    component: host
```

---

# Exemplo Prático 1: Correlation Rule

<style scoped>
pre { font-size: 0.68em; }
</style>

```
Data collection → Event correlation → Create

Name: Suppress hosts when switch fails

Conditions (Type of calculation: AND):

  Condition A:
    Type: Old event tag
    Tag: device
    Operator: equals
    Value: switch-core-01

  Condition B:
    Type: New event tag
    Tag: upstream
    Operator: equals
    Value: switch-core-01

Operations:
  [x] Close new event
```

---

# Entendendo o Fluxo

<style scoped>
pre { font-size: 0.7em; }
</style>

```
1. Trigger do Switch dispara (OLD EVENT)
   Tag: device=switch-core-01
   Status: PROBLEM

2. Trigger do Host dispara (NEW EVENT)
   Tag: upstream=switch-core-01
   Status: PROBLEM tentando abrir

3. Event Correlation avalia:
   ✅ Old event tag "device" = "switch-core-01"? SIM
   ✅ New event tag "upstream" = "switch-core-01"? SIM
   ✅ Condições AND satisfeitas? SIM

4. Operation executada:
   → Close new event (host)

5. Resultado:
   ✅ Switch event: ABERTO (notifica equipe)
   ❌ Host event: FECHADO automaticamente (suprimido)
```

---

# Operations: Close Old vs Close New

**Close new event:**
- Evento NOVO é redundante/consequência
- Mantém evento ANTIGO (root cause)
- **Uso:** Cascata de problemas (switch → hosts)

**Close old events:**
- Evento NOVO é mais importante
- Fecha evento ANTIGO (foi resolvido/atualizado)
- **Uso:** Atualização de status

---

**Ambos marcados:**
- Fecha OLD e NEW
- Útil para consolidação

---

# Exemplo Prático 2: Event Tag Pair

**Cenário:** Fechar eventos duplicados da mesma porta

**Tags nas triggers:**

```
Trigger:
  Name: Network port {#PORT} is down
  Tags:
    host: {HOST.NAME}
    port: {#PORT}
```

---

**Correlation rule:**

```
Name: Close duplicate port events

Conditions (Type: AND):
  Condition A:
    Type: Event tag pair
    Old tag: host
    New tag: host

  Condition B:
    Type: Event tag pair
    Old tag: port
    New tag: port

Operations:
  [x] Close new event
```

**Lógica:** Se novo evento tem MESMAS tags (host + port) → Fechar duplicata

---

# Boas Práticas - Event Correlation

**1. Evolução Gradual:**

```
Fase 1 (Semana 1-2):
  - 2-3 correlações básicas
  - Network failures, cascading services

Fase 2 (Semana 3-4):
  - Correlações temporais
  - Performance patterns

Fase 3 (Mês 2):
  - Padrões específicos do ambiente
  - Aplicações críticas

Fase 4 (Mês 3+):
  - Otimização e refinamento
  - Machine Learning (futuro)
```

---

# Boas Práticas (cont.)

**2. Taxonomia de Tags Consistente:**

```yaml
# Tags obrigatórias em TODOS os triggers
required_tags:
  - component: [cpu, memory, disk, network, app]
  - environment: [production, staging, dev]
  - tier: [frontend, backend, database]

# Tags opcionais
optional_tags:
  - location, business_unit, criticality, owner
```

---

# Boas Práticas (cont.)

**3. Limitar Número de Correlações:**
- Máximo **15-20 correlações** ativas
- Performance do Zabbix Server degradada com >30
- Priorizar correlações com maior impacto

---

# Boas Práticas (cont.)

**4. Monitorar Eficácia:**

```yaml
metrics_to_track:
  - reduction_rate: "> 60%"
    # (Alertas antes - Alertas depois) / Alertas antes

  - false_positive_rate: "< 5%"
    # Eventos suprimidos incorretamente

  - time_to_root_cause: "< 5 minutos"
    # Tempo para identificar causa raiz

  - alert_fatigue_index: "< 20 alertas/operador/dia"
    # Carga por operador
```

---

# Boas Práticas (cont.)

**5. Documentar Cada Regra:**
- Purpose, Trigger conditions, Action taken
- Justification, Expected reduction, Owner
- Review frequency (trimestral)

---

<!-- _class: lead -->

# PARTE 3
## Supressão Durante Manutenção Programada

---

# Planejamento de Janelas de Manutenção

**4 Dimensões Críticas:**

1. **Timing** - Quando executar
2. **Duração** - Quanto tempo
3. **Escopo** - O que será afetado
4. **Comunicação** - Quem notificar

---

**Objetivo:**
- Minimizar impacto no negócio
- Evitar conflitos com operações críticas
- Transparência para stakeholders

---

# Timing - Quando Executar

**Horários recomendados:**

```yaml
✅ IDEAL:
  days: [Saturday, Sunday]
  hours: [02:00-06:00]
  reasoning: "Mínimo impacto, baixo uso"

✅ ACEITÁVEL:
  days: [Tuesday, Wednesday, Thursday]
  hours: [22:00-02:00]
  reasoning: "Baixo uso, evita início/fim de semana"

❌ EVITAR:
  days: [Monday, Friday]
  hours: [06:00-22:00]
  reasoning: "Alto impacto, picos de uso"
```

---

# Conflitos a Evitar

**Períodos críticos:**

| Período | Quando | Razão |
|---------|--------|-------|
| Janelas de backup | 01:00-03:00 | Sobrecarga I/O |
| Fechamento mensal | Dias 28-3 | Processos contábeis |
| Horário de pico | 10-11h, 14-16h | Alto uso |
| Black Friday | Nov 25 - Dez 2 | Evento crítico |
| Natal/Ano Novo | Dez 15-31 | Evento crítico |
| Início/Fim trimestre | Últimos 3 dias | Relatórios |

**Checklist:** Validar com calendário de negócio antes de agendar

---

# Duração - Quanto Tempo

**Regra de buffer:**

```yaml
best_practice:
  rule: "Adicionar 25-50% buffer"

  example:
    work_planned: "2 hours"
    buffer: "+1 hour"
    total_window: "3 hours"

  reasoning:
    - Problemas inesperados
    - Rollback se necessário
    - Validação pós-manutenção
    - Margem de segurança
```

---

# Duração - Quanto Tempo (cont.)


**Duração máxima recomendada:**
- Manutenção típica: 4 horas
- Manutenção complexa: 8 horas
- Evitar: >12 horas (risco de over-suppression)

---

# Escopo - O Que Será Afetado

<style scoped>
pre { font-size: 0.65em; }
</style>

```yaml
# ❌ Muito amplo - EVITAR
bad_scope:
  hosts: "ALL"
  impact: "TODO o monitoramento suprimido!"

# ✅ Específico por Host Groups
good_scope_1:
  host_groups: ["Web Servers - Production"]
  impact: "Apenas web servers"

# ✅ Específico por Hosts
good_scope_2:
  hosts: ["web-prod-01", "web-prod-02", "web-prod-03"]
  impact: "3 hosts específicos"

# ✅ Específico por Tags (mais flexível)
good_scope_3:
  tags:
    - "application:web-portal"
    - "environment:production"
    - "datacenter:sp"
  impact: "Hosts que combinam todas as tags"
```

---

# Comunicação - Timeline

<style scoped>
table { font-size: 0.8em; }
</style>

**Quem notificar e quando:**

| Quando | Quem | Conteúdo |
|--------|------|----------|
| **7 dias antes** | Stakeholders, Management | Aviso formal, aprovação |
| **48 horas antes** | Ops, Dev, Support teams | Detalhes técnicos, preparação |
| **24 horas antes** | Todos os usuários afetados | Aviso de downtime esperado |
| **1 hora antes** | Ops-team | Confirmação final, go/no-go |
| **Início** | Ops-team | Manutenção iniciada |
| **Fim** | Todos previamente notificados | Conclusão, status |

---

**Template de comunicação:**
- O que será feito, quando, duração esperada
- Sistemas afetados, impacto esperado
- Contato para emergências

---

# Criando Maintenance Period - GUI

**Data collection → Maintenance → Create maintenance period**

**Passo 1: Informações Básicas**

**Name:** `[Scope] - [Type] - [Date]`
- Exemplo: `WebServers-Prod - Security Patching - 2025-02-10`

**Description:** Incluir informações completas
- **Purpose:** Security patches (CVE-2025-xxxx)
- **Expected downtime:** 3 hours
- **Systems affected:** web-prod-01, web-prod-02, web-prod-03
- **Impact:** Web portal may be temporarily unavailable

---

- **Rollback plan:** Rollback snapshots available
- **Contact:** ops-team@empresa.com
- **Approval:** CHG-2025-001234

---

# Criando Maintenance Period (cont.)

**Passo 2: Tipo de Manutenção**

**Maintenance type:**

● **With data collection**
  - ✅ Host online, problemas esperados
  - ✅ Mantém histórico de dados
  - ✅ Usar para: Patches, updates, restarts

○ **Without data collection**
  - ✅ Host completamente offline
  - ✅ Economiza recursos do Zabbix
  - ✅ Usar para: Hardware replacement, host desligado

---

# Criando Maintenance Period (cont.)

**Passo 3: Definir Período**

**Opção 1: One time only (uma vez)**
- **Active since:** 2025-02-10 02:00:00
- **Active till:** 2025-02-10 05:00:00 (3 horas)

**Opção 2: Daily (diário)**
- **Every N days:** 1
- **Start time:** 02:00
- **Period:** 3h

---

**Opção 3: Weekly (semanal)**
- **Days:** Saturday
- **Start time:** 02:00
- **Period:** 4h

**Opção 4: Monthly (mensal)**
- **Day of month:** 1st Saturday (primeiro sábado)
- **Start time:** 02:00
- **Period:** 4h

---

# Criando Maintenance Period (cont.)

**Passo 4: Definir Escopo (Hosts and groups tab)**

**Método 1: Por Host Groups**
- Click em **Add** (Host groups)
- Selecionar: `Web Servers - Production`

**Método 2: Por Hosts Específicos**
- Click em **Add** (Hosts)
- Selecionar: `web-prod-01`, `web-prod-02`, `web-prod-03`

---

**Método 3: Por Tags** (mais flexível ✅)
- **Tag name:** `application`
  **Operator:** `equals`
  **Tag value:** `web-portal`
- Click **AND**
- **Tag name:** `environment`
  **Operator:** `equals`
  **Tag value:** `production`

**Dica:** Tags são mais flexíveis (hosts adicionados automaticamente)

---

# Validação Pós-Manutenção

**Checklist após completar manutenção:**

- [ ] ✅ **Verificar serviços online**
  ```bash
  systemctl status apache2 mysql
  ```

- [ ] ✅ **Testar conectividade**
  ```bash
  curl -I https://portal.empresa.com
  ```

- [ ] ✅ **Verificar logs do Zabbix**
  ```bash
  tail -100 /var/log/zabbix/zabbix_agentd.log
  ```

---

- [ ] ✅ **Confirmar métricas normais** (Dashboard do Zabbix)

- [ ] ✅ **Encerrar maintenance period** (se não foi automático)

- [ ] ✅ **Notificar conclusão** (email para stakeholders)

---

# Post-Mortem - Documentação

**Após cada manutenção, documentar:**

**Planejado vs Real:**
- Duração planejada: 3h
- Duração real: 2h 45min ✅

**Issues encontrados:**
- Web-prod-02 não reiniciou automaticamente
- Necessário restart manual do serviço

---

**Resoluções aplicadas:**
- Ajustado systemd service para auto-restart

**Action items:**
- [ ] Criar script de validação pré-manutenção
- [ ] Atualizar runbook com problema encontrado

**Lições aprendidas:**
- Buffer de 1h foi suficiente
- Horário 02:00 adequado (zero usuários online)

---

<!-- _class: lead -->

# PARTE 4
## Laboratórios Práticos

---

# 🔬 Laboratório Prático 1

**Objetivo:** Configurar Event Correlation via GUI

**Tempo:** 20 minutos

**Cenário:**
- Switch core: `switch-core-01`
- 02 servidores web conectados: `web-prod-01` a `web-prod-02`
- Problema: Switch fica offline → 02 alertas (switch + 02 servidores)
- Meta: Apenas 1 alerta (switch) deve ser enviado

---

**Resultado esperado:**
- Switch unreachable → ✅ Notificado
- 02 servidores unreachable → ❌ Suprimidos

---

# Lab 1 - Passo 1: Preparação

**1. Verificar tags nos triggers:**

```
Data collection → Hosts → switch-core-01 → Triggers
  → "Network device is unreachable"
  → Tags: Adicionar tag "component:network-switch"

Data collection → Hosts → web-prod-XX → Triggers
  → "Host is unreachable"
  → Tags: Adicionar tag "component:host"
```

**2. Verificar host groups:**
```
Data collection → Host groups
  → Verificar grupo: "Web Servers - Production"
  → Members: web-prod-01 até web-prod-02
```

---

# Lab 1 - Passo 2: Criar Correlação

<style scoped>
pre { font-size: 0.7em; }
</style>

**Administration → Event correlation → Create correlation**

```yaml
Name: Suppress Hosts When Switch Fails
Description: Suprime hosts quando switch core fica offline

Conditions (type: AND):
  1. Condition type: Old event tag
     Tag: component
     Operator: equals
     Value: network-switch

  2. Condition type: New event tag
     Tag: component
     Operator: equals
     Value: host

  3. Condition type: New event host group
     Host group: Web Servers - Production
     Operator: equals
```

---

# Lab 1 - Passo 3: Configurar Operations

```yaml
Operations:
  ☑ Close new event
    - Eventos de hosts serão fechados (suprimidos)
    - Evento do switch permanece ativo

  ☐ Close old events
    - Não marcar (queremos manter alerta do switch)
```

**Click: Add**

**Status: Enabled ✅**

---

# Lab 1 - Passo 4: Validação

**Simular falha do switch:**

```bash
# No Zabbix Server, desabilitar switch temporariamente
# Data collection → Hosts → switch-core-01
# Status: Disabled (aguardar 2-3 minutos)
```

---

**Verificar resultado:**

```
Monitoring → Problems

Esperado:
  ✅ 1 problema: switch-core-01 - Network device is unreachable
  ❌ 0 problemas: web-prod-XX (suprimidos por correlação!)
```

**Reabilitar switch:**
```
Data collection → Hosts → switch-core-01 → Status: Enabled
```

---

<!-- _class: lead -->

# PARTE 5
## Troubleshooting e Métricas

---

# Troubleshooting - Correlação Não Funciona

**Sintomas:** Eventos ainda sendo notificados mesmo com correlação

**Diagnóstico:**

1. **Verificar se correlação está habilitada:**
   ```
   Administration → Event correlation → [sua correlação]
   Status: Enabled? ✅
   ```

2. **Verificar logs do Zabbix Server:**
   ```bash
   tail -100 /var/log/zabbix/zabbix_server.log | grep -i correlation
   ```

---

3. **Validar conditions (case-sensitive!):**
   ```yaml
   # ❌ ERRADO
   Tag: Component  (C maiúsculo)
   Value: Network-Switch  (N e S maiúsculos)

   # ✅ CORRETO
   Tag: component  (tudo minúsculo)
   Value: network-switch  (tudo minúsculo, traço)
   ```

---

# Troubleshooting (cont.)

**Soluções:**

1. **Corrigir grafia de tags:**
   - Padronizar: tudo minúsculo, traços ao invés de espaços
   - `component:network-switch` não `Component:Network Switch`

2. **Ajustar janela temporal:**
   ```yaml
   # Se eventos estão espaçados por 15 min
   time_window: 900  # 15 minutos (não 300/5min)
   ```

---

3. **Simplificar conditions:**
   - Começar com 2-3 conditions simples
   - Adicionar complexidade gradualmente

4. **Verificar tabela event_suppress no DB:**
   ```sql
   SELECT * FROM event_suppress
   WHERE suppress_until > UNIX_TIMESTAMP(NOW())
   LIMIT 10;
   ```

---
# Métricas de Sucesso

**Operacionais:**

| Métrica | Baseline | Meta | Como Medir |
|---------|----------|------|------------|
| Alertas/operador/dia | 150-200 | 30-50 | Query SQL events/day |
| Time to root cause | 15-30 min | 2-5 min | Tempo médio de análise |
| False positive rate | N/A | < 5% | Eventos incorretamente suprimidos |
| Noise reduction rate | N/A | > 60% | (Antes - Depois) / Antes |
| MTTR | 45 min | 20 min | Tempo médio de resolução |
| Incident escalations | 20-30/mês | 5-10/mês | Tickets escalados |
| Team satisfaction | N/A | > 8/10 | Survey trimestral |

---
# Dashboard de Eficácia

**Criar dashboard para acompanhar métricas:**

```yaml
Dashboard: Correlation & Suppression Effectiveness

Widgets:
  1. Graph: Events per day (before/after correlation)
  2. Graph: Suppression rate over time
  3. Plain text: Current noise reduction rate (> 60%?)
  4. Plain text: False positive rate (< 5%?)
  5. Top hosts: Most affected by correlation
  6. Problems: Critical events (never suppressed)
  7. Graph: MTTR trend
  8. Plain text: Alerts per operator per day
```

**Revisar mensalmente e ajustar correlações conforme necessário**

---
# Recursos Adicionais

**Documentação Oficial:**
- [Event Correlation](https://www.zabbix.com/documentation/current/en/manual/config/event_correlation)
- [Maintenance Periods](https://www.zabbix.com/documentation/current/en/manual/maintenance)
- [Trigger Dependencies](https://www.zabbix.com/documentation/current/en/manual/config/triggers/dependencies)

**Blog Posts:**
- "Reducing Alert Fatigue with Zabbix Event Correlation"
- "Best Practices for Maintenance Windows"

**Comunidade:**
- Zabbix Forums: https://www.zabbix.com/forum
- Zabbix Share: https://share.zabbix.com

---

<!-- _class: lead -->

# Perguntas?

**Dúvidas sobre:**
- Supressão de eventos
- Event Correlation
- Maintenance Periods
- Troubleshooting

---

<!-- _class: lead -->

# Obrigado!

### Até a próxima aula! 🚀
