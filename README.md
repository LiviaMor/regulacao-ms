
[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&pause=1000&width=435&lines=LIFE+IA+)](https://git.io/typing-svg)

# LIFE IA - Regulação Autônoma

### Modelos de IA
![BioBERT](https://img.shields.io/badge/🧬_BioBERT-v1.1_(60%25)-FF6F00?style=for-the-badge)
![Llama](https://img.shields.io/badge/🦙_Llama_3-8B_(10%25)-7C3AED?style=for-the-badge)
![Tesseract](https://img.shields.io/badge/📄_Tesseract-OCR_(30%25)-4285F4?style=for-the-badge)

### Tecnologias
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![React Native](https://img.shields.io/badge/React_Native-Expo-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=for-the-badge&logo=typescript&logoColor=white)

### Conformidade
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Open Source](https://img.shields.io/badge/IA-100%25_Aberta-brightgreen?style=for-the-badge)
![LGPD](https://img.shields.io/badge/LGPD-Compliant-blue?style=for-the-badge)

[![FAPEG](https://img.shields.io/badge/FAPEG-Goiás%20Aberto%20IA-orange.svg)](https://fapeg.go.gov.br)


Sistema de Regulação Hospitalar Inteligente Desenvolvido para o Prêmio Goiás Aberto para IA – GO.IA - Chamada Pública FAPEG nº 34/2025 

## Desenvolvido
**Proponente:** 
```bash
Livia Moreira Rocha - Desenvolvedora Junior - Odontóloga - Experiência em Saúde Pública
```
[![LiviaMor](https://img.shields.io/badge/GitHub-LiviaMor-181717?style=flat-square&logo=github)](https://github.com/LiviaMor)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-LiviaMor-0077B5?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/liviamor/)

## Equipe
```bash
Sebastião Relson Reis da Luz - Desenvolvedor Sênior - Ampla Experiência em Retrieval-Augmented Generation
```
[![Relson](https://img.shields.io/badge/GitHub-Relson-181717?style=flat-square&logo=github)](https://github.com/relson)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Relson-0077B5?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/relson/)


## Visão Geral

O LIFE IA é uma plataforma de regulação médica que utiliza Inteligência Artificial para otimizar o fluxo de pacientes na rede hospitalar estadual de Goiás. 
O sistema integra BioBERT (análise de textos médicos), Llama 3 (interpretação contextual) e algoritmos de matchmaking logístico.

### Principais Funcionalidades

- **Dashboard Público**: Monitoramento em tempo real da ocupação hospitalar
- **Área Hospitalar**: Solicitação de regulação com upload de documentos e análise por IA
- **Área de Regulação**: Fila de pacientes com sugestões de decisão da IA
- **Área de Transferência**: Acompanhamento de ambulâncias e transferências
- **Área de Auditoria**: Registro de altas e métricas de desempenho

### Tecnologias de IA

| Modelo | Função | Peso na Confiança | Licença |
|--------|--------|-------------------|---------|
| BioBERT v1.1 | Análise de entidades médicas | 60% | Apache 2.0 |
| Llama 3 | Interpretação contextual | 10% | Meta License |
| OCR (Tesseract) | Extração de texto de documentos | 30% | Apache 2.0 |

## Requisitos

### Sistema
- Docker Desktop 4.0+
- Docker Compose 2.0+
- 8GB RAM mínimo (16GB recomendado)
- 20GB espaço em disco

### Para Desenvolvimento Local (sem Docker)
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Ollama (para Llama 3)

## Instalação Rápida (Docker - Recomendado)

### 1. Clone o repositório

```bash
git clone https://github.com/LiviaMor/regulacao-ms.git
cd regulacao-ms
```

### 2. Configure as variáveis de ambiente

```bash
cp backend/.env.example backend/.env
# Edite backend/.env com suas configurações
```

### 3. Inicie os containers

**Windows (PowerShell):**
```powershell
.\start-docker.ps1 up
```

**Linux/Mac:**
```bash
chmod +x start-docker.sh
./start-docker.sh up
```

### 4. Acesse a aplicação

| Serviço | URL |
|---------|-----|
| Frontend | http://localhost:8082 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

## Instalação Manual (Desenvolvimento)

### Backend

```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
uvicorn main_unified:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd regulacao-app
npm install
npx expo start --web --port 8082
```

### Banco de Dados

```bash
# Criar banco PostgreSQL
createdb regulacao_db

# Ou via Docker
docker run -d --name postgres-regulacao \
  -e POSTGRES_PASSWORD=1904 \
  -e POSTGRES_DB=regulacao_db \
  -p 5432:5432 postgres:15
```

## Estrutura do Projeto

```
regulacao-ms/
├── backend/                    # API FastAPI + Serviços de IA
│   ├── main_unified.py         # API principal unificada
│   ├── requirements.txt        # Dependências Python
│   ├── shared/                 # Modelos e utilitários compartilhados
│   │   └── database.py         # Modelos SQLAlchemy
│   └── microservices/          # Serviços especializados
│       └── shared/
│           ├── biobert_service.py      # Análise BioBERT
│           ├── document_ai_service.py  # OCR + IA para documentos
│           ├── matchmaker_logistico.py # Algoritmo de alocação
│           └── xai_explicabilidade.py  # Explicabilidade das decisões
├── regulacao-app/              # Frontend React Native/Expo
│   ├── app/                    # Rotas e telas (tabs)
│   └── components/             # Componentes reutilizáveis
├── docker-compose.full.yml     # Orquestração de containers
├── start-docker.ps1            # Script de inicialização (Windows)
├── start-docker.sh             # Script de inicialização (Linux/Mac)
├── PIPELINE_HOSPITAIS_GOIAS_IMPLEMENTADO.md  # Mapeamento de hospitais
├── PIPELINE_RAG_FOCADO_IMPLEMENTADO.md       # Pipeline RAG
└── Projeto Regulacao.md        # Proposta do projeto (FAPEG)
```

## Comandos Úteis

### Gerenciamento de Containers

```powershell
# Iniciar todos os serviços
.\start-docker.ps1 up

# Parar todos os serviços
.\start-docker.ps1 down

# Reiniciar
.\start-docker.ps1 down; .\start-docker.ps1 up

# Ver logs
docker logs regulacao_backend -f

# Status dos containers
docker ps
```

### Validação do Sistema

```bash
python validar_consistencia_sistema.py
```

### Banco de Dados

```bash
# Acessar PostgreSQL
docker exec -it regulacao_postgres psql -U postgres -d regulacao_db

# Verificar colunas
docker exec regulacao_postgres psql -U postgres -d regulacao_db -c "\d pacientes_regulacao"
```

## Credenciais Padrão (Desenvolvimento)

| Usuário | Senha | Perfil |
|---------|-------|--------|
| admin@sesgo.gov.br | admin123 | Administrador |

⚠️ **Altere as credenciais em produção!**

## Arquitetura

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   Backend API   │────▶│   PostgreSQL    │
│   (Expo/React)  │     │   (FastAPI)     │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐
              │ BioBERT  │ │  Llama 3 │ │   OCR    │
              │ (NLP)    │ │  (LLM)   │ │(Imagens) │
              └──────────┘ └──────────┘ └──────────┘
```

## Conformidade

- **LGPD**: Dados pessoais anonimizados em consultas públicas
- **IA Aberta**: Modelos open-source com documentação de treinamento
- **Auditabilidade**: Logs de todas as decisões da IA

## Pipeline de IA para Hospitais

O sistema utiliza um pipeline inteligente para selecionar o hospital mais adequado:

1. **Peneira de Especialidade**: Filtra hospitais pela especialidade necessária
2. **Peneira de Complexidade**: Baseado no CID, prioriza hospitais adequados
3. **Peneira de Localidade**: Prioriza hospitais regionais quando adequados

Documentação detalhada em:
- `PIPELINE_HOSPITAIS_GOIAS_IMPLEMENTADO.md`
- `PIPELINE_RAG_FOCADO_IMPLEMENTADO.md`
- `MS_INGESTAO_IMPLEMENTADO.md`

## Licença

MIT

## Suporte

Para dúvidas ou problemas, abra uma issue no repositório.
