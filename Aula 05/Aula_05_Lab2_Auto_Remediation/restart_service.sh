#!/bin/bash
################################################################################
# Script: restart_service.sh
# Descrição: Script de auto-remediation para reinício automático de serviços
# Autor: 4Linux - Curso Zabbix Advanced
# Uso: ./restart_service.sh <nome_do_servico>
################################################################################

SERVICE=$1
LOG=/var/log/zabbix-remediation.log

# Validar parâmetro
if [ -z "$SERVICE" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ ERRO: Serviço não especificado" >> $LOG
    echo "Uso: $0 <nome_do_servico>"
    exit 1
fi

# Whitelist de serviços permitidos (SEGURANÇA)
ALLOWED_SERVICES="apache2 httpd mysql mariadb postgresql ssh sshd nginx redis-server mongodb"

if ! echo "$ALLOWED_SERVICES" | grep -w "$SERVICE" > /dev/null; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ ERRO: Serviço '$SERVICE' não está na whitelist" >> $LOG
    echo "❌ Serviço não permitido. Serviços autorizados: $ALLOWED_SERVICES"
    exit 1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🔄 Iniciando verificação do serviço: $SERVICE" >> $LOG

# Verificar se serviço existe no sistema
if ! systemctl list-unit-files | grep -q "^$SERVICE.service"; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ ERRO: Serviço '$SERVICE' não existe no sistema" >> $LOG
    exit 1
fi

# Verificar se serviço está realmente down
if ! systemctl is-active --quiet $SERVICE; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ Serviço $SERVICE está INATIVO. Tentando reiniciar..." >> $LOG

    # Tentar reiniciar
    systemctl restart $SERVICE

    # Aguardar serviço inicializar
    sleep 5

    # Verificar se subiu com sucesso
    if systemctl is-active --quiet $SERVICE; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ SUCESSO: $SERVICE reiniciado com sucesso" >> $LOG
        echo "✅ Serviço $SERVICE reiniciado com sucesso"
        exit 0
    else
        # Capturar status detalhado do erro
        STATUS=$(systemctl status $SERVICE 2>&1 | head -10)
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ FALHA: Não foi possível reiniciar $SERVICE" >> $LOG
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Status: $STATUS" >> $LOG
        echo "❌ Falha ao reiniciar $SERVICE. Verifique os logs do sistema."
        exit 1
    fi
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ℹ️ INFO: Serviço $SERVICE já está ATIVO" >> $LOG
    echo "ℹ️ Serviço $SERVICE já está rodando"
    exit 0
fi
