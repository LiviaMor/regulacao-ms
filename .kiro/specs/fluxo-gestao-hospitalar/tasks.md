# Tasks: Fluxo de Gestão Hospitalar

## Correções Implementadas

### Backend
- [x] Corrigir status de criação de paciente: `AGUARDANDO_REGULACAO` (não `EM_REGULACAO`)
- [x] Corrigir status de autorização: `EM_TRANSFERENCIA` (não `INTERNACAO_AUTORIZADA`)
- [x] Corrigir status de negação: `NEGADO_PENDENTE` (não `REGULACAO_NEGADA`)
- [x] Atualizar endpoint `/decisao-regulador` para setar campos de ambulância
- [x] Atualizar endpoint `/pacientes-transferencia` para filtrar status corretos
- [x] Sincronizar `backend/microservices/shared/database.py` com campos LGPD e transferência
- [x] Atualizar ms-regulacao com novos status
- [x] Atualizar ms-transferencia com novos status
- [x] Atualizar ms-hospital com novos status

### Frontend
- [x] Corrigir `Colors.error` para `Colors.danger` em AreaHospital.tsx

## Fluxo de Status Padronizado

```
AGUARDANDO_REGULACAO  → Paciente inserido pelo hospital, aguardando análise
EM_REGULACAO          → Sendo analisado pelo regulador (opcional)
EM_TRANSFERENCIA      → Autorizado, ambulância acionada
EM_TRANSITO           → Ambulância transportando paciente
ADMITIDO              → Paciente chegou ao destino
ALTA                  → Paciente recebeu alta
NEGADO_PENDENTE       → Negado, retornou ao hospital para correção
```

## Testes Recomendados

1. Criar paciente via AreaHospital → verificar status `AGUARDANDO_REGULACAO`
2. Listar fila de regulação → verificar paciente aparece
3. Processar com IA → verificar CardDecisaoIA exibe corretamente
4. Autorizar transferência → verificar status muda para `EM_TRANSFERENCIA`
5. Negar transferência → verificar status muda para `NEGADO_PENDENTE`
6. Verificar paciente negado aparece na lista do hospital
