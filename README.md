# LIFE IA - Regulação Autônoma

Sistema de Regulação Hospitalar Inteligente para a Secretaria de Estado da Saúde de Goiás (SES-GO).

## Visão Geral

O LIFE IA é uma plataforma de regulação médica que utiliza Inteligência Artificial para otimizar o fluxo de pacientes na rede hospitalar estadual de Goiás. O sistema integra BioBERT (análise de textos médicos), Llama 3 (interpretação contextual) e algoritmos de matchmaking logístico.

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
git clone https://github.com/ses-go/life-ia-regulacao.git
cd life-ia-regulacao
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
life-ia-regulacao/
├── backend/                    # API FastAPI + Serviços de IA
│   ├── main_unified.py         # API principal unificada
│   ├── shared/                 # Modelos e utilitários compartilhados
│   │   └── database.py         # Modelos SQLAlchemy
│   └── microservices/          # Serviços especializados
│       └── shared/
│           ├── biobert_service.py      # Análise BioBERT
│           ├── document_ai_service.py  # OCR + IA para documentos
│           ├── matchmaker_logistico.py # Algoritmo de alocação
│           └── xai_explicabilidade.py  # Explicabilidade das decisões
├── regulacao-app/              # Frontend React Native/Expo
│   ├── app/                    # Rotas e telas
│   └── components/             # Componentes reutilizáveis
├── docker-compose.full.yml     # Orquestração de containers
├── start-docker.ps1            # Script de inicialização (Windows)
└── start-docker.sh             # Script de inicialização (Linux/Mac)
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

Este projeto é desenvolvido para a Secretaria de Estado da Saúde de Goiás (SES-GO).
Código-fonte disponível sob licença MIT para fins de transparência e auditabilidade.

## Suporte

Para dúvidas ou problemas, abra uma issue no repositório.
