# =============================================================================
# DIAGNOSTICO DOCKER - Sistema de Regulacao SES-GO
# =============================================================================
# Script para diagnosticar problemas com os containers Docker
# =============================================================================

Write-Host "=============================================="
Write-Host "  DIAGNOSTICO DOCKER - SISTEMA REGULACAO"
Write-Host "=============================================="
Write-Host ""

# 1. Verificar Docker
Write-Host "[1/6] Verificando Docker..." -ForegroundColor Cyan
try {
    $dockerVersion = docker --version
    Write-Host "   [OK] $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "   [ERRO] Docker nao encontrado!" -ForegroundColor Red
    exit 1
}

# 2. Verificar containers
Write-Host ""
Write-Host "[2/6] Verificando containers..." -ForegroundColor Cyan
docker compose -f docker-compose.full.yml ps

# 3. Verificar logs de erro
Write-Host ""
Write-Host "[3/6] Verificando logs de erro (ultimas 20 linhas)..." -ForegroundColor Cyan

Write-Host ""
Write-Host "--- BACKEND ---" -ForegroundColor Yellow
docker logs regulacao_backend --tail 20 2>&1 | Select-Object -Last 10

Write-Host ""
Write-Host "--- MS-INGESTAO ---" -ForegroundColor Yellow
docker logs regulacao_ms_ingestao --tail 20 2>&1 | Select-Object -Last 10

Write-Host ""
Write-Host "--- FRONTEND ---" -ForegroundColor Yellow
docker logs regulacao_frontend --tail 20 2>&1 | Select-Object -Last 10

Write-Host ""
Write-Host "--- OLLAMA ---" -ForegroundColor Yellow
docker logs regulacao_ollama --tail 10 2>&1 | Select-Object -Last 5

# 4. Verificar portas
Write-Host ""
Write-Host "[4/6] Verificando portas..." -ForegroundColor Cyan

$portas = @(
    @{Porta=5432; Servico="PostgreSQL"},
    @{Porta=6379; Servico="Redis"},
    @{Porta=8000; Servico="Backend"},
    @{Porta=8004; Servico="MS-Ingestao"},
    @{Porta=8082; Servico="Frontend"},
    @{Porta=11434; Servico="Ollama"}
)

foreach ($p in $portas) {
    try {
        $connection = Test-NetConnection -ComputerName localhost -Port $p.Porta -WarningAction SilentlyContinue
        if ($connection.TcpTestSucceeded) {
            Write-Host "   [OK] $($p.Servico) (porta $($p.Porta))" -ForegroundColor Green
        } else {
            Write-Host "   [--] $($p.Servico) (porta $($p.Porta)) - NAO RESPONDE" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   [--] $($p.Servico) (porta $($p.Porta)) - ERRO" -ForegroundColor Yellow
    }
}

# 5. Testar endpoints
Write-Host ""
Write-Host "[5/6] Testando endpoints..." -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "   [OK] Backend /health - HTTP $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "   [--] Backend /health - NAO RESPONDE" -ForegroundColor Yellow
}

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8004/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "   [OK] MS-Ingestao /health - HTTP $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "   [--] MS-Ingestao /health - NAO RESPONDE" -ForegroundColor Yellow
}

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8082" -TimeoutSec 5 -UseBasicParsing
    Write-Host "   [OK] Frontend - HTTP $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "   [--] Frontend - NAO RESPONDE" -ForegroundColor Yellow
}

try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 5 -UseBasicParsing
    Write-Host "   [OK] Ollama /api/tags - HTTP $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "   [--] Ollama /api/tags - NAO RESPONDE" -ForegroundColor Yellow
}

# 6. Sugestoes
Write-Host ""
Write-Host "[6/6] Sugestoes..." -ForegroundColor Cyan
Write-Host ""
Write-Host "   Se algum container estiver com erro, tente:" -ForegroundColor White
Write-Host "   1. Reconstruir imagens: docker compose -f docker-compose.full.yml build --no-cache" -ForegroundColor Gray
Write-Host "   2. Reiniciar: docker compose -f docker-compose.full.yml up -d" -ForegroundColor Gray
Write-Host "   3. Ver logs detalhados: docker logs <container_name> -f" -ForegroundColor Gray
Write-Host ""
Write-Host "=============================================="
