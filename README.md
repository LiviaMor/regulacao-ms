# Sistema de Regulação Autônoma SES-GO
### PAIC-Regula - Solução de IA Aberta para Otimização da Regulação Médica

<div align="center">

![SES-GO](https://img.shields.io/badge/SES--GO-Sistema%20de%20Regulação-blue?style=for-the-badge)
![IA Aberta](https://img.shields.io/badge/IA%20Aberta-BioBERT%20%2B%20Llama3-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-MVP%20Funcional%20TRL%206--7-orange?style=for-the-badge)
![Licença](https://img.shields.io/badge/Licença-MIT-brightgreen?style=for-the-badge)

</div>

---

## 🏆 **PRÊMIO GOIÁS ABERTO PARA IA (GO.IA)**

Este projeto foi desenvolvido para o **Prêmio FAPEG de IA Aberta** e atende aos três pilares fundamentais do edital:

| Pilar | Requisito | Status |
|-------|-----------|--------|
| **IA Aberta** | Modelos de pesos abertos e auditáveis | ✅ BioBERT + Llama 3 |
| **TRL 5-7** | Protótipo funcional validado | ✅ MVP Operacional |
| **Impacto Regional** | Problema específico de Goiás | ✅ Regulação SUS-GO |

---

## 📋 **TRANSPARÊNCIA DO MODELO DE IA**

### Modelos Utilizados (100% Open Source)

| Modelo | Fonte | Licença | Dados de Treinamento |
|--------|-------|---------|---------------------|
| **BioBERT v1.1** | [dmis-lab/biobert-base-cased-v1.1](https://huggingface.co/dmis-lab/biobert-base-cased-v1.1) | Apache 2.0 | PubMed (4.5B palavras) + PMC (13.5B palavras) |
| **Bio_ClinicalBERT** | [emilyalsentzer/Bio_ClinicalBERT](https://huggingface.co/emilyalsentzer/Bio_ClinicalBERT) | MIT | MIMIC-III (notas clínicas) |
| **Llama 3 8B** | [Meta AI](https://llama.meta.com/) | Llama 3 License | 15T tokens (dados públicos) |

### Dados de Treinamento do BioBERT

O modelo BioBERT foi pré-treinado pela equipe DMIS Lab (Korea University) usando:

1. **PubMed Abstracts**: 4.5 bilhões de palavras de resumos de artigos científicos biomédicos
2. **PMC Full-text Articles**: 13.5 bilhões de palavras de artigos completos do PubMed Central
3. **Vocabulário**: WordPiece com 28.996 tokens especializados em terminologia médica

**Referência Científica:**
> Lee, J., et al. (2020). BioBERT: a pre-trained biomedical language representation model for biomedical text mining. Bioinformatics, 36(4), 1234-1240. DOI: [10.1093/bioinformatics/btz682](https://doi.org/10.1093/bioinformatics/btz682)

### Como a IA Toma Decisões (Explicabilidade)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PIPELINE DE DECISÃO AUDITÁVEL                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. ENTRADA                                                             │
│     └── Prontuário + CID + Especialidade + Cidade de Origem             │
│                                                                         │
│  2. ANÁLISE BIOBERT (NLP Médico)                                        │
│     └── Extração de entidades: sintomas, condições, anatomia            │
│     └── Score de confiança: 0.0 a 1.0                                   │
│                                                                         │
│  3. CLASSIFICAÇÃO DE RISCO (Baseada em CIDs)                            │
│     └── VERMELHO (Score 8-10): I21 (Infarto), S06 (Trauma craniano)     │
│     └── AMARELO (Score 5-7): J18 (Pneumonia), E11 (Diabetes)            │
│     └── VERDE (Score 1-4): M54 (Dor lombar), M79 (Dor muscular)         │
│                                                                         │
│  4. SELEÇÃO DE HOSPITAL (Pipeline Goiás)                                │
│     └── Filtro 1: Especialidade compatível                              │
│     └── Filtro 2: Hierarquia SUS (UPA → Regional → Referência)          │
│     └── Filtro 3: Distância geodésica (Haversine)                       │
│                                                                         │
│  5. MATCHMAKER LOGÍSTICO                                                │
│     └── Cálculo de rota otimizada                                       │
│     └── Seleção de ambulância (USA/USB)                                 │
│     └── Tempo estimado de transporte                                    │
│                                                                         │
│  6. SAÍDA (JSON Estruturado)                                            │
│     └── hospital_sugerido + justificativa_tecnica + score_prioridade    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Auditabilidade das Decisões

Todas as decisões da IA são registradas na tabela `HistoricoDecisoes`:

```sql
-- Estrutura de auditoria (LGPD Compliant)
CREATE TABLE historico_decisoes (
    id INTEGER PRIMARY KEY,
    protocolo VARCHAR(50),
    decisao_ia JSON,           -- Decisão completa da IA (preservada)
    usuario_validador VARCHAR, -- Quem validou (regulador humano)
    decisao_final JSON,        -- Decisão final (humano pode alterar)
    tempo_processamento FLOAT, -- Tempo de processamento em segundos
    created_at TIMESTAMP       -- Timestamp para auditoria
);
```

### Endpoint de Auditoria Pública

```bash
# Consultar auditoria de um paciente específico
GET /auditoria/paciente/{protocolo}

# Relatório geral de auditoria (requer autenticação)
GET /auditoria/relatorio?data_inicio=2025-01-01&data_fim=2025-12-31
```

---

## **Apresentação para o ABERTO de IA de Goiás**

Este sistema representa uma **solução inovadora de Inteligência Artificial** desenvolvida para revolucionar o processo de regulação médica da **Secretaria de Estado da Saúde de Goiás (SES-GO)**. 

### **Problema Resolvido**
- **Agilidade**: Redução do tempo de análise de prontuários de horas para minutos
- **Precisão**: IA especializada em análise médica com BioBERT + Llama3
- **Transparência**: Dashboard público em tempo real da situação hospitalar
- **Eficiência**: Automatização do fluxo de regulação com validação humana

### **Inovação Tecnológica**
Sistema pioneiro que combina **processamento de linguagem natural médica** com **análise preditiva** para apoiar decisões críticas de regulação hospitalar, mantendo o regulador humano no centro do processo decisório.

---

## **📁 Estrutura do Projeto**

```
regulacao-ms/
├── backend/                          # Backend Python/FastAPI
│   ├── main_unified.py              # ✅ Servidor principal unificado (porta 8000)
│   ├── requirements.txt             # ✅ Dependências Python
│   ├── .env                         # Configuração (DATABASE_URL, etc.)
│   ├── .env.example                 # Exemplo de configuração
│   ├── docker-compose.yml           # Docker Compose
│   ├── Dockerfile.unified           # Dockerfile para build
│   │
│   ├── shared/                      # Módulos compartilhados
│   │   └── database.py              # ✅ Modelos e anonimização LGPD
│   │
│   ├── microservices/               # Microserviços
│   │   ├── shared/                  # Código compartilhado entre microserviços
│   │   │   ├── database.py          # ✅ Modelos compartilhados
│   │   │   ├── biobert_service.py   # ✅ Serviço BioBERT
│   │   │   ├── matchmaker_logistico.py  # ✅ Matchmaker
│   │   │   ├── xai_explicabilidade.py   # ✅ XAI
│   │   │   ├── auth.py              # Autenticação JWT
│   │   │   └── utils.py             # Utilitários
│   │   │
│   │   ├── ms-ingestao/             # ✅ MS-Ingestao (porta 8004)
│   │   │   ├── main.py              # ✅ Memória de curto prazo, tendências
│   │   │   └── README.md            # Documentação do microserviço
│   │   │
│   │   ├── ms-hospital/             # MS Hospital (futuro)
│   │   ├── ms-regulacao/            # MS Regulação (futuro)
│   │   └── ms-transferencia/        # MS Transferência (futuro)
│   │
│   ├── pipeline_hospitais_goias.py  # ✅ Pipeline de seleção de hospitais
│   ├── migrar_banco_completo.py     # ✅ Script migração completa
│   ├── verificar_colunas.py         # ✅ Verificar banco de dados
│   └── criar_paciente_teste.py      # ✅ Criar dados de teste
│
├── regulacao-app/                    # Frontend React Native/Expo (porta 8082)
│   ├── app/                         # Rotas e telas
│   │   └── (tabs)/                  # Navegação por abas
│   │       ├── index.tsx            # Dashboard público
│   │       ├── hospital.tsx         # ✅ Área hospitalar
│   │       ├── regulacao.tsx        # ✅ Área de regulação
│   │       ├── transferencia.tsx    # ✅ Área de transferência
│   │       ├── consulta.tsx         # ✅ Consulta pública
│   │       └── auditoria.tsx        # ✅ Dashboard auditoria
│   │
│   ├── components/                  # Componentes React
│   │   ├── AreaHospital.tsx         # ✅ Formulário inserção paciente
│   │   ├── FilaRegulacao.tsx        # ✅ Fila de regulação
│   │   ├── CardDecisaoIA.tsx        # ✅ Card de decisão IA
│   │   ├── AreaTransferencia.tsx    # ✅ Gestão de transferências
│   │   ├── ConsultaPaciente.tsx     # ✅ Consulta pública
│   │   ├── DashboardPublico.tsx     # ✅ Dashboard público
│   │   ├── DashboardAuditoria.tsx   # ✅ Dashboard auditoria
│   │   ├── OcupacaoHospitais.tsx    # ✅ Ocupação hospitalar
│   │   └── ui/                      # Componentes UI
│   │       ├── Header.tsx
│   │       ├── HospitalCard.tsx
│   │       ├── AILoadingIndicator.tsx
│   │       └── Toast.tsx
│   │
│   ├── constants/                   # Constantes e temas
│   │   └── theme.ts
│   │
│   ├── package.json                 # ✅ Dependências Node.js
│   └── tsconfig.json                # Configuração TypeScript
│
├── dados_*.json                     # Dados reais SES-GO
│   ├── dados_admitidos.json
│   ├── dados_alta.json
│   ├── dados_em_regulacao.json
│   └── dados_em_transito.json
│
├── teste_*.py                       # Scripts de teste
│   ├── teste_fluxo_completo_validacao.py  # ✅ Teste end-to-end
│   ├── teste_fluxo_hospital_regulacao.py
│   ├── teste_ia_completa.py
│   └── benchmark_performance.py
│
├── ANALISE_COMPLETA_SISTEMA.md      # ✅ Análise técnica completa
├── DIAGRAMA_FLUXO_COMPLETO.md       # ✅ Diagrama de fluxo
├── CHECKLIST_VALIDACAO_FINAL.md     # ✅ Checklist de validação
├── COMO_TESTAR_SISTEMA_COMPLETO.md  # ✅ Guia de testes
├── FLUXO_TRANSFERENCIA_CORRIGIDO.md # ✅ Fluxo de transferência
└── README.md                        # ✅ Este arquivo
```

---

## **🏗️ Arquitetura da Solução**

### **Visão Geral**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React Native/Expo)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │Dashboard │  │ Hospital │  │Regulação │  │Transfer. │  │ Consulta │ │
│  │ Público  │  │          │  │          │  │          │  │  Pública │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘ │
└───────┼─────────────┼─────────────┼─────────────┼─────────────┼────────┘
        │             │             │             │             │
        └─────────────┴─────────────┴─────────────┴─────────────┘
                                    │
                              REST API (FastAPI)
                                    │
┌───────────────────────────────────┼─────────────────────────────────────┐
│                         BACKEND (Python/FastAPI)                        │
│                                   │                                     │
│  ┌────────────────────────────────┴──────────────────────────────────┐ │
│  │                     main_unified.py                                │ │
│  │  • Endpoints REST                                                  │ │
│  │  • Autenticação JWT                                                │ │
│  │  • Validação de dados                                              │ │
│  │  • Orquestração de serviços                                        │ │
│  └────────────────────────────────┬──────────────────────────────────┘ │
│                                   │                                     │
│  ┌────────────┬──────────────────┼──────────────────┬────────────────┐│
│  │            │                  │                  │                ││
│  ▼            ▼                  ▼                  ▼                ││
│ ┌──────┐  ┌──────┐          ┌──────┐          ┌──────┐             ││
│ │BioBERT│  │Llama3│          │Pipeline│         │Match-│             ││
│ │Service│  │(Opt.)│          │Hospitais│        │maker │             ││
│ │       │  │      │          │Goiás   │        │Logís.│             ││
│ └───┬───┘  └───┬──┘          └───┬────┘        └───┬──┘             ││
│     │          │                 │                 │                ││
│     └──────────┴─────────────────┴─────────────────┘                ││
│                          │                                           ││
│                          ▼                                           ││
│                  ┌───────────────┐                                   ││
│                  │  XAI Module   │                                   ││
│                  │(Explicabilidade)│                                 ││
│                  └───────────────┘                                   ││
└───────────────────────────┼──────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    BANCO DE DADOS (PostgreSQL)                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │pacientes_        │  │historico_        │  │usuarios          │     │
│  │regulacao         │  │decisoes          │  │                  │     │
│  │(33 colunas)      │  │(auditoria)       │  │(auth)            │     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────────────────────┘
```

### **Fluxo de Dados**

```
1. HOSPITAL insere paciente
   └─> POST /solicitar-regulacao
       └─> Salva em pacientes_regulacao (status: AGUARDANDO_REGULACAO)

2. REGULADOR visualiza fila
   └─> GET /pacientes-hospital-aguardando
       └─> Retorna pacientes com status AGUARDANDO_REGULACAO

3. REGULADOR processa com IA
   └─> POST /processar-regulacao
       ├─> BioBERT analisa prontuário
       ├─> Pipeline seleciona hospital
       ├─> Calcula score e risco
       └─> Salva em historico_decisoes

4. REGULADOR decide
   └─> POST /decisao-regulador
       ├─> Atualiza status (INTERNACAO_AUTORIZADA ou REGULACAO_NEGADA)
       └─> Registra auditoria

5. COORDENADOR solicita ambulância
   └─> POST /solicitar-ambulancia
       ├─> Atualiza status (EM_TRANSFERENCIA)
       └─> Define tipo_transporte e status_ambulancia

6. PÚBLICO consulta
   └─> GET /consulta-publica/paciente/{busca}
       └─> Retorna dados anonimizados (LGPD)
```

### **Inteligência Artificial - Pipeline Detalhado**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PIPELINE DE PROCESSAMENTO IA                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ENTRADA: Prontuário + CID + Especialidade + Cidade                    │
│     │                                                                   │
│     ▼                                                                   │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ 1. BioBERT (Análise NLP Médica)                                  │  │
│  │    • Tokenização com vocabulário médico                          │  │
│  │    • Extração de entidades: sintomas, anatomia, medicamentos     │  │
│  │    • Score de confiança: 0.0 a 1.0                               │  │
│  │    • Tempo: ~1-2 segundos                                        │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│     │                                                                   │
│     ▼                                                                   │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ 2. Análise de CID e Sintomas                                     │  │
│  │    • Mapeamento de CIDs críticos (I21, I46, S06, etc.)           │  │
│  │    • Detecção de sintomas críticos (dor torácica, etc.)          │  │
│  │    • Cálculo de score: 1-10                                      │  │
│  │    • Classificação: VERMELHO/AMARELO/VERDE                       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│     │                                                                   │
│     ▼                                                                   │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ 3. Pipeline Hospitais Goiás                                      │  │
│  │    • Filtro por especialidade disponível                         │  │
│  │    • Hierarquia SUS (UPA → Regional → Referência)                │  │
│  │    • Cálculo de distância (Haversine)                            │  │
│  │    • Seleção do hospital mais adequado                           │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│     │                                                                   │
│     ▼                                                                   │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ 4. Matchmaker Logístico                                          │  │
│  │    • Tipo de ambulância (USA/USB/AEROMÉDICO)                     │  │
│  │    • Cálculo de rota otimizada                                   │  │
│  │    • Tempo estimado de transporte                                │  │
│  │    • Previsão de disponibilidade de vaga                         │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│     │                                                                   │
│     ▼                                                                   │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ 5. Llama 3 (Opcional - Contexto Adicional)                       │  │
│  │    • Análise contextual do caso                                  │  │
│  │    • Geração de justificativa técnica                            │  │
│  │    • Recomendações adicionais                                    │  │
│  │    • Fallback: Sistema funciona sem Llama                        │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│     │                                                                   │
│     ▼                                                                   │
│  SAÍDA: JSON Estruturado                                               │
│  {                                                                      │
│    "analise_decisoria": {                                              │
│      "score_prioridade": 8,                                            │
│      "classificacao_risco": "VERMELHO",                                │
│      "unidade_destino_sugerida": "HOSPITAL ESTADUAL...",              │
│      "justificativa_clinica": "Paciente com IAM..."                   │
│    },                                                                  │
│    "biobert_usado": true,                                              │
│    "matchmaker_logistico": {...},                                      │
│    "tempo_processamento": 2.5                                          │
│  }                                                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### **Segurança e LGPD**

#### Autenticação e Autorização
- **JWT (JSON Web Tokens)** com expiração de 8 horas
- **Roles**: REGULADOR, HOSPITAL, ADMIN
- **Bcrypt** para hash de senhas
- **Bearer Token** em headers HTTP

#### Anonimização de Dados (LGPD Art. 12)
```python
# Exemplos de anonimização
Nome: "João da Silva Santos" → "J*** d* S*** S***"
CPF: "123.456.789-01" → "***.***.*89-01"
Telefone: "(62) 98765-4321" → "(62) *****-**21"
```

#### Auditoria (LGPD Art. 37)
- Todas as decisões registradas em `historico_decisoes`
- Timestamp de cada ação
- Responsável identificado
- Decisão da IA preservada
- Decisão final do regulador registrada

---

## **Impacto e Resultados Esperados**

### **Redução de Tempo**
- **Análise de prontuário**: De 30-60 min → 2-5 min (90% redução)
- **Tomada de decisão**: De 2-4 horas → 15-30 min (87% redução)
- **Processamento da fila**: Redução de 70% no tempo médio

### **Melhoria na Precisão**
- **Padronização**: Critérios uniformes baseados em evidências
- **Redução de erros**: Validação automática de dados
- **Rastreabilidade**: Histórico completo de decisões

### **Transparência**
- **Dashboard público**: Cidadãos podem acompanhar a situação
- **Métricas em tempo real**: Gestores têm visibilidade total
- **Relatórios automáticos**: Dados para tomada de decisão estratégica

### **Economia de Recursos**
- **Redução de custos operacionais**: Menos tempo de reguladores
- **Otimização de ambulâncias**: Rotas mais eficientes
- **Melhor uso de leitos**: Alocação inteligente de recursos

---

## 🚀 **Como Executar a Aplicação**

### **🐳 Opção 1: Docker (Recomendado para Produção)**

A forma mais fácil de rodar o sistema completo é usando Docker. Todos os serviços (PostgreSQL, Redis, Ollama/Llama 3, Backend, MS-Ingestao, Frontend) são iniciados automaticamente.

#### Pré-requisitos Docker
- **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop/)
- **8GB+ RAM** (recomendado 16GB para Llama 3)
- **20GB+ espaço em disco** (para imagens e modelos)

#### Iniciar com Docker (Windows)
```powershell
# Clone o repositório
git clone https://github.com/LiviaMor/regulacao-ms.git
cd regulacao-ms

# Iniciar todos os serviços
.\start-docker.ps1 up

# Aguarde ~10 minutos na primeira execução (download de imagens e modelos)
```

#### Iniciar com Docker (Linux/Mac)
```bash
# Clone o repositório
git clone https://github.com/LiviaMor/regulacao-ms.git
cd regulacao-ms

# Dar permissão ao script
chmod +x start-docker.sh

# Iniciar todos os serviços
./start-docker.sh up
```

#### Acessar o Sistema
Após iniciar, acesse:
- **Frontend**: http://localhost:8082
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

#### Comandos Docker Úteis
```bash
# Ver status dos containers
.\start-docker.ps1 status

# Ver logs em tempo real
.\start-docker.ps1 logs

# Parar todos os serviços
.\start-docker.ps1 down

# Reconstruir imagens (após alterações)
.\start-docker.ps1 rebuild

# Limpar tudo (volumes inclusos)
.\start-docker.ps1 clean
```

---

### **💻 Opção 2: Execução Local (Desenvolvimento)**

### **Pré-requisitos**

#### Software Necessário
- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **PostgreSQL 12+** - [Download](https://www.postgresql.org/download/)
- **Git** - [Download](https://git-scm.com/)

#### Verificar Instalações
```bash
python --version  # Deve ser >= 3.8
node --version    # Deve ser >= 16
npm --version     # Deve ser >= 8
psql --version    # Deve ser >= 12
```

---

### **📦 Instalação Rápida (Desenvolvimento)**

#### **PASSO 1: Clone o Repositório**
```bash
git clone https://github.com/LiviaMor/regulacao-ms.git
cd regulacao-ms
```

#### **PASSO 2: Configurar Backend**

##### 2.1 Instalar Dependências Python
```bash
cd backend
pip install -r requirements.txt
```

##### 2.2 Configurar Banco de Dados (PostgreSQL - Recomendado)

**Windows:**
```powershell
# Criar banco de dados
psql -U postgres
CREATE DATABASE regulacao_db;
\q
```

**Linux/Mac:**
```bash
# Criar banco de dados
sudo -u postgres psql
CREATE DATABASE regulacao_db;
\q
```

Edite o arquivo `backend/.env`:
```bash
# Configurar PostgreSQL
DATABASE_URL=postgresql://postgres:1904@localhost:5432/regulacao_db
```

##### 2.3 Criar Tabelas e Colunas
```bash
# Executar migração completa
python migrar_banco_completo.py

# Verificar se tudo foi criado
python verificar_colunas.py
```

**Saída Esperada:**
```
✅ Colunas adicionadas: 10
📊 Total de colunas agora: 33
🎉 Todas as colunas críticas estão presentes!
✅ Banco de dados pronto para uso!
```

#### **PASSO 3: Iniciar Sistema Completo**

> **⚠️ IMPORTANTE**: O sistema completo requer 3 serviços rodando simultaneamente!

##### Opção A: Script Automático (Recomendado)
```bash
cd backend
python start_all_services.py
```

Este script inicia automaticamente:
- Backend Principal (porta 8000)
- MS-Ingestao (porta 8004)
- Sincronização automática de dados

**Saída Esperada:**
```
[SISTEMA] ✅ MS-Ingestao está rodando!
[SISTEMA] ✅ Backend Principal está rodando!
[SISTEMA] ✅ Sincronização: 10 registros ingeridos com sucesso
[SISTEMA] ✅ SISTEMA INICIADO COM SUCESSO!
```

##### Opção B: Inicialização Manual (3 Terminais)

###### Terminal 1 - Backend Principal (porta 8000)
```bash
cd backend
python main_unified.py
```

**Saída Esperada:**
```
INFO:biobert_service:🧬 Carregando modelo BioBERT...
INFO:biobert_service:✅ BioBERT carregado
INFO:main_unified:✅ Módulo XAI carregado
INFO:     Uvicorn running on http://0.0.0.0:8000
```

###### Terminal 2 - MS-Ingestao (porta 8004)
```bash
cd backend/microservices/ms-ingestao
python main.py
```

**Saída Esperada:**
```
INFO: MS-Ingestao iniciado com sucesso - Memória de Curto Prazo ativa
INFO:     Uvicorn running on http://0.0.0.0:8004
```

###### Terminal 3 - Sincronizar Dados de Ocupação
```bash
# Sincronizar dados com MS-Ingestao (executar após ambos serviços estarem rodando)
curl -X POST http://localhost:8000/sincronizar-ocupacao
```

**Saída Esperada:**
```json
{
  "status": "ok",
  "message": "10 registros ingeridos com sucesso",
  "registros_enviados": 10
}
```

##### 3.4 Verificar Health do Sistema
```bash
curl http://localhost:8000/health
```

**Saída Esperada:**
```json
{
  "status": "healthy",
  "biobert_disponivel": true,
  "matchmaker_disponivel": true,
  "xai_disponivel": true,
  "ms_ingestao": {
    "status": "online",
    "url": "http://localhost:8004"
  }
}
```

##### 3.5 Reconectar MS-Ingestao (se necessário)
Se o MS-Ingestao foi iniciado depois do backend, force a reconexão:
```bash
curl -X POST http://localhost:8000/ms-ingestao/reconectar
```

#### **PASSO 4: Configurar Frontend**

##### 4.1 Terminal 3 - Frontend (porta 8082)
```bash
cd regulacao-app
npm install
npm start
```

**Saída Esperada:**
```
Starting Metro Bundler
› Web is waiting on http://localhost:8082
```

##### 4.2 Abrir no Navegador
```
http://localhost:8082
```

#### **PASSO 5: Testar Sistema Completo**
```bash
# Na raiz do projeto
python teste_fluxo_completo_validacao.py
```

---

### **📊 Arquitetura de Serviços**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SISTEMA COMPLETO                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    │
│  │   FRONTEND      │    │  BACKEND        │    │  MS-INGESTAO    │    │
│  │   (Expo/React)  │───▶│  (FastAPI)      │───▶│  (FastAPI)      │    │
│  │   porta 8082    │    │  porta 8000     │    │  porta 8004     │    │
│  └─────────────────┘    └────────┬────────┘    └────────┬────────┘    │
│                                  │                      │              │
│                                  └──────────┬───────────┘              │
│                                             │                          │
│                                  ┌──────────▼──────────┐               │
│                                  │    PostgreSQL       │               │
│                                  │    porta 5432       │               │
│                                  └─────────────────────┘               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### **Serviços e Portas**

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| **Backend Principal** | 8000 | API REST, BioBERT, Matchmaker, XAI |
| **MS-Ingestao** | 8004 | Memória de curto prazo, tendências de ocupação |
| **Frontend** | 8082 | Interface React Native/Expo |
| **PostgreSQL** | 5432 | Banco de dados |

### **Endpoints Principais**

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/health` | GET | Status do sistema e serviços |
| `/dashboard/leitos` | GET | Dashboard público com ocupação |
| `/sincronizar-ocupacao` | POST | Sincroniza dados com MS-Ingestao |
| `/login` | POST | Autenticação JWT |
| `/processar-regulacao` | POST | Análise IA de paciente |
| `/decisao-regulador` | POST | Registrar decisão do regulador |
| `/solicitar-ambulancia` | POST | Solicitar ambulância |
| `/consulta-paciente` | POST | Consulta pública de paciente |

---

### **🐳 Instalação com Docker (Produção)**

#### **Opção 1: Docker Compose (Recomendado)**

##### 1.1 Subir Todos os Serviços
```bash
cd backend
docker-compose up -d
```

##### 1.2 Verificar Status
```bash
docker-compose ps
```

##### 1.3 Ver Logs
```bash
docker-compose logs -f
```

##### 1.4 Parar Serviços
```bash
docker-compose down
```

#### **Opção 2: Build Manual**

##### 2.1 Build da Imagem Backend
```bash
cd backend
docker build -t regulacao-backend:latest -f Dockerfile.unified .
```

##### 2.2 Executar Container
```bash
docker run -d \
  --name regulacao-backend \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://postgres:1904@host.docker.internal:5432/regulacao_db \
  regulacao-backend:latest
```

##### 2.3 Build do Frontend (Web)
```bash
cd regulacao-app
npm run build:web
```

---

### **🔧 Configuração Avançada**

#### **Configurar Llama 3 (Opcional)**

O sistema funciona sem Llama 3, mas para melhor performance:

```bash
# Instalar Ollama
# Windows: https://ollama.ai/download
# Linux: curl https://ollama.ai/install.sh | sh

# Baixar modelo Llama 3
ollama pull llama3

# Verificar se está rodando
curl http://localhost:11434/api/tags
```

#### **Configurar Redis (Opcional)**

Para cache e filas assíncronas:

```bash
# Windows: https://github.com/microsoftarchive/redis/releases
# Linux: sudo apt-get install redis-server

# Iniciar Redis
redis-server

# Testar
redis-cli ping
```

---

### **📱 Build para Produção**

#### **Backend - Build Docker**

##### 1. Criar Imagem de Produção
```bash
cd backend
docker build -t regulacao-backend:v1.0.0 -f Dockerfile.unified .
```

##### 2. Testar Imagem
```bash
docker run -p 8000:8000 regulacao-backend:v1.0.0
```

##### 3. Push para Registry (Opcional)
```bash
# Docker Hub
docker tag regulacao-backend:v1.0.0 seu-usuario/regulacao-backend:v1.0.0
docker push seu-usuario/regulacao-backend:v1.0.0

# AWS ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker tag regulacao-backend:v1.0.0 123456789.dkr.ecr.us-east-1.amazonaws.com/regulacao-backend:v1.0.0
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/regulacao-backend:v1.0.0
```

#### **Frontend - Build Web**

##### 1. Build para Produção
```bash
cd regulacao-app
npm run build:web
```

##### 2. Servir Build
```bash
# Instalar servidor estático
npm install -g serve

# Servir build
serve -s web-build -p 3000
```

##### 3. Deploy para Vercel/Netlify
```bash
# Vercel
npm install -g vercel
vercel --prod

# Netlify
npm install -g netlify-cli
netlify deploy --prod --dir=web-build
```

#### **Frontend - Build Mobile**

##### Android (APK)
```bash
cd regulacao-app

# Build APK
expo build:android

# Ou com EAS Build
eas build --platform android
```

##### iOS (IPA)
```bash
cd regulacao-app

# Build IPA (requer Mac)
expo build:ios

# Ou com EAS Build
eas build --platform ios
```

---

### **🌐 Deploy em Servidor**

#### **Opção 1: VPS (Ubuntu/Debian)**

##### 1. Preparar Servidor
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install -y python3 python3-pip postgresql nginx

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

##### 2. Clonar Repositório
```bash
cd /opt
sudo git clone https://github.com/LiviaMor/regulacao-ms.git
cd regulacao-ms
```

##### 3. Configurar Banco de Dados
```bash
sudo -u postgres psql
CREATE DATABASE regulacao_db;
CREATE USER regulacao WITH PASSWORD 'senha_segura';
GRANT ALL PRIVILEGES ON DATABASE regulacao_db TO regulacao;
\q
```

##### 4. Iniciar com Docker Compose
```bash
cd backend
sudo docker-compose up -d
```

##### 5. Configurar Nginx
```bash
sudo nano /etc/nginx/sites-available/regulacao

# Adicionar configuração:
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Ativar site
sudo ln -s /etc/nginx/sites-available/regulacao /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

##### 6. Configurar SSL (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com
```

#### **Opção 2: AWS (EC2 + RDS)**

##### 1. Criar Instância EC2
- AMI: Ubuntu 22.04 LTS
- Tipo: t3.medium (2 vCPU, 4 GB RAM)
- Storage: 30 GB SSD

##### 2. Criar RDS PostgreSQL
- Engine: PostgreSQL 14
- Tipo: db.t3.micro
- Storage: 20 GB

##### 3. Deploy Backend
```bash
# Conectar via SSH
ssh -i sua-chave.pem ubuntu@ec2-ip

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clonar e iniciar
git clone https://github.com/LiviaMor/regulacao-ms.git
cd regulacao-ms/backend
sudo docker-compose up -d
```

##### 4. Deploy Frontend (S3 + CloudFront)
```bash
# Build
cd regulacao-app
npm run build:web

# Upload para S3
aws s3 sync web-build/ s3://seu-bucket-frontend/

# Configurar CloudFront
# Console AWS → CloudFront → Create Distribution
```

---

### **🔍 Troubleshooting**

#### Backend não inicia
```bash
# Verificar porta 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Verificar logs
tail -f backend/logs/app.log

# Verificar banco de dados
psql -U postgres -d regulacao_db -c "SELECT 1"
```

#### Frontend não carrega
```bash
# Limpar cache
cd regulacao-app
rm -rf node_modules
npm install

# Verificar porta 8082
netstat -ano | findstr :8082  # Windows
lsof -i :8082                 # Linux/Mac
```

#### BioBERT não carrega
```bash
# Verificar instalação PyTorch
python -c "import torch; print(torch.__version__)"

# Reinstalar transformers
pip install --upgrade transformers torch
```

#### Erro de conexão com banco
```bash
# Verificar PostgreSQL
psql -U postgres -c "SELECT version()"

# Verificar .env
cat backend/.env | grep DATABASE_URL

# Testar conexão
python backend/verificar_colunas.py
```

---

## **🎯 Demonstração da Solução**

### **Credenciais de Acesso**
```
Email: admin@sesgo.gov.br
Senha: admin123
Tipo: ADMIN (acesso completo)
```

### **Endpoints da API**

#### Públicos (sem autenticação)
- **Root**: http://localhost:8000/
- **Health Check**: http://localhost:8000/health
- **Dashboard Público**: http://localhost:8000/dashboard/leitos
- **Consulta Paciente**: http://localhost:8000/consulta-publica/paciente/{protocolo_ou_cpf}
- **Documentação Interativa**: http://localhost:8000/docs

#### Autenticados (requer Bearer Token)
- **Login**: POST http://localhost:8000/login
- **Solicitar Regulação**: POST http://localhost:8000/solicitar-regulacao
- **Fila de Regulação**: GET http://localhost:8000/pacientes-hospital-aguardando
- **Processar com IA**: POST http://localhost:8000/processar-regulacao
- **Decisão Regulador**: POST http://localhost:8000/decisao-regulador
- **Pacientes Transferência**: GET http://localhost:8000/pacientes-transferencia
- **Solicitar Ambulância**: POST http://localhost:8000/solicitar-ambulancia
- **Atualizar Status Ambulância**: POST http://localhost:8000/atualizar-status-ambulancia

### **Frontend - Abas Disponíveis**

#### 1. Dashboard (Público)
- Visualização em tempo real
- Ocupação de hospitais
- Métricas gerais

#### 2. Hospital (Público)
- Inserir novo paciente
- Campos obrigatórios: Nome, CPF, CID, Prontuário
- Upload de documentos (futuro)

#### 3. Regulação (Autenticado)
- Login necessário
- Fila de pacientes aguardando
- Processar com IA (BioBERT + Llama)
- Aprovar/Negar/Alterar decisões

#### 4. Transferência (Autenticado)
- Login necessário
- Pacientes autorizados
- Solicitar ambulância (USA/USB/AEROMÉDICO)
- Acompanhar status da ambulância

#### 5. Consulta (Público)
- Busca por protocolo ou CPF
- Dados anonimizados (LGPD)
- Status em tempo real
- Histórico de movimentações

#### 6. Auditoria (Autenticado)
- Métricas de impacto
- Transparência do modelo
- Relatórios de decisões

### **Fluxo Completo de Teste**

#### 1. Inserir Paciente (Área Hospitalar)
```bash
curl -X POST http://localhost:8000/solicitar-regulacao \
  -H "Content-Type: application/json" \
  -d '{
    "protocolo": "REG-2025-TEST-001",
    "nome_completo": "João da Silva Santos",
    "cpf": "12345678901",
    "especialidade": "CARDIOLOGIA",
    "cid": "I21.0",
    "cid_desc": "Infarto Agudo do Miocárdio",
    "prontuario_texto": "Paciente com dor torácica intensa",
    "cidade_origem": "GOIANIA"
  }'
```

#### 2. Fazer Login
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@sesgo.gov.br",
    "senha": "admin123"
  }'
```

#### 3. Processar com IA
```bash
curl -X POST http://localhost:8000/processar-regulacao \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "protocolo": "REG-2025-TEST-001",
    "especialidade": "CARDIOLOGIA",
    "cid": "I21.0"
  }'
```

#### 4. Aprovar Regulação
```bash
curl -X POST http://localhost:8000/decisao-regulador \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "protocolo": "REG-2025-TEST-001",
    "decisao_regulador": "AUTORIZADA",
    "unidade_destino": "HOSPITAL ESTADUAL DR ALBERTO RASSI",
    "tipo_transporte": "USA",
    "decisao_ia_original": {}
  }'
```

#### 5. Solicitar Ambulância
```bash
curl -X POST http://localhost:8000/solicitar-ambulancia \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "protocolo": "REG-2025-TEST-001",
    "tipo_transporte": "USA"
  }'
```

#### 6. Consultar Publicamente
```bash
curl http://localhost:8000/consulta-publica/paciente/REG-2025-TEST-001
```

### **Funcionalidades Demonstráveis**

#### **1. Dashboard Público**
- ✅ Visualização em tempo real
- ✅ 10 hospitais estaduais monitorados
- ✅ Taxa de ocupação por hospital
- ✅ Mapa de calor por especialidade
- ✅ Dados atualizados automaticamente

#### **2. Análise com IA**
```json
{
  "analise_decisoria": {
    "score_prioridade": 8,
    "classificacao_risco": "VERMELHO",
    "unidade_destino_sugerida": "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG",
    "justificativa_clinica": "Paciente com IAM (I21.0) necessita UTI cardiológica"
  },
  "biobert_usado": true,
  "matchmaker_logistico": {
    "acionar_ambulancia": true,
    "tipo_transporte": "USA",
    "previsao_vaga_h": "2-4 horas"
  },
  "tempo_processamento": 2.5
}
```

#### **3. Interface do Regulador**
- ✅ **CardDecisaoIA**: Visualização clara da decisão
- ✅ **Fila inteligente**: Ordenação por prioridade
- ✅ **Autorização rápida**: Aprovar/Negar/Alterar
- ✅ **Auditoria automática**: Todas as decisões registradas

#### **4. Gestão de Ambulâncias**
- ✅ Solicitar ambulância (USA/USB/AEROMÉDICO)
- ✅ Acompanhar status em tempo real
- ✅ Fluxo: SOLICITADA → A_CAMINHO → NO_LOCAL → TRANSPORTANDO → CONCLUIDA
- ✅ Notificações de mudança de status

#### **5. Consulta Pública (LGPD)**
- ✅ Busca por protocolo ou CPF
- ✅ Dados pessoais anonimizados
- ✅ Status em tempo real
- ✅ Histórico completo de movimentações
- ✅ Transparência total do processo

---

## **Impacto e Resultados Esperados**

### **Redução de Tempo**
- **Análise de prontuário**: De 30-60 min → 2-5 min
- **Tomada de decisão**: De 2-4 horas → 15-30 min
- **Processamento da fila**: Redução de 70% no tempo médio

### **Melhoria na Precisão**
- **Padronização**: Critérios uniformes baseados em evidências
- **Redução de erros**: Validação automática de dados
- **Rastreabilidade**: Histórico completo de decisões

### **Transparência**
- **Dashboard público**: Cidadãos podem acompanhar a situação
- **Métricas em tempo real**: Gestores têm visibilidade total
- **Relatórios automáticos**: Dados para tomada de decisão estratégica

---

## **Detalhes Técnicos da IA**

### **Processamento de Linguagem Natural**
```python
# Exemplo de processamento com BioBERT
def extrair_entidades_biobert(prontuario_texto: str) -> str:
    inputs = biobert_tokenizer(prontuario_texto, return_tensors="pt")
    outputs = biobert_model(**inputs)
    # Análise de embeddings médicos especializados
    return analise_clinica_estruturada
```

### **Geração de Decisões**
```python
# Prompt estruturado para Llama3
prompt = f"""
### ESPECIALISTA SÊNIOR DE REGULAÇÃO MÉDICA SES-GO
Analise o caso e forneça decisão estruturada:

CONTEXTO DO PACIENTE:
- CID-10: {cid} ({descricao})
- Quadro Clínico: {biobert_analysis}
- Disponibilidade da Rede: {dados_rede}

RESPOSTA EM JSON:
{{
  "analise_decisoria": {{
    "score_prioridade": [1-10],
    "classificacao_risco": "VERMELHO|AMARELO|VERDE",
    "justificativa_clinica": "Explicação técnica"
  }}
}}
"""
```

---

## **Roadmap e Próximos Passos**

### **Fase 1 - MVP (Atual)**
- ✅ Backend com microserviços
- ✅ Frontend multiplataforma
- ✅ IA básica com BioBERT + Llama3
- ✅ Dashboard público

### **Fase 2 - Expansão (3-6 meses)**
- 🔄 OCR para prontuários digitalizados
- 🔄 Integração com sistemas hospitalares
- 🔄 Métricas avançadas e relatórios
- 🔄 App mobile nativo

### **📅 Fase 3 - Inteligência Avançada (6-12 meses)**
- 🔄 Machine Learning preditivo
- 🔄 Análise de imagens médicas
- 🔄 Integração com IoT hospitalar
- 🔄 IA conversacional para reguladores

---

## 🏆 **Diferenciais Competitivos**

### **🎯 Foco na Saúde Pública**
- Desenvolvido especificamente para o SUS
- Dados reais da SES-GO
- Compliance com regulamentações médicas

### **🤖 IA Especializada**
- BioBERT treinado em textos médicos
- Prompts otimizados para regulação
- Validação humana obrigatória

### **🔓 Código Aberto**
- Transparência total do algoritmo
- Possibilidade de auditoria
- Adaptável para outros estados

### **💰 Custo-Benefício**
- Infraestrutura local (sem dependência de nuvem)
- Tecnologias open source
- ROI mensurável em redução de tempo

---

## 📞 **Contato e Suporte**

### **👩‍💻 Desenvolvedora Principal**
**Livia Mor**
- 📧 Email: liviamor01@hotmail.com
- 💼 LinkedIn: [Livia Mor](https://linkedin.com/in/liviamor)
- 🐙 GitHub: [@LiviaMor](https://github.com/LiviaMor)

### **🏛️ Instituição Parceira**
**Secretaria de Estado da Saúde de Goiás (SES-GO)**
- 🌐 Site: https://www.saude.go.gov.br
- 📧 Email: suporte@sesgo.gov.br
- 📍 Endereço: Av. Anhanguera, 5195 - Setor Coimbra, Goiânia - GO

### **📚 Documentação e Recursos**

#### Documentação Técnica
- 📖 **README.md** - Este arquivo (visão geral)
- 📊 **ANALISE_COMPLETA_SISTEMA.md** - Análise técnica detalhada
- 🔄 **DIAGRAMA_FLUXO_COMPLETO.md** - Fluxo visual completo
- ✅ **CHECKLIST_VALIDACAO_FINAL.md** - Checklist de validação
- 🧪 **COMO_TESTAR_SISTEMA_COMPLETO.md** - Guia de testes
- 🚑 **FLUXO_TRANSFERENCIA_CORRIGIDO.md** - Fluxo de transferência

#### API e Desenvolvimento
- 🔌 **API Docs (Swagger)**: http://localhost:8000/docs
- 📡 **API Docs (ReDoc)**: http://localhost:8000/redoc
- 🏥 **Dashboard Público**: http://localhost:8000/dashboard/leitos
- ❤️ **Health Check**: http://localhost:8000/health

#### Repositório
- 📦 **GitHub**: https://github.com/LiviaMor/regulacao-ms
- 🐛 **Issues**: https://github.com/LiviaMor/regulacao-ms/issues
- 🔀 **Pull Requests**: https://github.com/LiviaMor/regulacao-ms/pulls

### **🆘 Suporte e Ajuda**

#### Reportar Bugs
1. Acesse: https://github.com/LiviaMor/regulacao-ms/issues
2. Clique em "New Issue"
3. Descreva o problema com detalhes
4. Inclua logs e screenshots se possível

#### Solicitar Funcionalidades
1. Acesse: https://github.com/LiviaMor/regulacao-ms/issues
2. Clique em "New Issue"
3. Use o template "Feature Request"
4. Descreva a funcionalidade desejada

#### Contribuir com o Projeto
1. Fork o repositório
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit suas mudanças: `git commit -m 'Adiciona nova funcionalidade'`
4. Push para a branch: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

---

## 📄 **Licença**

Este projeto está licenciado sob a **Licença MIT** - veja o arquivo [LICENSE](LICENSE) para detalhes.

### MIT License

```
Copyright (c) 2024 Livia Mor

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### **Modelos de IA - Licenças**

| Modelo | Licença | Uso Comercial | Modificação |
|--------|---------|---------------|-------------|
| BioBERT | Apache 2.0 | ✅ Permitido | ✅ Permitido |
| Bio_ClinicalBERT | MIT | ✅ Permitido | ✅ Permitido |
| Llama 3 | Llama 3 License | ✅ Permitido* | ✅ Permitido |

*Sujeito aos termos da Meta AI

---

## 🏆 **Agradecimentos**

### **Instituições**
- **FAPEG** - Fundação de Amparo à Pesquisa do Estado de Goiás
- **SES-GO** - Secretaria de Estado da Saúde de Goiás
- **Governo de Goiás** - Apoio institucional

### **Comunidade Open Source**
- **HuggingFace** - Plataforma de modelos de IA
- **Meta AI** - Llama 3
- **DMIS Lab (Korea University)** - BioBERT
- **FastAPI** - Framework web moderno
- **Expo** - Plataforma de desenvolvimento mobile

### **Inspirações e Referências**
- Sistema de Regulação do SUS
- Protocolos de Manchester
- Diretrizes da ANVISA
- Legislação LGPD (Lei 13.709/2018)

---

## 🌟 **Citação Acadêmica**

Se você usar este projeto em pesquisa acadêmica, por favor cite:

```bibtex
@software{regulacao_ses_go_2024,
  author = {Mor, Livia},
  title = {Sistema de Regulação Autônoma SES-GO: PAIC-Regula},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/LiviaMor/regulacao-ms},
  note = {Sistema de IA Aberta para Otimização da Regulação Médica}
}
```

---

## 📊 **Estatísticas do Projeto**

### **Código**
- **Linhas de Código**: ~15.000+
- **Arquivos Python**: 30+
- **Componentes React**: 20+
- **Endpoints API**: 18
- **Testes**: 10+ scripts

### **Documentação**
- **Páginas de Documentação**: 10+
- **Diagramas**: 5+
- **Exemplos de Código**: 50+

### **Tecnologias**
- **Linguagens**: Python, TypeScript, SQL
- **Frameworks**: FastAPI, React Native, Expo
- **Banco de Dados**: PostgreSQL
- **IA**: BioBERT, Llama 3
- **DevOps**: Docker, Docker Compose

---

<div align="center">

## 🌟 **Transformando a Saúde Pública com Inteligência Artificial**

### **Sistema de Regulação Autônoma SES-GO**
*Desenvolvido com ❤️ para o Prêmio FAPEG de IA Aberta*

![Goiás](https://img.shields.io/badge/Goiás-Inovação%20em%20Saúde-green?style=for-the-badge)
![IA](https://img.shields.io/badge/IA-Futuro%20da%20Medicina-blue?style=for-the-badge)
![Open Source](https://img.shields.io/badge/Open%20Source-100%25-orange?style=for-the-badge)

### **⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!**

[![GitHub stars](https://img.shields.io/github/stars/LiviaMor/regulacao-ms?style=social)](https://github.com/LiviaMor/regulacao-ms/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/LiviaMor/regulacao-ms?style=social)](https://github.com/LiviaMor/regulacao-ms/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/LiviaMor/regulacao-ms?style=social)](https://github.com/LiviaMor/regulacao-ms/watchers)

---

**Última Atualização**: 27 de Dezembro de 2024  
**Versão**: 1.0.0  
**Status**: ✅ Produção

</div>