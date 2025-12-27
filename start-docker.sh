#!/bin/bash
# =============================================================================
# SCRIPT DE INICIALIZAÇÃO - Sistema de Regulação SES-GO (Docker)
# =============================================================================

set -e

echo "=============================================="
echo "  SISTEMA DE REGULAÇÃO SES-GO - DOCKER"
echo "=============================================="

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado!"
    echo "   Instale em: https://docs.docker.com/get-docker/"
    exit 1
fi

# Verificar se Docker Compose está disponível
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose não está disponível!"
    exit 1
fi

echo "✅ Docker encontrado"

# Opções
case "$1" in
    "up"|"start")
        echo ""
        echo "🚀 Iniciando todos os serviços..."
        echo "   (Primeira execução pode demorar ~10min para baixar imagens e modelos)"
        echo ""
        docker compose -f docker-compose.full.yml up -d
        
        echo ""
        echo "⏳ Aguardando serviços iniciarem..."
        sleep 10
        
        echo ""
        echo "📊 Status dos serviços:"
        docker compose -f docker-compose.full.yml ps
        
        echo ""
        echo "=============================================="
        echo "  ✅ SISTEMA INICIADO!"
        echo "=============================================="
        echo ""
        echo "  🌐 Frontend:    http://localhost:8082"
        echo "  🔧 Backend API: http://localhost:8000"
        echo "  📚 API Docs:    http://localhost:8000/docs"
        echo "  🤖 Ollama:      http://localhost:11434"
        echo "  🗄️  PostgreSQL: localhost:5432"
        echo ""
        echo "  📋 Ver logs:    docker compose -f docker-compose.full.yml logs -f"
        echo "  🛑 Parar:       ./start-docker.sh down"
        echo "=============================================="
        ;;
        
    "down"|"stop")
        echo "🛑 Parando todos os serviços..."
        docker compose -f docker-compose.full.yml down
        echo "✅ Serviços parados"
        ;;
        
    "logs")
        docker compose -f docker-compose.full.yml logs -f
        ;;
        
    "status"|"ps")
        docker compose -f docker-compose.full.yml ps
        ;;
        
    "rebuild")
        echo "🔄 Reconstruindo imagens..."
        docker compose -f docker-compose.full.yml build --no-cache
        echo "✅ Imagens reconstruídas"
        ;;
        
    "clean")
        echo "🧹 Limpando volumes e containers..."
        docker compose -f docker-compose.full.yml down -v
        echo "✅ Limpeza concluída"
        ;;
        
    *)
        echo "Uso: $0 {up|down|logs|status|rebuild|clean}"
        echo ""
        echo "Comandos:"
        echo "  up/start  - Inicia todos os serviços"
        echo "  down/stop - Para todos os serviços"
        echo "  logs      - Mostra logs em tempo real"
        echo "  status/ps - Mostra status dos containers"
        echo "  rebuild   - Reconstrói as imagens"
        echo "  clean     - Remove containers e volumes"
        exit 1
        ;;
esac
