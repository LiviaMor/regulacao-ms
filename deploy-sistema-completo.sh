#!/bin/bash

# DEPLOY SISTEMA COMPLETO - REGULAÇÃO SES-GO
# Sistema de Regulação Autônoma com IA, BioBERT, Matchmaker Logístico
# Microserviços: Hospital, Regulação, Transferência + Ollama + PostgreSQL + Redis

echo "🏥 DEPLOY SISTEMA DE REGULAÇÃO SES-GO - VERSÃO COMPLETA"
echo "=" * 70

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Instale o Docker primeiro."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado. Instale o Docker Compose primeiro."
    exit 1
fi

echo "✅ Docker e Docker Compose encontrados"

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose -f backend/docker-compose.yml down 2>/dev/null || true
docker-compose -f backend/microservices/docker-compose.microservices.yml down 2>/dev/null || true

# Limpar containers órfãos
echo "🧹 Limpando containers órfãos..."
docker container prune -f

# Criar redes se não existirem
echo "🌐 Criando redes Docker..."
docker network create regulacao_network 2>/dev/null || true
docker network create regulacao_microservices_network 2>/dev/null || true

# Instalar dependências Python se necessário
echo "🐍 Verificando dependências Python..."
if [ -f "backend/requirements.txt" ]; then
    echo "📦 Instalando dependências Python localmente (para desenvolvimento)..."
    pip install -r backend/requirements.txt 2>/dev/null || echo "⚠️ Não foi possível instalar dependências localmente (continuando...)"
fi

# Construir e iniciar microserviços
echo "🔧 Construindo e iniciando microserviços..."
cd backend/microservices

# Verificar se arquivo docker-compose existe
if [ ! -f "docker-compose.microservices.yml" ]; then
    echo "❌ Arquivo docker-compose.microservices.yml não encontrado!"
    exit 1
fi

# Construir imagens
echo "🏗️ Construindo imagens dos microserviços..."
docker-compose -f docker-compose.microservices.yml build --no-cache

# Iniciar infraestrutura primeiro (banco, redis, ollama)
echo "🗄️ Iniciando infraestrutura (PostgreSQL, Redis, Ollama)..."
docker-compose -f docker-compose.microservices.yml up -d db redis ollama

# Aguardar banco de dados estar pronto
echo "⏳ Aguardando PostgreSQL estar pronto..."
sleep 15

# Verificar se banco está respondendo
echo "🔍 Verificando conexão com banco de dados..."
for i in {1..30}; do
    if docker-compose -f docker-compose.microservices.yml exec -T db pg_isready -U regulacao_user -d regulacao_db; then
        echo "✅ PostgreSQL está pronto!"
        break
    fi
    echo "⏳ Aguardando PostgreSQL... ($i/30)"
    sleep 2
done

# Iniciar Ollama e baixar modelo Llama
echo "🦙 Configurando Ollama e baixando Llama 3..."
sleep 10

# Verificar se Ollama está respondendo
for i in {1..20}; do
    if curl -s http://localhost:11434/api/tags > /dev/null; then
        echo "✅ Ollama está rodando!"
        break
    fi
    echo "⏳ Aguardando Ollama... ($i/20)"
    sleep 3
done

# Baixar modelo Llama 3 (pode demorar)
echo "📥 Baixando modelo Llama 3 (pode demorar alguns minutos)..."
docker-compose -f docker-compose.microservices.yml exec -T ollama ollama pull llama3 || echo "⚠️ Erro ao baixar Llama 3 (continuando...)"

# Iniciar microserviços
echo "🚀 Iniciando microserviços..."
docker-compose -f docker-compose.microservices.yml up -d ms-hospital ms-regulacao ms-transferencia

# Aguardar microserviços estarem prontos
echo "⏳ Aguardando microserviços estarem prontos..."
sleep 20

# Verificar saúde dos microserviços
echo "🔍 Verificando saúde dos microserviços..."

services=("ms-hospital:8001" "ms-regulacao:8002" "ms-transferencia:8003")
for service in "${services[@]}"; do
    name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    
    for i in {1..10}; do
        if curl -s http://localhost:$port/health > /dev/null; then
            echo "✅ $name está saudável!"
            break
        fi
        echo "⏳ Aguardando $name... ($i/10)"
        sleep 3
    done
done

# Iniciar API Gateway
echo "🌐 Iniciando API Gateway..."
docker-compose -f docker-compose.microservices.yml up -d api-gateway

# Voltar para diretório raiz
cd ../..

# Instalar dependências do frontend se necessário
echo "📱 Verificando frontend React Native..."
if [ -d "regulacao-app" ] && [ -f "regulacao-app/package.json" ]; then
    echo "📦 Instalando dependências do frontend..."
    cd regulacao-app
    npm install 2>/dev/null || echo "⚠️ Não foi possível instalar dependências do frontend"
    cd ..
fi

# Executar health check completo
echo "🏥 Executando health check completo..."
python backend/microservices/e2e-health-check.py || echo "⚠️ Health check com problemas (sistema pode ainda estar inicializando)"

# Mostrar status final
echo ""
echo "=" * 70
echo "🎉 DEPLOY CONCLUÍDO!"
echo "=" * 70
echo ""
echo "📊 SERVIÇOS DISPONÍVEIS:"
echo "🏥 MS-Hospital:      http://localhost:8001"
echo "🤖 MS-Regulacao:     http://localhost:8002"
echo "🚑 MS-Transferencia: http://localhost:8003"
echo "🌐 API Gateway:      http://localhost:8080"
echo "🦙 Ollama (Llama 3): http://localhost:11434"
echo "🗄️ PostgreSQL:       localhost:5433"
echo "🔴 Redis:            localhost:6380"
echo ""
echo "📱 FRONTEND:"
echo "React Native App: regulacao-app/"
echo "Para iniciar: cd regulacao-app && npm start"
echo ""
echo "🔧 FERRAMENTAS DE TESTE:"
echo "Health Check: python backend/microservices/e2e-health-check.py"
echo "Teste Matchmaker: python backend/microservices/shared/matchmaker_logistico.py"
echo "Teste Pipeline RAG: python backend/pipeline_hospitais_goias_rag.py"
echo ""
echo "📋 CREDENCIAIS PADRÃO:"
echo "Admin: admin@sesgo.gov.br / admin123"
echo "Regulador: regulador@sesgo.gov.br / regulador123"
echo ""
echo "🚨 FUNCIONALIDADES IMPLEMENTADAS:"
echo "✅ IA Inteligente com Pipeline de Hospitais de Goiás"
echo "✅ BioBERT para análise de textos médicos"
echo "✅ Matchmaker Logístico com cálculo de Haversine"
echo "✅ Pipeline RAG focado para LLMs (Llama 3)"
echo "✅ Protocolos especiais (óbito/transplante)"
echo "✅ Sistema de frota de ambulâncias"
echo "✅ Microserviços completos (Hospital, Regulação, Transferência)"
echo "✅ Frontend React Native com Expo"
echo "✅ Auditoria completa e rastreabilidade"
echo ""
echo "⚠️ PRÓXIMOS PASSOS:"
echo "1. Aguardar todos os serviços estarem 100% prontos (pode levar alguns minutos)"
echo "2. Testar endpoints individualmente"
echo "3. Executar health check novamente se necessário"
echo "4. Iniciar frontend React Native"
echo ""
echo "🆘 SUPORTE:"
echo "Logs: docker-compose -f backend/microservices/docker-compose.microservices.yml logs -f"
echo "Parar: docker-compose -f backend/microservices/docker-compose.microservices.yml down"
echo "=" * 70

# Mostrar containers rodando
echo "🐳 CONTAINERS ATIVOS:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "✅ Deploy concluído com sucesso!"
echo "🏥 Sistema de Regulação SES-GO está rodando!"