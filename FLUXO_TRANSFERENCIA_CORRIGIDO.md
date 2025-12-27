# FLUXO DE TRANSFERÊNCIA E AMBULÂNCIA - CORRIGIDO ✅

## PROBLEMA IDENTIFICADO

O usuário relatou que:
1. ❌ Botão "Chamar Ambulância" estava na aba de Regulação (deveria estar na Transferência)
2. ❌ Pacientes com ambulância solicitada não apareciam na aba Transferência
3. ❌ Status "Aguardando Ambulância" não aparecia na consulta pública
4. ❌ Após admitir paciente na Regulação, ele não saía da fila
5. ❌ Faltava o ciclo completo: Regulação → Transferência → Internação

## SOLUÇÃO IMPLEMENTADA

### 1. NOVOS STATUS DO SISTEMA

```
AGUARDANDO_REGULACAO → Paciente inserido pelo hospital, aguardando análise
INTERNACAO_AUTORIZADA → Regulador aprovou, aguardando ambulância
EM_TRANSFERENCIA → Ambulância solicitada, em processo de transferência
INTERNADA → Paciente chegou ao destino
COM_ALTA → Paciente recebeu alta
REGULACAO_NEGADA → Regulador negou (volta para fila)
```

### 2. FLUXO COMPLETO CORRIGIDO

```
┌─────────────────────────────────────────────────────────────┐
│ 1. ÁREA HOSPITALAR                                          │
│    Hospital insere paciente → Status: AGUARDANDO_REGULACAO  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. ÁREA DE REGULAÇÃO (Regulador Médico)                    │
│    - Visualiza fila de pacientes AGUARDANDO_REGULACAO       │
│    - IA analisa e sugere hospital                           │
│    - Regulador decide:                                      │
│      ✅ APROVAR → Status: INTERNACAO_AUTORIZADA             │
│      ❌ NEGAR → Status: REGULACAO_NEGADA (volta para fila) │
│      🔄 ALTERAR → Muda hospital e aprova                    │
│    - Paciente SAI da fila de regulação                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. ÁREA DE TRANSFERÊNCIA (Regulador/Coordenador)           │
│    - Lista pacientes com status: INTERNACAO_AUTORIZADA     │
│    - Botão: 🚑 SOLICITAR AMBULÂNCIA                        │
│      → Escolhe tipo: USA / USB / AEROMÉDICO                │
│      → Status muda para: EM_TRANSFERENCIA                  │
│      → status_ambulancia: SOLICITADA                       │
│    - Acompanha status da ambulância:                       │
│      SOLICITADA → A_CAMINHO → NO_LOCAL → TRANSPORTANDO     │
│    - Quando CONCLUÍDA → Status: INTERNADA                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. CONSULTA PÚBLICA                                         │
│    - Mostra status atual do paciente                        │
│    - Se EM_TRANSFERENCIA, mostra:                          │
│      • Status da ambulância                                 │
│      • Tipo de transporte                                   │
│      • Data/hora da solicitação                            │
│    - Dados pessoais ANONIMIZADOS (LGPD)                    │
└─────────────────────────────────────────────────────────────┘
```

### 3. BANCO DE DADOS - NOVAS COLUNAS

Adicionadas 5 colunas na tabela `pacientes_regulacao`:

```sql
tipo_transporte VARCHAR(50)              -- 'USA', 'USB', 'AEROMÉDICO'
status_ambulancia VARCHAR(50)            -- 'SOLICITADA', 'A_CAMINHO', etc.
data_solicitacao_ambulancia TIMESTAMP    -- Quando foi solicitada
data_internacao TIMESTAMP                -- Quando chegou ao destino
observacoes_transferencia TEXT           -- Observações da transferência
```

✅ Script executado: `backend/adicionar_colunas_transferencia.py`

### 4. NOVOS ENDPOINTS BACKEND

#### POST /solicitar-ambulancia
```json
{
  "protocolo": "REG-2025-001",
  "tipo_transporte": "USA",
  "observacoes": "Paciente crítico"
}
```
- Muda status de `INTERNACAO_AUTORIZADA` → `EM_TRANSFERENCIA`
- Define `status_ambulancia` = `SOLICITADA`
- Requer autenticação (REGULADOR/ADMIN)

#### GET /pacientes-transferencia
- Lista pacientes com status: `INTERNACAO_AUTORIZADA` ou `EM_TRANSFERENCIA`
- Retorna informações de ambulância
- Requer autenticação (REGULADOR/ADMIN)

#### POST /atualizar-status-ambulancia
```json
{
  "protocolo": "REG-2025-001",
  "novo_status": "A_CAMINHO",
  "observacoes": "Ambulância saiu da base"
}
```
- Atualiza status da ambulância
- Se status = `CONCLUIDA`, muda paciente para `INTERNADA`
- Requer autenticação (REGULADOR/ADMIN)

### 5. FRONTEND - COMPONENTES ATUALIZADOS

#### AreaTransferencia.tsx
✅ Agora busca dados reais do backend
✅ Botão "🚑 Solicitar Ambulância" para pacientes autorizados
✅ Permite escolher tipo de transporte (USA/USB/AEROMÉDICO)
✅ Botão "Atualizar Status" para acompanhar ambulância
✅ Requer autenticação (login admin@sesgo.gov.br / admin123)

#### ConsultaPaciente.tsx
✅ Mostra status de ambulância quando disponível
✅ Exibe tipo de transporte
✅ Mostra data/hora da solicitação
✅ Dados pessoais anonimizados (LGPD)

#### FilaRegulacao.tsx
✅ Lista apenas pacientes com status `AGUARDANDO_REGULACAO`
✅ Após aprovação, paciente SAI da fila automaticamente
✅ Paciente vai para Área de Transferência

#### transferencia.tsx (Aba)
✅ Adicionada autenticação (igual à aba de Regulação)
✅ Passa userToken para AreaTransferencia
✅ Header com informações do usuário logado

### 6. ANONIMIZAÇÃO LGPD

Função `anonimizar_paciente()` atualizada para incluir:
- ✅ status_ambulancia
- ✅ tipo_transporte
- ✅ data_solicitacao_ambulancia

Dados pessoais continuam anonimizados:
- Nome: "João da Silva" → "J*** d* S***"
- CPF: "123.456.789-01" → "***.***.*89-01"
- Telefone: "(62) 98765-4321" → "(62) *****-**21"

## ARQUIVOS MODIFICADOS

### Backend
1. ✅ `backend/main_unified.py` - 3 novos endpoints
2. ✅ `backend/shared/database.py` - Modelo atualizado + anonimização
3. ✅ `backend/adicionar_colunas_transferencia.py` - Script de migração (EXECUTADO)

### Frontend
1. ✅ `regulacao-app/components/AreaTransferencia.tsx` - Reescrito completamente
2. ✅ `regulacao-app/components/ConsultaPaciente.tsx` - Adicionado status ambulância
3. ✅ `regulacao-app/app/(tabs)/transferencia.tsx` - Adicionada autenticação

## COMO TESTAR

### 1. Criar Paciente (Área Hospitalar)
```
Nome: João da Silva
CPF: 12345678901
Especialidade: CARDIOLOGIA
CID: I21 (Infarto)
```
→ Status: `AGUARDANDO_REGULACAO`

### 2. Aprovar na Regulação
- Login: admin@sesgo.gov.br / admin123
- Aba "Regulação"
- Processar com IA
- Aprovar decisão
→ Status: `INTERNACAO_AUTORIZADA`
→ Paciente SAI da fila de regulação

### 3. Solicitar Ambulância (Transferência)
- Aba "Transferência"
- Paciente aparece na lista
- Clicar "🚑 Solicitar Ambulância"
- Escolher tipo: USA
→ Status: `EM_TRANSFERENCIA`
→ status_ambulancia: `SOLICITADA`

### 4. Atualizar Status Ambulância
- Clicar "Atualizar Status"
- Escolher: A_CAMINHO → NO_LOCAL → TRANSPORTANDO → CONCLUIDA
→ Quando CONCLUIDA, status: `INTERNADA`

### 5. Consultar Publicamente
- Aba "Consulta"
- Buscar por protocolo ou CPF
- Ver status de ambulância
- Dados pessoais anonimizados

## CREDENCIAIS DE TESTE

```
Email: admin@sesgo.gov.br
Senha: admin123
```

## PRÓXIMOS PASSOS (OPCIONAL)

1. ⏱️ Adicionar previsão de chegada da ambulância
2. 📍 Integração com GPS para rastreamento em tempo real
3. 📊 Dashboard de ambulâncias disponíveis
4. 🔔 Notificações push quando ambulância chegar
5. 📱 App mobile para motoristas de ambulância

## CONCLUSÃO

✅ Fluxo completo implementado e funcional
✅ Botão de ambulância na aba correta (Transferência)
✅ Pacientes aparecem corretamente em cada etapa
✅ Status de ambulância visível na consulta pública
✅ Ciclo completo: Hospital → Regulação → Transferência → Internação
✅ Dados anonimizados conforme LGPD
✅ Sistema pronto para uso!

---

**Data:** 27/12/2024
**Status:** ✅ IMPLEMENTADO E TESTADO
