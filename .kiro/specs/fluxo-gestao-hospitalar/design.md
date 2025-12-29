# Design: Fluxo de Gestão Hospitalar

## Arquitetura

### Frontend (React Native/Expo)
- AreaHospital.tsx → POST /processar-regulacao, POST /salvar-paciente-hospital
- FilaRegulacao.tsx → GET /pacientes-hospital-aguardando
- CardDecisaoIA.tsx → POST /decisao-regulador
- AreaTransferencia.tsx → GET /pacientes-transferencia

### Backend (FastAPI - main_unified.py)
- /processar-regulacao → analisar_com_ia_inteligente()
- /salvar-paciente-hospital → PacienteRegulacao (status=AGUARDANDO)
- /pacientes-hospital-aguardando → filter(status IN [AGUARDANDO, NEGADO])
- /decisao-regulador → atualiza status + aciona ambulância

### Database (PostgreSQL)
Tabela pacientes_regulacao com campos LGPD, clínicos, IA e transferência.

## Fluxo de Dados

### 1. Hospital Solicita Regulação
1. AreaHospital.tsx envia POST /processar-regulacao
2. Backend processa com IA e retorna decisaoIA
3. Frontend envia POST /salvar-paciente-hospital
4. Backend salva com status='AGUARDANDO_REGULACAO'

### 2. Regulador Processa Paciente
1. FilaRegulacao.tsx busca GET /pacientes-hospital-aguardando
2. Backend retorna pacientes com status AGUARDANDO ou NEGADO
3. Regulador clica "Processar com IA"
4. CardDecisaoIA exibe análise

### 3. Regulador Toma Decisão
1. Regulador clica AUTORIZAR/NEGAR/ALTERAR
2. POST /decisao-regulador com decisão
3. Backend atualiza status conforme decisão

## Status Válidos
- AGUARDANDO_REGULACAO: Aguardando análise
- EM_REGULACAO: Sendo analisado
- NEGADO_PENDENTE: Negado, retornou ao hospital
- EM_TRANSFERENCIA: Autorizado, aguardando ambulância
- EM_TRANSITO: Ambulância a caminho
- ADMITIDO: Paciente chegou
- ALTA: Paciente recebeu alta

## Correções Implementadas
1. Status correto: AGUARDANDO_REGULACAO (não EM_REGULACAO)
2. Filtro correto: Lista AGUARDANDO e NEGADO_PENDENTE
3. Cores do tema: Colors.danger em vez de Colors.error
4. Schema sincronizado entre backend/shared e microservices/shared
