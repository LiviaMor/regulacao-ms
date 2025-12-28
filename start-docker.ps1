# =============================================================================
# SCRIPT DE INICIALIZACAO - Sistema de Regulacao SES-GO (Docker) - Windows
# =============================================================================

param(
    [Parameter(Position=0)]
    [ValidateSet("up", "start", "down", "stop", "logs", "status", "ps", "rebuild", "clean")]
    [string]$Command = "up"
)

Write-Host "=============================================="
Write-Host "  SISTEMA DE REGULACAO SES-GO - DOCKER"
Write-Host "=============================================="

# Verificar se Docker esta instalado
try {
    docker --version | Out-Null
    Write-Host "[OK] Docker encontrado" -ForegroundColor Green
} catch {
    Write-Host "[ERRO] Docker nao esta instalado!" -ForegroundColor Red
    Write-Host "   Instale em: https://docs.docker.com/get-docker/"
    exit 1
}

switch ($Command) {
    { $_ -in "up", "start" } {
        Write-Host ""
        Write-Host "[INFO] Iniciando todos os servicos..." -ForegroundColor Cyan
        Write-Host "   (Primeira execucao pode demorar ~10min para baixar imagens e modelos)"
        Write-Host ""
        
        docker compose -f docker-compose.full.yml up -d
        
        Write-Host ""
        Write-Host "[INFO] Aguardando servicos iniciarem..."
        Start-Sleep -Seconds 10
        
        Write-Host ""
        Write-Host "[INFO] Status dos servicos:"
        docker compose -f docker-compose.full.yml ps
        
        Write-Host ""
        Write-Host "=============================================="
        Write-Host "  [OK] SISTEMA INICIADO!" -ForegroundColor Green
        Write-Host "=============================================="
        Write-Host ""
        Write-Host "  Frontend:    http://localhost:8082"
        Write-Host "  Backend API: http://localhost:8000"
        Write-Host "  API Docs:    http://localhost:8000/docs"
        Write-Host "  Ollama:      http://localhost:11434"
        Write-Host "  PostgreSQL:  localhost:5432"
        Write-Host ""
        Write-Host "  Ver logs:    .\start-docker.ps1 logs"
        Write-Host "  Parar:       .\start-docker.ps1 down"
        Write-Host "=============================================="
    }
    
    { $_ -in "down", "stop" } {
        Write-Host "[INFO] Parando todos os servicos..." -ForegroundColor Yellow
        docker compose -f docker-compose.full.yml down
        Write-Host "[OK] Servicos parados" -ForegroundColor Green
    }
    
    "logs" {
        docker compose -f docker-compose.full.yml logs -f
    }
    
    { $_ -in "status", "ps" } {
        docker compose -f docker-compose.full.yml ps
    }
    
    "rebuild" {
        Write-Host "[INFO] Reconstruindo imagens..." -ForegroundColor Cyan
        docker compose -f docker-compose.full.yml build --no-cache
        Write-Host "[OK] Imagens reconstruidas" -ForegroundColor Green
    }
    
    "clean" {
        Write-Host "[INFO] Limpando volumes e containers..." -ForegroundColor Yellow
        docker compose -f docker-compose.full.yml down -v
        Write-Host "[OK] Limpeza concluida" -ForegroundColor Green
    }
}
