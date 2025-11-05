#!/bin/bash
echo "🐳 Configurando Laboratório SNMP Docker..."
echo ""

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado! Por favor, instale o Docker primeiro."
    echo "   https://docs.docker.com/engine/install/"
    exit 1
fi

# Verificar se Docker Compose está disponível
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose não encontrado!"
    exit 1
fi

# Carregar imagem
if [ -f "lab-snmp-image.tar.gz" ]; then
    echo "📦 Carregando imagem Docker..."
    gunzip -c lab-snmp-image.tar.gz | docker load
    echo "✅ Imagem carregada com sucesso!"
else
    echo "❌ Arquivo lab-snmp-image.tar.gz não encontrado!"
    exit 1
fi

# Iniciar containers
echo ""
echo "🚀 Iniciando containers..."
docker compose up -d

# Aguardar containers ficarem prontos
echo ""
echo "⏳ Aguardando containers ficarem prontos (30s)..."
sleep 30

# Verificar status
echo ""
echo "📊 Status dos containers:"
docker compose ps

# Testar SNMP
echo ""
echo "🔍 Testando conectividade SNMP..."
comando_snmp="snmpget"

# Verificar se snmpget está instalado
if ! command -v snmpget &> /dev/null; then
    echo "⚠️  Comando snmpget não encontrado. Instale: sudo apt-get install snmp"
    echo ""
    echo "✅ Containers iniciados com sucesso!"
    echo "   Use 'docker compose ps' para verificar status"
    exit 0
fi

# Testar cada container
sucesso=0
falhas=0
for port in {10161..10167}; do
    result=$(snmpget -v2c -c public -Ln -t 2 localhost:$port SNMPv2-MIB::sysName.0 2>/dev/null | grep STRING)
    if [ ! -z "$result" ]; then
        nome=$(echo "$result" | awk -F'"' '{print $2}')
        echo "✅ Porta $port: $nome"
        sucesso=$((sucesso + 1))
    else
        echo "❌ Porta $port: Não respondeu"
        falhas=$((falhas + 1))
    fi
done

echo ""
echo "📈 Resultado: $sucesso containers respondendo, $falhas falhas"

if [ $falhas -eq 0 ]; then
    echo "🎉 Setup completo! Todos os containers estão funcionando perfeitamente!"
else
    echo "⚠️  Alguns containers não responderam. Aguarde mais alguns segundos e tente:"
    echo "   docker compose ps"
fi

echo ""
echo "💡 Comandos úteis:"
echo "   docker compose ps       - Ver status"
echo "   docker compose logs     - Ver logs"
echo "   docker compose down     - Parar tudo"
echo "   docker compose restart  - Reiniciar"
