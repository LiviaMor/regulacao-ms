# 📋 DOCUMENTAÇÃO TÉCNICA - PAIC-REGULA
## Prêmio FAPEG "Goiás Aberto para IA" (GO.IA)

---

## 1. TRANSPARÊNCIA DO MODELO DE IA

### 1.1 Modelos Utilizados (100% Open Source)

| Modelo | Versão | Licença | Repositório |
|--------|--------|---------|-------------|
| **BioBERT** | v1.1 | Apache 2.0 | [dmis-lab/biobert-base-cased-v1.1](https://huggingface.co/dmis-lab/biobert-base-cased-v1.1) |
| **Bio_ClinicalBERT** | v1.0 | MIT | [emilyalsentzer/Bio_ClinicalBERT](https://huggingface.co/emilyalsentzer/Bio_ClinicalBERT) |
| **Llama 3** | 8B | Llama 3 License | [Meta AI](https://llama.meta.com/) |

### 1.2 Dados de Treinamento do BioBERT

O modelo BioBERT foi pré-treinado pela equipe DMIS Lab (Korea University) usando:

**Corpus de Treinamento:**
- **PubMed Abstracts**: 4.5 bilhões de palavras
  - Fonte: National Library of Medicine (NLM)
  - Período: 1966-2019
  - Conteúdo: Resumos de artigos científicos biomédicos
  
- **PMC Full-text Articles**: 13.5 bilhões de palavras
  - Fonte: PubMed Central
  - Conteúdo: Artigos completos de acesso aberto

**Vocabulário:**
- 28.996 tokens WordPiece
- Especializado em terminologia médica
- Baseado no vocabulário BERT original + termos biomédicos

**Referência Científica:**
```
Lee, J., Yoon, W., Kim, S., Kim, D., Kim, S., So, C. H., & Kang, J. (2020). 
BioBERT: a pre-trained biomedical language representation model for biomedical text mining. 
Bioinformatics, 36(4), 1234-1240. 
DOI: 10.1093/bioinformatics/btz682
```

### 1.3 Dados de Treinamento do Llama 3

O modelo Llama 3 foi treinado pela Meta AI usando:

- **Volume**: 15 trilhões de tokens
- **Fontes**: Dados públicos da internet (Common Crawl, Wikipedia, livros, código)
- **Filtragem**: Remoção de conteúdo tóxico e dados pessoais
- **Execução**: Local via Ollama (dados do paciente NUNCA saem do servidor)

---

## 2. METODOLOGIA DE DECISÃO (AUDITÁVEL)

### 2.1 Pipeline de Processamento

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PIPELINE DE DECISÃO AUDITÁVEL                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ENTRADA                                                                │
│  ├── Prontuário médico (texto)                                          │
│  ├── CID-10 (código da doença)                                          │
│  ├── Especialidade solicitada                                           │
│  └── Cidade de origem do paciente                                       │
│                                                                         │
│  ETAPA 1: ANÁLISE BIOBERT (NLP Médico)                                  │
│  ├── Tokenização do texto médico                                        │
│  ├── Extração de embeddings contextuais                                 │
│  ├── Identificação de entidades: sintomas, condições, anatomia          │
│  └── Score de confiança: 0.0 a 1.0                                      │
│                                                                         │
│  ETAPA 2: CLASSIFICAÇÃO DE RISCO (Baseada em CIDs)                      │
│  ├── VERMELHO (Score 8-10): I21, I46, S06, I61, I63, N17                │
│  ├── AMARELO (Score 5-7): J18, E11, I10, K92                            │
│  └── VERDE (Score 1-4): M54, M79, R10                                   │
│                                                                         │
│  ETAPA 3: SELEÇÃO DE HOSPITAL (Pipeline Goiás)                          │
│  ├── Filtro 1: Especialidade compatível                                 │
│  ├── Filtro 2: Hierarquia SUS (UPA → Regional → Referência)             │
│  ├── Filtro 3: Taxa de ocupação (< 90% preferencial)                    │
│  └── Filtro 4: Distância geodésica (Haversine)                          │
│                                                                         │
│  ETAPA 4: MATCHMAKER LOGÍSTICO                                          │
│  ├── Cálculo de rota otimizada                                          │
│  ├── Seleção de ambulância (USA para críticos, USB para demais)         │
│  ├── Tempo estimado de transporte                                       │
│  └── Detecção de protocolos especiais (óbito, transplante)              │
│                                                                         │
│  SAÍDA (JSON Estruturado)                                               │
│  ├── hospital_sugerido                                                  │
│  ├── justificativa_tecnica (texto explicativo)                          │
│  ├── score_prioridade (1-10)                                            │
│  ├── classificacao_risco (VERMELHO/AMARELO/VERDE)                       │
│  └── explicacao_xai (detalhamento dos fatores)                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Pesos dos Fatores de Decisão

| Fator | Peso | Descrição |
|-------|------|-----------|
| Especialidade Compatível | 30% | Hospital possui a especialidade necessária |
| Gravidade Clínica | 25% | Baseado no CID e sintomas detectados |
| Distância Geográfica | 20% | Menor distância = maior score |
| Ocupação do Hospital | 15% | Menor ocupação = maior score |
| Hierarquia SUS | 10% | Adequação ao nível de complexidade |

### 2.3 Fórmula de Cálculo de Distância (Haversine)

```python
def calcular_distancia_km(lat1, lon1, lat2, lon2):
    """
    Fórmula de Haversine para distância geodésica
    Considera a curvatura da Terra
    """
    r = 6371  # Raio da Terra em km
    
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    
    a = sin(dphi/2)**2 + cos(phi1) * cos(phi2) * sin(dlambda/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return r * c  # Distância em km
```

---

## 3. AUDITABILIDADE DAS DECISÕES

### 3.1 Estrutura de Registro (LGPD Compliant)

```sql
-- Tabela de histórico de decisões
CREATE TABLE historico_decisoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    protocolo VARCHAR(50) NOT NULL,
    decisao_ia JSON NOT NULL,           -- Decisão completa da IA (preservada)
    usuario_validador VARCHAR(100),     -- Email do regulador que validou
    decisao_final JSON,                 -- Decisão final (pode diferir da IA)
    tempo_processamento FLOAT,          -- Tempo em segundos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para auditoria
CREATE INDEX idx_protocolo ON historico_decisoes(protocolo);
CREATE INDEX idx_created_at ON historico_decisoes(created_at);
```

### 3.2 Endpoints de Auditoria

| Endpoint | Método | Descrição | Autenticação |
|----------|--------|-----------|--------------|
| `/consulta-paciente` | POST | Consulta pública por protocolo/CPF | Não |
| `/auditoria/paciente/{protocolo}` | GET | Histórico completo de um paciente | Sim (Regulador) |
| `/auditoria/relatorio` | GET | Relatório geral de auditoria | Sim (Admin) |
| `/transparencia-modelo` | GET | Informações sobre os modelos de IA | Não |
| `/explicar-decisao` | POST | Explicação detalhada de uma decisão | Não |
| `/metricas-impacto` | GET | Métricas de impacto do sistema | Não |

---

## 4. CONFORMIDADE LGPD

### 4.1 Medidas de Segurança Implementadas

| Medida | Implementação | Artigo LGPD |
|--------|---------------|-------------|
| Anonimização de CPF | `cpf_mascarado = "123.***.***-45"` | Art. 12 |
| Criptografia de senhas | bcrypt com 12 rounds | Art. 46 |
| Controle de acesso | JWT com roles (ADMIN, REGULADOR, HOSPITAL) | Art. 46 |
| Registro de acessos | Logs de todas as operações | Art. 37 |
| Minimização de dados | Apenas dados necessários são coletados | Art. 6, III |

### 4.2 Processamento Local

- **Llama 3**: Executa localmente via Ollama
- **BioBERT**: Carregado em memória local
- **Dados do paciente**: NUNCA enviados para APIs externas
- **Logs**: Armazenados localmente com retenção de 90 dias

---

## 5. HOSPITAIS DE GOIÁS (DADOS REAIS)

### 5.1 Coordenadas Geográficas

| Hospital | Sigla | Cidade | Latitude | Longitude |
|----------|-------|--------|----------|-----------|
| Hospital Estadual Dr. Alberto Rassi | HGG | Goiânia | -16.679 | -49.255 |
| Hospital de Urgências Dr. Valdemiro Cruz | HUGO | Goiânia | -16.705 | -49.261 |
| Hospital de Urgências de Goiânia | HUGOL | Goiânia | -16.643 | -49.339 |
| Hospital de Doenças Tropicais | HDT | Goiânia | -16.685 | -49.278 |
| Hospital Materno Infantil | HEMU | Goiânia | -16.685 | -49.278 |
| Hospital de Aparecida de Goiânia | HEAPA | Aparecida | -16.823 | -49.244 |
| Hospital de Trindade | HUTRIN | Trindade | -16.647 | -49.347 |
| Hospital de Formosa | HEF | Formosa | -15.541 | -47.339 |
| Hospital de Jataí | HEJ | Jataí | -17.881 | -51.714 |
| Hospital do Centro Norte | HECNG | Uruaçu | -14.520 | -49.141 |
| Hospital de Anápolis | HEA | Anápolis | -16.327 | -48.953 |

### 5.2 Especialidades por Hospital

| Hospital | Especialidades |
|----------|----------------|
| HGG | Clínica Médica, Cirurgia, UTI Adulto, Cardiologia |
| HUGO | Trauma, Neurocirurgia, UTI Trauma, Ortopedia |
| HUGOL | Urgência, Cirurgia Vascular, Neurologia |
| HDT | Infectologia, Doenças Tropicais |
| HEMU | Obstetrícia, Ginecologia, UTI Neonatal |

---

## 6. MÉTRICAS DE IMPACTO ESPERADO

### 6.1 Indicadores de Performance

| Métrica | Antes da IA | Com IA | Redução |
|---------|-------------|--------|---------|
| Tempo médio de análise | 30-60 min | 2-5 min | 90% |
| Tempo de regulação | 4-8 horas | 1-2 horas | 70% |
| Erros de encaminhamento | ~15% | < 5% | 67% |
| Satisfação do regulador | N/A | A medir | - |

### 6.2 Impacto Econômico Estimado

- **Economia de tempo**: 70% de redução no tempo de regulação
- **Otimização de leitos**: Aumento de 15% na rotatividade
- **Redução de custos**: Estimativa de R$ 45.000/mês em eficiência operacional

---

## 7. STACK TECNOLÓGICA

### 7.1 Backend

| Tecnologia | Versão | Função |
|------------|--------|--------|
| Python | 3.11+ | Linguagem principal |
| FastAPI | 0.100+ | Framework web |
| SQLAlchemy | 2.0+ | ORM |
| PyTorch | 2.0+ | Deep Learning |
| Transformers | 4.30+ | Modelos NLP |

### 7.2 Frontend

| Tecnologia | Versão | Função |
|------------|--------|--------|
| React Native | 0.72+ | Framework mobile |
| Expo | 49+ | Plataforma de desenvolvimento |
| TypeScript | 5.0+ | Tipagem estática |

### 7.3 Infraestrutura

| Tecnologia | Função |
|------------|--------|
| Docker | Containerização |
| Kubernetes | Orquestração |
| PostgreSQL | Banco de dados (produção) |
| SQLite | Banco de dados (desenvolvimento) |
| Ollama | Servidor LLM local |

---

## 8. COMO EXECUTAR

### 8.1 Requisitos

```bash
# Python 3.11+
python --version

# Node.js 18+
node --version

# Docker (opcional)
docker --version
```

### 8.2 Instalação

```bash
# Clone o repositório
git clone https://github.com/LiviaMor/regulacao-ms.git
cd regulacao-ms

# Instale dependências Python
pip install -r backend/requirements.txt

# Inicie o backend
cd backend
python main_unified.py

# Em outro terminal, inicie o frontend
cd regulacao-app
npm install
npm start
```

### 8.3 Endpoints Principais

- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Frontend**: http://localhost:8082

---

## 9. LICENÇA

Este projeto é distribuído sob a licença **MIT**, garantindo:

- ✅ Uso comercial permitido
- ✅ Modificação permitida
- ✅ Distribuição permitida
- ✅ Uso privado permitido
- ✅ Código fonte aberto para auditoria

---

## 10. CONTATO

**Proponente**: Lívia Moreira Rocha  
**Email**: liviamor01@hotmail.com  
**GitHub**: [@LiviaMor](https://github.com/LiviaMor)  
**Startup**: Nine Health  

---

*Documento gerado em: Dezembro 2025*  
*Versão: 1.0.0*
