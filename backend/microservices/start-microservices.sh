#!/bin/bash

echo "🚀 INICIANDO ARQUITETURA DE MICROSERVIÇOS - SISTEMA DE REGULAÇÃO SES-GO"
echo "=================================================================="

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Por favor, inicie o Docker primeiro."
    exit 1
fi

# Parar containers existentes se houver
echo "🛑 Parando containers existentes..."
docker-compose -f docker-compose.microservices.yml down

# Construir e iniciar microserviços
echo "🔨 Construindo e iniciando microserviços..."
docker-compose -f docker-compose.microservices.yml up --build -d

# Aguardar inicialização
echo "⏳ Aguardando inicialização dos serviços..."
sleep 10

# Verificar status dos serviços
echo "📊 Verificando status dos microserviços..."
echo ""

# MS-Hospital
echo "🏥 MS-Hospital (Porta 8001):"
curl -s http://localhost:8001/health | jq . 2>/dev/null || echo "  ❌ Não disponível"

# MS-Regulacao
echo "🧠 MS-Regulacao (Porta 8002):"
curl -s http://localhost:8002/health | jq . 2>/dev/null || echo "  ❌ Não disponível"

# MS-Transferencia
echo "🚑 MS-Transferencia (Porta 8003):"
curl -s http://localhost:8003/health | jq . 2>/dev/null || echo "  ❌ Não disponível"

# API Gateway
echo "🌐 API Gateway (Porta 8080):"
curl -s http://localhost:8080/health | jq . 2>/dev/null || echo "  ❌ Não disponível"

echo ""
echo "=================================================================="
echo "✅ MICROSERVIÇOS INICIADOS COM SUCESSO!"
echo ""
echo "📋 ENDPOINTS DISPONÍVEIS:"
echo "  🏥 MS-Hospital:      http://localhost:8001"
echo "  🧠 MS-Regulacao:     http://localhost:8002"
echo "  🚑 MS-Transferencia: http://localhost:8003"
echo "  🌐 API Gateway:      http://localhost:8080"
echo ""
echo "📊 MONITORAMENTO:"
echo "  docker-compose -f docker-compose.microservices.yml logs -f"
echo "  docker-compose -f docker-compose.microservices.yml ps"
echo ""
echo "🛑 PARAR MICROSERVIÇOS:"
echo "  docker-compose -f docker-compose.microservices.yml down"
echo "=================================================================="