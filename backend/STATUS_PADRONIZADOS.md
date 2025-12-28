# PADRONIZAÇÃO DE STATUS DO SISTEMA

## Status Oficiais do Paciente

| Status | Descrição | Área que Exibe | Próximo Status |
|--------|-----------|----------------|----------------|
| `AGUARDANDO_REGULACAO` | Paciente inserido pelo hospital, aguardando análise | Fila de Regulação | EM_TRANSFERENCIA ou NEGADO_PENDENTE |
| `NEGADO_PENDENTE` | Regulação negada, aguardando correção do hospital | Área Hospital (para edição) | AGUARDANDO_REGULACAO (após reenvio) |
| `EM_TRANSFERENCIA` | Transferência autorizada, ambulância acionada | Área de Transferência | EM_TRANSITO |
| `EM_TRANSITO` | Paciente sendo transportado pela ambulância | Área de Transferência | ADMITIDO |
| `ADMITIDO` | Paciente chegou ao destino, internado | Área de Auditoria | ALTA |
| `ALTA` | Paciente recebeu alta hospitalar | Histórico/Consulta Pública | - |

## Status da Ambulância

| Status | Descrição | Status do Paciente |
|--------|-----------|-------------------|
| `ACIONADA` | Ambulância foi acionada | EM_TRANSFERENCIA |
| `A_CAMINHO` | Ambulância a caminho do hospital origem | EM_TRANSFERENCIA |
| `NO_LOCAL` | Ambulância chegou no hospital origem | EM_TRANSFERENCIA |
| `TRANSPORTANDO` | Paciente em transporte | EM_TRANSITO |
| `CONCLUIDA` | Paciente entregue no destino | ADMITIDO |

## Fluxo Completo

```
HOSPITAL                    REGULAÇÃO                   TRANSFERÊNCIA              AUDITORIA
   │                            │                            │                         │
   │  Insere paciente           │                            │                         │
   │  ─────────────────────►    │                            │                         │
   │  AGUARDANDO_REGULACAO      │                            │                         │
   │                            │                            │                         │
   │                            │  Processa com IA           │                         │
   │                            │  ─────────────────►        │                         │
   │                            │                            │                         │
   │                            │  AUTORIZAR                 │                         │
   │                            │  ─────────────────────────►│                         │
   │                            │  EM_TRANSFERENCIA          │                         │
   │                            │  (ambulância ACIONADA)     │                         │
   │                            │                            │                         │
   │  ◄─────────────────────────│  NEGAR                     │                         │
   │  NEGADO_PENDENTE           │                            │                         │
   │  (editar e reenviar)       │                            │                         │
   │                            │                            │                         │
   │                            │                            │  Atualiza status        │
   │                            │                            │  ambulância             │
   │                            │                            │  ─────────────────────► │
   │                            │                            │  ADMITIDO               │
   │                            │                            │  (ambulância CONCLUIDA) │
   │                            │                            │                         │
   │                            │                            │                         │  Registra alta
   │                            │                            │                         │  ───────────►
   │                            │                            │                         │  ALTA
```

## Endpoints por Área

### Área Hospital
- `GET /pacientes-hospital-aguardando` → Status: `AGUARDANDO_REGULACAO`, `NEGADO_PENDENTE`
- `POST /salvar-paciente-hospital` → Define status: `AGUARDANDO_REGULACAO`

### Área Regulação (Fila)
- `GET /pacientes-hospital-aguardando` → Filtra apenas: `AGUARDANDO_REGULACAO`
- `POST /processar-regulacao` → Processa com IA
- `POST /decisao-regulador` → Muda para: `EM_TRANSFERENCIA` ou `NEGADO_PENDENTE`

### Área Transferência
- `GET /pacientes-transferencia` → Status: `EM_TRANSFERENCIA`, `EM_TRANSITO`
- `POST /atualizar-status-ambulancia` → Atualiza status ambulância e paciente

### Área Auditoria
- `GET /pacientes-auditoria` → Status: `ADMITIDO`
- `POST /registrar-alta` → Muda para: `ALTA`

### Consulta Pública
- `GET /consulta-publica/paciente/{busca}` → Todos os status (dados anonimizados)

---
**Última atualização**: 28/12/2024
