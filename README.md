# Sistema de Regulação Autônoma SES-GO

Sistema inteligente de regulação médica para a Secretaria de Estado da Saúde de Goiás, utilizando IA para otimizar o processo de alocação de leitos e transferência de pacientes.

## 🏗️ Arquitetura

### Backend (Microserviços)
- **MS-Ingestion**: Scraper do Pentaho + API de dados públicos
- **MS-Intelligence**: BioBERT + Llama para análise de prontuários
- **MS-Logistics**: Autenticação JWT + Gerenciamento de estados

### Frontend
- **React Native + Expo**: App único para Web/Mobile
- **Dashboard Público**: Mapa de calor de leitos em tempo real
- **Área Hospitalar**: Upload de prontuários e solicitações

## 🚀 Início Rápido

### ✅ Pré-requisitos
- Python 3.8+
- Node.js 16+ (para React Native)
- PostgreSQL 15+ (será instalado automaticamente)

### 🎯 Instalação Completa (Recomendado)

```bash
# 1. Clone o repositório
git clone <seu-repositorio>
cd regulacao-microservicos

# 2. Instale dependências Python
pip install -r requirements.txt

# 3. Configure PostgreSQL (automático)
python install_postgresql.py    # Instala PostgreSQL
python setup_postgresql.py      # Configura banco de dados

# 4. Inicie o sistema completo
python start_complete_system.py

# 5. Em outro terminal, inicie o app React Native
cd regulacao-app
npm install
npm start
```

### ⚡ Início Rápido (Sem PostgreSQL)

```bash
# Executar apenas com dados JSON (sem banco)
python backend/main_simple_with_data.py

# Testar
python test_dashboard_api.py
```

## 📊 Endpoints da API

### MS-Ingestion (Porta 8001)
- `GET /dashboard/leitos` - Dashboard público
- `GET /pacientes` - Lista de pacientes
- `POST /sync` - Sincronização manual

### MS-Intelligence (Porta 8002)
- `POST /processar-regulacao` - Análise com IA
- `POST /upload-prontuario` - Upload de imagens
- `GET /historico/{protocolo}` - Histórico de decisões

### MS-Logistics (Porta 8003)
- `POST /login` - Autenticação
- `POST /transferencia` - Autorizar transferência
- `GET /fila-regulacao` - Fila de regulação
- `GET /dashboard-regulador` - Dashboard do regulador

## 🤖 Fluxo da IA

1. **Extração**: BioBERT processa texto do prontuário
2. **Contexto**: Sistema busca dados da rede hospitalar
3. **Decisão**: Llama3 analisa e sugere regulação
4. **Validação**: Regulador humano valida/ajusta
5. **Execução**: Sistema atualiza status e notifica

## 🔒 Autenticação

### Usuário Padrão
- **Email**: admin@sesgo.gov.br
- **Senha**: admin123

### Tipos de Usuário
- **ADMIN**: Acesso total
- **REGULADOR**: Gerenciar regulações
- **HOSPITAL**: Solicitar regulações

## 📱 Funcionalidades do App

### 🏠 Dashboard Público (Tab 1)
- **Dados reais da SES-GO** processados de 2.751 registros
- **Mapa de pressão hospitalar** com 766 pacientes em regulação
- **Top unidades críticas**: COMPLEXO REGULADOR MUNICIPAL DE GOIANIA (82 pacientes)
- **Especialidades em demanda**: ORTOPEDIA (205), CLÍNICA MÉDICA (145), CARDIOLOGIA (98)
- **Atualização automática** a cada 5 minutos
- **Modo offline** com dados de fallback
- **Indicadores visuais** de pressão (Verde/Amarelo/Vermelho)
- **Métricas temporais**: 82 solicitações nas últimas 24h

### 🏥 Área Hospitalar (Tab 2)
- **Upload de prontuários** via câmera ou galeria
- **Formulário estruturado** de solicitação
- **Análise automática com IA** (BioBERT + Llama3)
- **Resultado visual** com CardDecisaoIA
- **Login opcional** para autorizar transferências

### 👨‍⚕️ Área do Regulador (Tab 3)
- **Fila de regulação** em tempo real
- **Processamento com IA** para cada paciente
- **Autorização de transferências** com um clique
- **Dashboard de métricas** e estatísticas
- **Autenticação JWT** com roles de usuário

### 🤖 CardDecisaoIA - Componente Principal
```typescript
// Exibe decisões estruturadas da IA
<CardDecisaoIA 
  decisaoIA={resultado}
  protocolo="PROTO-12345"
  userToken={token}
  onTransferenciaAutorizada={callback}
/>
```

**Funcionalidades do Card:**
- 🚨 **Classificação de risco** visual (Vermelho/Amarelo/Verde)
- 📊 **Score de prioridade** (1-10)
- 🏥 **Unidade de destino** sugerida pela IA
- 📋 **Justificativa clínica** detalhada
- 🚑 **Logística de transporte** (USA/USB/Aéreo)
- ⏱️ **Previsão de vaga** estimada
- 🏥 **Protocolos especiais** (UTI/Transplante/Cirurgia)
- 🔐 **Autorização segura** com JWT

## 🛠️ Desenvolvimento

### Estrutura do Projeto
```
├── backend/
│   ├── shared/           # Modelos compartilhados
│   ├── ms-ingestion/     # Microserviço de ingestão
│   ├── ms-intelligence/  # Microserviço de IA
│   ├── ms-logistics/     # Microserviço de logística
│   └── docker-compose.yml
├── regulacao-app/        # App React Native
└── main.py              # Script original (legacy)
```

### Variáveis de Ambiente
```bash
# Database
DATABASE_URL=postgresql://regulacao_user:regulacao_pass@localhost:5432/regulacao_db

# JWT
JWT_SECRET_KEY=sua_chave_secreta_jwt_aqui

# Ollama
OLLAMA_URL=http://localhost:11434

# Redis
REDIS_URL=redis://localhost:6379
```

### Comandos Úteis
```bash
# Ver logs dos serviços
docker-compose logs -f

# Reiniciar um serviço específico
docker-compose restart ms-intelligence

# Executar migrações
docker-compose exec ms-ingestion python -c "from shared.database import create_tables; create_tables()"

# Backup do banco
docker-compose exec postgres pg_dump -U regulacao_user regulacao_db > backup.sql
```

## 🧪 Testes

### Backend
```bash
cd backend
pip install pytest httpx
pytest
```

### Frontend
```bash
cd regulacao-app
npm test
```

## 📈 Monitoramento

### Health Checks
- MS-Ingestion: http://localhost:8001/health
- MS-Intelligence: http://localhost:8002/health  
- MS-Logistics: http://localhost:8003/health
- Gateway: http://localhost/health

### Métricas
- Tempo de resposta da IA
- Taxa de acerto das predições
- Volume de regulações por hora
- Disponibilidade dos serviços

## 🔧 Configuração de Produção

### Nginx (Load Balancer)
```nginx
upstream backend {
    server ms-ingestion:8000;
    server ms-intelligence:8000;
    server ms-logistics:8000;
}
```

### PostgreSQL
- Configurar backup automático
- Otimizar índices para consultas frequentes
- Configurar replicação para alta disponibilidade

### Segurança
- HTTPS obrigatório
- Rate limiting
- Validação de entrada rigorosa
- Logs de auditoria

## 📚 Documentação Técnica

### Modelo de Dados
- **PacienteRegulacao**: Dados do paciente e regulação
- **HistoricoDecisoes**: Histórico de decisões da IA
- **Usuario**: Usuários do sistema

### Integração SES-GO
- API CDA do Pentaho
- Datasets: em_regulacao, admitidos, alta, em_transito
- Atualização a cada 10 minutos

### IA e Machine Learning
- **BioBERT**: Extração de entidades médicas
- **Llama3**: Análise e tomada de decisão
- **Prompt Engineering**: Templates estruturados
- **Validação Humana**: Loop de feedback

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

## 🆘 Suporte

Para suporte técnico:
- Abra uma issue no GitHub
- Email: suporte@sesgo.gov.br
- Documentação: [Wiki do Projeto]

---

**Desenvolvido com ❤️ para a SES-GO**