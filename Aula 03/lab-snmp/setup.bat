@echo off
chcp 65001 > nul
echo 🐳 Configurando Laboratório SNMP Docker...
echo.

REM Verificar Docker
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker não encontrado! Por favor, instale o Docker Desktop.
    echo    https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Carregar imagem
if exist lab-snmp-image.tar.gz (
    echo 📦 Carregando imagem Docker...
    docker load -i lab-snmp-image.tar.gz
    echo ✅ Imagem carregada com sucesso!
) else (
    echo ❌ Arquivo lab-snmp-image.tar.gz não encontrado!
    pause
    exit /b 1
)

REM Iniciar containers
echo.
echo 🚀 Iniciando containers...
docker compose up -d

REM Aguardar
echo.
echo ⏳ Aguardando containers ficarem prontos (30s)...
timeout /t 30 /nobreak > nul

REM Verificar status
echo.
echo 📊 Status dos containers:
docker compose ps

echo.
echo 🎉 Setup completo!
echo.
echo 💡 Comandos úteis:
echo    docker compose ps       - Ver status
echo    docker compose logs     - Ver logs
echo    docker compose down     - Parar tudo
echo    docker compose restart  - Reiniciar
echo.
pause
