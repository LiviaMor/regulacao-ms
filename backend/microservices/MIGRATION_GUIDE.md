# GUIA DE MIGRAÇÃO - SISTEMA UNIFICADO PARA MICROSERVIÇOS

## Visão Geral

Este guia explica como migrar do sistema atual (`main_unified.py`) para a nova arquitetura de microserviços, mantendo compatibilidade durante a transição.

## Estratégia de Migração

### Fase 1: Coexistência (Atual)
- Sistema unificado continua funcionando na porta 8000
- Microserviços funcionam nas portas 8001-8003
- API Gateway na porta 8080 roteia para microserviços
- Frontend pode usar ambos os sistemas

### Fase 2: Migração Gradual
- Endpoints específicos são redirecionados para microserviços
- Sistema unificado atua como fallback
- Testes A/B entre sistemas

### Fase 3: Microserviços Completos
- Sistema unificado é desativado
- Todos os endpoints funcionam via microserviços
- API Gateway é o ponto único de entrada

## Mapeamento de Endpoints

### Sistema Atual → Microserviços

#### MS-Hospital (8001)
```
POST /processar-regulacao → POST /solicitar-regulacao
GET /pacientes-hospital-aguardando → GET /pacientes-aguardando
POST /salvar-paciente-hospital → POST /salvar-paciente
```

#### MS-Regulacao (8002)
```
POST /processar-regulacao → POST /processar-regulacao (mantido)
GET /fila-regulacao → GET /fila-regulacao (mantido)
POST /decisao-regulador → POST /decisao-regulador (mantido)
```

#### MS-Transferencia (8003)
```
POST /transferencia → POST /autorizar-transferencia
GET /pacientes-aguardando-ambulancia → GET /pacientes-aguardando-ambulancia (novo)
```

## Configuração do Frontend

### Opção 1: API Gateway (Recomendado)
```typescript
const API_BASE_URL = "http://localhost:8080";

// Todos os endpoints funcionam através do gateway
const response = await fetch(`${API_BASE_URL}/solicitar-regulacao`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data)
});
```

### Opção 2: Microserviços Diretos
```typescript
const MS_HOSPITAL_URL = "http://localhost:8001";
const MS_REGULACAO_URL = "http://localhost:8002";
const MS_TRANSFERENCIA_URL = "http://localhost:8003";

// Hospital
await fetch(`${MS_HOSPITAL_URL}/solicitar-regulacao`, {...});

// Regulação
await fetch(`${MS_REGULACAO_URL}/processar-regulacao`, {...});

// Transferência
await fetch(`${MS_TRANSFERENCIA_URL}/autorizar-transferencia`, {...});
```

### Opção 3: Sistema Unificado (Compatibilidade)
```typescript
const API_BASE_URL = "http://localhost:8000";

// Continua funcionando como antes
const response = await fetch(`${API_BASE_URL}/processar-regulacao`, {...});
```

## Banco de Dados

### Compartilhamento
- Todos os microserviços usam o mesmo banco PostgreSQL
- Modelos de dados são compartilhados via `shared/database.py`
- Migrações são aplicadas automaticamente

### Novos Modelos
- `TransferenciaAmbulancia`: Controle de transferências
- `MedicacaoAltaComplexidade`: Para MS-Medicacao futuro
- Campos adicionais em modelos existentes

## Autenticação

### JWT Compartilhado
- Mesmo SECRET_KEY em todos os microserviços
- Token válido em qualquer serviço
- Middleware de autenticação compartilhado

### Exemplo de Uso
```python
# Qualquer microserviço
from shared.auth import get_current_user, require_role

@app.get("/endpoint-protegido")
async def endpoint(current_user: Usuario = Depends(require_role(["ADMIN"]))):
    return {"user": current_user.nome}
```

## Comunicação Entre Microserviços

### HTTP Interno
```python
from shared.utils import MicroserviceClient

# MS-Hospital chamando MS-Regulacao
ms_regulacao = MicroserviceClient("http://ms-regulacao:8002", "MS-Regulacao")
resultado = ms_regulacao.post("/processar-regulacao", data)
```

### Eventos Futuros
- Redis Pub/Sub para eventos assíncronos
- Celery para processamento em background
- Webhooks para notificações

## Monitoramento

### Health Checks
```bash
# Verificar todos os serviços
curl http://localhost:8001/health  # MS-Hospital
curl http://localhost:8002/health  # MS-Regulacao
curl http://localhost:8003/health  # MS-Transferencia
curl http://localhost:8080/health  # API Gateway
```

### Logs Centralizados
```bash
# Ver logs de todos os microserviços
docker-compose -f docker-compose.microservices.yml logs -f

# Ver logs de um serviço específico
docker-compose -f docker-compose.microservices.yml logs -f ms-hospital
```

### Métricas
- Cada microserviço expõe métricas de performance
- Tempo de resposta da IA
- Throughput de regulações
- Status de transferências

## Testes

### Testes Individuais
```bash
# Testar MS-Hospital
curl -X POST http://localhost:8001/solicitar-regulacao \
  -H "Content-Type: application/json" \
  -d '{"protocolo":"TEST-001","cid":"M54.5","especialidade":"ORTOPEDIA"}'

# Testar MS-Regulacao
curl -X POST http://localhost:8002/processar-regulacao \
  -H "Content-Type: application/json" \
  -d '{"protocolo":"TEST-001","cid":"M54.5","especialidade":"ORTOPEDIA"}'
```

### Testes de Integração
```bash
# Fluxo completo via API Gateway
curl -X POST http://localhost:8080/solicitar-regulacao \
  -H "Content-Type: application/json" \
  -d '{"protocolo":"TEST-001","cid":"M54.5","especialidade":"ORTOPEDIA"}'
```

## Rollback

### Em Caso de Problemas
1. Parar microserviços: `docker-compose -f docker-compose.microservices.yml down`
2. Voltar para sistema unificado: `python backend/main_unified.py`
3. Frontend volta para `http://localhost:8000`

### Backup de Dados
- Banco de dados é compartilhado, dados preservados
- Histórico de decisões mantém rastreabilidade
- Logs de auditoria preservados

## Próximos Passos

### Microserviços Futuros
1. **MS-Alta**: Gestão de altas hospitalares
2. **MS-Obito**: Registro de óbitos
3. **MS-Transplante**: Fila de transplantes
4. **MS-Medicacao**: Medicação de alta complexidade

### Melhorias Planejadas
- Service Discovery automático
- Circuit Breakers para resiliência
- Rate Limiting por microserviço
- Observabilidade com Prometheus/Grafana

## Suporte

### Documentação
- Cada microserviço tem documentação Swagger em `/docs`
- Logs detalhados para debugging
- Health checks para monitoramento

### Contato
- Logs centralizados mostram origem dos problemas
- Cada microserviço tem identificação única
- Rastreabilidade completa de requisições