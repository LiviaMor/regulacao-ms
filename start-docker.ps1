# =============================================================================
# SCRIPT DE INICIALIZAÇÃO - Sistema de Regulação SES-GO (Docker) - Windows
# =============================================================================

param(
    [Parameter(Position=0)]
    [ValidateSet("up", "start", "down", "stop", "logs", "status", "ps", "rebuild", "clean")]
    [string]$Command = "up"
)

Write-Host "=============================================="
Write-Host "  SISTEMA DE REGULAÇÃO SES-GO - DOCKER"
Write-Host "=============================================="

# Verificar se Docker está instalado
try {
    docker --version | Out-Null
    Write-Host "✅ Docker encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker não está instalado!" -ForegroundColor Red
    Write-Host "   Instale em: https://docs.docker.com/get-docker/"
    exit 1
}

switch ($Command) {
    { $_ -in "up", "start" } {
        Write-Host ""
        Write-Host "🚀 Iniciando todos os serviços..." -ForegroundColor Cyan
        Write-Host "   (Primeira execução pode demorar ~10min para baixar imagens e modelos)"
        Write-Host ""
        
        docker compose -f docker-compose.full.yml up -d
        
        Write-Host ""
        Write-Host "⏳ Aguardando serviços iniciarem..."
        Start-Sleep -Seconds 10
        
        Write-Host ""
        Write-Host "📊 Status dos serviços:"
        docker compose -f docker-compose.full.yml ps
        
        Write-Host ""
        Write-Host "=============================================="
        Write-Host "  ✅ SISTEMA INICIADO!" -ForegroundColor Green
        Write-Host "=============================================="
        Write-Host ""
        Write-Host "  🌐 Frontend:    http://localhost:8082"
        Write-Host "  🔧 Backend API: http://localhost:8000"
        Write-Host "  📚 API Docs:    http://localhost:8000/docs"
        Write-Host "  🤖 Ollama:      http://localhost:11434"
        Write-Host "  🗄️  PostgreSQL: localhost:5432"
        Write-Host ""
        Write-Host "  📋 Ver logs:    .\start-docker.ps1 logs"
        Write-Host "  🛑 Parar:       .\start-docker.ps1 down"
        Write-Host "=============================================="
    }
    
    { $_ -in "down", "stop" } {
        Write-Host "🛑 Parando todos os serviços..." -ForegroundColor Yellow
        docker compose -f docker-compose.full.yml down
        Write-Host "✅ Serviços parados" -ForegroundColor Green
    }
    
    "logs" {
        docker compose -f docker-compose.full.yml logs -f
    }
    
    { $_ -in "status", "ps" } {
        docker compose -f docker-compose.full.yml ps
    }
    
    "rebuild" {
        Write-Host "🔄 Reconstruindo imagens..." -ForegroundColor Cyan
        docker compose -f docker-compose.full.yml build --no-cache
        Write-Host "✅ Imagens reconstruídas" -ForegroundColor Green
    }
    
    "clean" {
        Write-Host "🧹 Limpando volumes e containers..." -ForegroundColor Yellow
        docker compose -f docker-compose.full.yml down -v
        Write-Host "✅ Limpeza concluída" -ForegroundColor Green
    }
}
