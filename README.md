# Sistema de Regulação Autônoma SES-GO
### Solução de Inteligência Artificial para Otimização da Regulação Médica

<div align="center">

![SES-GO](https://img.shields.io/badge/SES--GO-Sistema%20de%20Regulação-blue?style=for-the-badge)
![IA](https://img.shields.io/badge/IA-BioBERT%20%2B%20Llama3-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Apresentação%20ABERTO%20IA-orange?style=for-the-badge)

</div>

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

## **Arquitetura da Solução**

### **Inteligência Artificial**
- **BioBERT**: Modelo especializado em textos médicos para extração de entidades clínicas
- **Llama3**: LLM para análise contextual e geração de recomendações estruturadas
- **Prompt Engineering**: Templates otimizados para decisões de regulação médica
- **Validação Humana**: Interface intuitiva para aprovação/ajuste das decisões da IA

### **Backend - Microserviços**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MS-Ingestion  │    │ MS-Intelligence │    │  MS-Logistics   │
│                 │    │                 │    │                 │
│ • Scraper SES-GO│    │ • BioBERT       │    │ • Auth JWT      │
│ • API Pentaho   │    │ • Llama3        │    │ • Workflows     │
│ • Dashboard     │    │ • OCR Futuro    │    │ • Transferências│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Frontend - Multiplataforma**
- **React Native + Expo**: Código único para Web, iOS e Android
- **Dashboard Público**: Transparência total da situação hospitalar
- **Área Hospitalar**: Interface para solicitações e upload de prontuários
- **Área do Regulador**: Fila inteligente com sugestões da IA

---

## **Stack Tecnológica**

### **Backend**
- **Python 3.11+** - Linguagem principal
- **FastAPI** - Framework web moderno e performático
- **SQLAlchemy** - ORM para banco de dados
- **PostgreSQL/SQLite** - Banco de dados relacional
- **Redis** - Cache e filas assíncronas
- **Celery** - Processamento assíncrono
- **Docker** - Containerização e deploy

### **Inteligência Artificial**
- **Transformers (HuggingFace)** - BioBERT para NLP médico
- **Ollama** - Servidor local para Llama3
- **PyTorch** - Framework de deep learning
- **Pandas/NumPy** - Processamento de dados

### **Frontend**
- **React Native** - Framework mobile multiplataforma
- **Expo** - Plataforma de desenvolvimento
- **TypeScript** - Tipagem estática
- **React Navigation** - Navegação entre telas

### **DevOps & Infraestrutura**
- **Docker Compose** - Orquestração de containers
- **Nginx** - Load balancer e proxy reverso
- **GitHub Actions** - CI/CD (futuro)
- **Monitoring** - Health checks e métricas

---

## **Como Executar a Aplicação**

### **Pré-requisitos**
```bash
# Verificar versões
python --version  # >= 3.8
node --version    # >= 16
npm --version     # >= 8
```

### **Instalação Rápida (Desenvolvimento)**

#### **1. Clone o Repositório**
```bash
git clone git@github.com:LiviaMor/regulacao-ms.git
cd regulacao-ms
```

#### **2. Instalar Dependências Python**
```bash
pip install -r requirements.txt
```

#### **3. Iniciar Backend (Modo Simples)**
```bash
# Inicia com SQLite e dados de demonstração
python start_backend_simple.py
```

#### **4. Iniciar Frontend**
```bash
# Em outro terminal
cd regulacao-app
npm install
npm start
```

#### **5. Testar Integração**
```bash
# Verificar se tudo está funcionando
python test_frontend_backend.py
```

### **Instalação Completa (Produção)**

#### **1. Docker Compose (Recomendado)**
```bash
# Subir todos os serviços
cd backend
docker-compose up -d

# Verificar status
docker-compose ps
```

#### **2. Configuração Manual Completa**
```bash
# 1. Instalar PostgreSQL
python install_postgresql.py

# 2. Configurar banco de dados
python setup_postgresql.py

# 3. Iniciar sistema completo
python start_complete_system.py
```

---

## **Demonstração da Solução**

### **Credenciais de Demonstração**
```
Email: admin@sesgo.gov.br
Senha: admin123
Tipo: ADMIN (acesso completo)
```

### **Endpoints Principais**
- **API Principal**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Dashboard Público**: http://localhost:8000/dashboard/leitos
- **Health Check**: http://localhost:8000/health

### **Funcionalidades Demonstráveis**

#### **1. Dashboard Público**
- Visualização em tempo real de **766 pacientes em regulação**
- **20 unidades hospitalares** monitoradas
- **Mapa de calor** por especialidade médica
- Dados reais processados da SES-GO

#### **2. Análise com IA**
```json
{
  "analise_decisoria": {
    "score_prioridade": 8,
    "classificacao_risco": "VERMELHO",
    "unidade_destino_sugerida": "HOSPITAL ESTADUAL DR ALBERTO RASSI",
    "justificativa_clinica": "Paciente com quadro de IAM necessita UTI cardiológica"
  },
  "logistica": {
    "acionar_ambulancia": true,
    "tipo_transporte": "USA",
    "previsao_vaga_h": "2-4 horas"
  }
}
```

#### **3. Interface do Regulador**
- **CardDecisaoIA**: Componente visual para validação das decisões
- **Fila inteligente**: Ordenação automática por prioridade
- **Autorização com um clique**: Workflow otimizado

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

### **👩‍💻 Desenvolvedora**
**Livia Mor**
- GitHub: [@LiviaMor](https://github.com/LiviaMor)
- Email: liviamor01@hotmail.com
- LinkedIn: [Livia Mor](https://linkedin.com/in/liviamor)

### **🏛️ Instituição**
**Secretaria de Estado da Saúde de Goiás (SES-GO)**
- Site: https://www.saude.go.gov.br
- Email: suporte@sesgo.gov.br

### **📚 Documentação**
- **Repositório**: https://github.com/LiviaMor/regulacao-ms
- **Wiki**: [Em desenvolvimento]
- **API Docs**: http://localhost:8000/docs

---

<div align="center">

## 🌟 **Transformando a Saúde Pública com Inteligência Artificial**

*Desenvolvido com ❤️ para o ABERTO de IA de Goiás*

![Goiás](https://img.shields.io/badge/Goiás-Inovação%20em%20Saúde-green?style=for-the-badge)
![IA](https://img.shields.io/badge/IA-Futuro%20da%20Medicina-blue?style=for-the-badge)

</div>