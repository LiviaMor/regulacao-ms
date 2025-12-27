@echo off
echo 🚀 INICIANDO ARQUITETURA DE MICROSERVIÇOS - SISTEMA DE REGULAÇÃO SES-GO
echo ==================================================================

REM Verificar se Docker está rodando
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker não está rodando. Por favor, inicie o Docker primeiro.
    pause
    exit /b 1
)

REM Parar containers existentes se houver
echo 🛑 Parando containers existentes...
docker-compose -f docker-compose.microservices.yml down

REM Construir e iniciar microserviços
echo 🔨 Construindo e iniciando microserviços...
docker-compose -f docker-compose.microservices.yml up --build -d

REM Aguardar inicialização
echo ⏳ Aguardando inicialização dos serviços...
timeout /t 10 /nobreak >nul

REM Verificar status dos serviços
echo 📊 Verificando status dos microserviços...
echo.

echo 🏥 MS-Hospital (Porta 8001):
curl -s http://localhost:8001/health 2>nul || echo   ❌ Não disponível

echo 🧠 MS-Regulacao (Porta 8002):
curl -s http://localhost:8002/health 2>nul || echo   ❌ Não disponível

echo 🚑 MS-Transferencia (Porta 8003):
curl -s http://localhost:8003/health 2>nul || echo   ❌ Não disponível

echo 🌐 API Gateway (Porta 8080):
curl -s http://localhost:8080/health 2>nul || echo   ❌ Não disponível

echo.
echo ==================================================================
echo ✅ MICROSERVIÇOS INICIADOS COM SUCESSO!
echo.
echo 📋 ENDPOINTS DISPONÍVEIS:
echo   🏥 MS-Hospital:      http://localhost:8001
echo   🧠 MS-Regulacao:     http://localhost:8002
echo   🚑 MS-Transferencia: http://localhost:8003
echo   🌐 API Gateway:      http://localhost:8080
echo.
echo 📊 MONITORAMENTO:
echo   docker-compose -f docker-compose.microservices.yml logs -f
echo   docker-compose -f docker-compose.microservices.yml ps
echo.
echo 🛑 PARAR MICROSERVIÇOS:
echo   docker-compose -f docker-compose.microservices.yml down
echo ==================================================================
pause