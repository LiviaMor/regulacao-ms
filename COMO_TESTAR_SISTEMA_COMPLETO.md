# 🧪 COMO TESTAR O SISTEMA COMPLETO

## 📋 PRÉ-REQUISITOS

### Software Necessário
- ✅ Python 3.8+
- ✅ PostgreSQL 12+
- ✅ Node.js 16+
- ✅ npm ou yarn

### Verificar Instalações
```bash
python --version
psql --version
node --version
npm --version
```

---

## 🚀 PASSO 1: INICIAR BACKEND

### 1.1 Navegar para pasta backend
```bash
cd backend
```

### 1.2 Verificar banco de dados
```bash
python verificar_colunas.py
```

**Saída Esperada**:
```
✅ Conectado ao PostgreSQL
📋 Colunas da tabela pacientes_regulacao:
  - id: integer
  - protocolo: character varying
  - status: character varying
  ... (33 colunas no total)
```

### 1.3 Iniciar servidor backend
```bash
python main_unified.py
```

**Saída Esperada**:
```
INFO:biobert_service:🧬 Carregando modelo BioBERT...
INFO:biobert_service:✅ BioBERT carregado
INFO:main_unified:BioBERT e Matchmaker carregados com sucesso
INFO:main_unified:✅ Módulo XAI (Explicabilidade) carregado
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 1.4 Testar backend (em outro terminal)
```bash
curl http://localhost:8000/health
```

**Saída Esperada**:
```json
{
  "status": "healthy",
  "database": "connected",
  "biobert": "loaded"
}
```

---

## 🎨 PASSO 2: INICIAR FRONTEND

### 2.1 Navegar para pasta frontend (novo terminal)
```bash
cd regulacao-app
```

### 2.2 Instalar dependências (primeira vez)
```bash
npm install
```

### 2.3 Iniciar servidor frontend
```bash
npm start
```

**Saída Esperada**:
```
Starting Metro Bundler
› Metro waiting on exp://192.168.x.x:8082
› Scan the QR code above with Expo Go (Android) or the Camera app (iOS)

› Web is waiting on http://localhost:8082
```

### 2.4 Abrir no navegador
```
http://localhost:8082
```

---

## 🧪 PASSO 3: TESTE MANUAL COMPLETO

### 3.1 ÁREA HOSPITALAR - Inserir Paciente

1. Abrir navegador: `http://localhost:8082`
2. Clicar na aba **"Hospital"**
3. Preencher formulário:

```
Nome Completo: João da Silva Santos
Nome da Mãe: Maria Santos Silva
CPF: 12345678901
Telefone: (62) 98765-4321
Data de Nascimento: 15/05/1980

Especialidade: CARDIOLOGIA
CID: I21.0
Descrição CID: Infarto Agudo do Miocárdio

Prontuário:
Paciente com dor torácica intensa há 2 horas, sudorese profusa, 
dispneia. ECG com supradesnivelamento de ST em parede anterior. 
Troponina elevada (5.2 ng/mL).

Histórico:
HAS há 10 anos, DM tipo 2, tabagista (20 cigarros/dia), 
dislipidemia. Pai faleceu de IAM aos 55 anos.

Prioridade: URGENTE
Cidade: GOIANIA
Hospital: HOSPITAL MUNICIPAL DE GOIANIA
```

4. Clicar em **"Solicitar Regulação"**

**Resultado Esperado**:
- ✅ Mensagem de sucesso
- ✅ Protocolo gerado (ex: REG-2025-001)
- ✅ Status: AGUARDANDO_REGULACAO

---

### 3.2 ÁREA DE REGULAÇÃO - Processar com IA

1. Clicar na aba **"Regulação"**
2. Fazer login:
   - Email: `admin@sesgo.gov.br`
   - Senha: `admin123`
3. Clicar em **"Entrar como Regulador"**

**Resultado Esperado**:
- ✅ Login bem-sucedido
- ✅ Lista de pacientes aguardando regulação
- ✅ Paciente REG-2025-001 aparece na lista

4. Localizar paciente REG-2025-001
5. Clicar em **"Processar com IA"**

**Aguardar processamento (5-10 segundos)**

**Resultado Esperado**:
```
✅ IA Processou com Sucesso!

Score de Prioridade: 8/10
Classificação de Risco: VERMELHO
Hospital Sugerido: HOSPITAL ESTADUAL DR ALBERTO RASSI HGG

Justificativa:
Paciente com IAM (I21.0) apresenta quadro crítico com 
supradesnivelamento de ST. Necessita UTI cardiológica 
especializada. BioBERT identificou sintomas críticos: 
dor torácica, sudorese, dispneia.

Matchmaker Logístico:
• Acionar Ambulância: SIM
• Tipo de Transporte: USA (Unidade de Suporte Avançado)
• Previsão de Vaga: 2-4 horas
```

6. Analisar decisão da IA
7. Clicar em **"✅ Aprovar"**

**Resultado Esperado**:
- ✅ Decisão registrada
- ✅ Status: INTERNACAO_AUTORIZADA
- ✅ Paciente SAI da fila de regulação
- ✅ Auditoria salva no banco

---

### 3.3 ÁREA DE TRANSFERÊNCIA - Solicitar Ambulância

1. Clicar na aba **"Transferência"**
2. Fazer login (se necessário):
   - Email: `admin@sesgo.gov.br`
   - Senha: `admin123`

**Resultado Esperado**:
- ✅ Lista de pacientes autorizados
- ✅ Paciente REG-2025-001 aparece

3. Localizar paciente REG-2025-001
4. Clicar em **"🚑 Solicitar Ambulância"**
5. Escolher tipo: **USA**

**Resultado Esperado**:
- ✅ Ambulância solicitada
- ✅ Status: EM_TRANSFERENCIA
- ✅ Status Ambulância: SOLICITADA
- ✅ Tipo: USA

6. Clicar em **"Atualizar Status"**
7. Escolher: **A_CAMINHO**

**Resultado Esperado**:
- ✅ Status atualizado
- ✅ Status Ambulância: A_CAMINHO

8. Repetir para: **NO_LOCAL** → **TRANSPORTANDO** → **CONCLUIDA**

**Resultado Final**:
- ✅ Status Paciente: INTERNADA
- ✅ Status Ambulância: CONCLUIDA
- ✅ Paciente SAI da área de transferência

---

### 3.4 CONSULTA PÚBLICA - Verificar Status

1. Clicar na aba **"Consulta"**
2. Digitar protocolo: `REG-2025-001`
3. Clicar em **"Consultar"**

**Resultado Esperado**:
```
✅ Paciente Encontrado!

Protocolo: REG-2025-001
Nome: J*** d* S*** S***
CPF: ***.***.*89-01
Telefone: (62) *****-**21

Status: INTERNADA
Status Ambulância: CONCLUIDA
Tipo de Transporte: USA

Especialidade: CARDIOLOGIA
Classificação de Risco: VERMELHO
Unidade Destino: HOSPITAL ESTADUAL DR ALBERTO RASSI HGG

Data Solicitação: 27/12/2024 10:30
Ambulância Solicitada: 27/12/2024 11:15
Internação: 27/12/2024 12:45
```

**Validações**:
- ✅ Dados pessoais ANONIMIZADOS
- ✅ Status em tempo real
- ✅ Histórico completo
- ✅ Transparência total

4. Testar busca por CPF: `12345678901`

**Resultado Esperado**:
- ✅ Mesmo paciente encontrado
- ✅ Dados anonimizados

---

## 🤖 PASSO 4: TESTE AUTOMATIZADO

### 4.1 Executar script de teste
```bash
python teste_fluxo_completo_validacao.py
```

**Saída Esperada**:
```
================================================================================
                    TESTE COMPLETO DE VALIDAÇÃO DO SISTEMA
================================================================================

Protocolo de Teste: REG-2025-TEST-1735308000
Data/Hora: 2024-12-27 14:30:00

================================================================================
                         ETAPA 1: AUTENTICAÇÃO
================================================================================

✅ Login realizado com sucesso
ℹ️  Usuário: Admin SES-GO (ADMIN)
ℹ️  Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

================================================================================
                  ETAPA 2: ÁREA HOSPITALAR - INSERIR PACIENTE
================================================================================

ℹ️  Protocolo: REG-2025-TEST-1735308000
ℹ️  Paciente: João da Silva Santos
ℹ️  CID: I21.0 - Infarto Agudo do Miocárdio
✅ Paciente inserido com sucesso!
ℹ️  Status inicial: AGUARDANDO_REGULACAO

================================================================================
                ETAPA 3: VERIFICAR PACIENTE NA FILA DE REGULAÇÃO
================================================================================

✅ Fila de regulação carregada: 1 pacientes
✅ Paciente REG-2025-TEST-1735308000 encontrado na fila!
ℹ️  Status: AGUARDANDO_REGULACAO

================================================================================
                  ETAPA 4: PROCESSAR COM IA (BioBERT + Llama)
================================================================================

ℹ️  Enviando para análise da IA...
ℹ️  BioBERT: Análise de entidades médicas
ℹ️  Llama 3: Geração de decisão clínica
✅ IA processou com sucesso!
ℹ️  Score Prioridade: 8/10
ℹ️  Classificação Risco: VERMELHO
ℹ️  Hospital Sugerido: HOSPITAL ESTADUAL DR ALBERTO RASSI
ℹ️  BioBERT Utilizado: True

================================================================================
                    ETAPA 5: DECISÃO DO REGULADOR - AUTORIZADA
================================================================================

ℹ️  Ação: AUTORIZADA
ℹ️  Hospital Destino: HOSPITAL ESTADUAL DR ALBERTO RASSI
✅ Decisão registrada com sucesso!
ℹ️  Auditoria: Histórico ID 1

================================================================================
              ETAPA 6: VERIFICAR PACIENTE NA ÁREA DE TRANSFERÊNCIA
================================================================================

✅ Área de transferência carregada: 1 pacientes
✅ Paciente REG-2025-TEST-1735308000 encontrado na transferência!
ℹ️  Status Paciente: INTERNACAO_AUTORIZADA
ℹ️  Status Ambulância: PENDENTE

================================================================================
                        ETAPA 7: SOLICITAR AMBULÂNCIA
================================================================================

ℹ️  Tipo de Transporte: USA (Unidade de Suporte Avançado)
✅ Ambulância solicitada com sucesso!
ℹ️  Status Ambulância: SOLICITADA

================================================================================
              ETAPA 8: CONSULTA PÚBLICA (DADOS ANONIMIZADOS)
================================================================================

ℹ️  Consultando por protocolo (sem autenticação)...
✅ Paciente encontrado na consulta pública!
ℹ️  Nome: J*** d* S*** S***
ℹ️  CPF: ***.***.*89-01
ℹ️  Status: EM_TRANSFERENCIA
ℹ️  Ambulância: SOLICITADA
✅ ✓ Dados anonimizados corretamente (LGPD)

================================================================================
                            RESUMO DOS TESTES
================================================================================

LOGIN: ✅ PASSOU
INSERIR: ✅ PASSOU
FILA: ✅ PASSOU
IA: ✅ PASSOU
APROVAR: ✅ PASSOU
TRANSFERENCIA: ✅ PASSOU
AMBULANCIA: ✅ PASSOU
CONSULTA: ✅ PASSOU

================================================================================
RESULTADO FINAL: 8/8 testes passaram
Taxa de Sucesso: 100.0%
================================================================================

✅ 🎉 TODOS OS TESTES PASSARAM! Sistema funcionando corretamente.
```

---

## 📊 PASSO 5: VERIFICAR BANCO DE DADOS

### 5.1 Conectar ao PostgreSQL
```bash
psql -U postgres -d regulacao_db
```

### 5.2 Verificar paciente inserido
```sql
SELECT protocolo, status, nome_completo, especialidade, classificacao_risco
FROM pacientes_regulacao
WHERE protocolo LIKE 'REG-2025%'
ORDER BY created_at DESC
LIMIT 5;
```

**Resultado Esperado**:
```
     protocolo      |       status        |    nome_completo     | especialidade | classificacao_risco
--------------------+---------------------+----------------------+---------------+--------------------
 REG-2025-TEST-001  | INTERNADA           | João da Silva Santos | CARDIOLOGIA   | VERMELHO
```

### 5.3 Verificar histórico de decisões
```sql
SELECT protocolo, usuario_validador, created_at
FROM historico_decisoes
WHERE protocolo LIKE 'REG-2025%'
ORDER BY created_at DESC
LIMIT 5;
```

**Resultado Esperado**:
```
     protocolo      | usuario_validador  |       created_at
--------------------+--------------------+-------------------------
 REG-2025-TEST-001  | admin@sesgo.gov.br | 2024-12-27 14:30:15
```

### 5.4 Sair do PostgreSQL
```sql
\q
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

### Backend
- [ ] Servidor iniciou sem erros
- [ ] BioBERT carregado
- [ ] Endpoint /health retorna 200
- [ ] Banco de dados conectado

### Frontend
- [ ] Servidor iniciou sem erros
- [ ] Página carrega no navegador
- [ ] Todas as abas visíveis
- [ ] Login funciona

### Fluxo Completo
- [ ] Paciente inserido com sucesso
- [ ] Aparece na fila de regulação
- [ ] IA processa corretamente
- [ ] Regulador pode aprovar
- [ ] Aparece na transferência
- [ ] Ambulância pode ser solicitada
- [ ] Status pode ser atualizado
- [ ] Consulta pública funciona
- [ ] Dados anonimizados corretamente

### Banco de Dados
- [ ] Paciente salvo em pacientes_regulacao
- [ ] Histórico salvo em historico_decisoes
- [ ] Todas as colunas preenchidas
- [ ] Timestamps corretos

---

## 🐛 TROUBLESHOOTING

### Erro: "Connection refused" no backend
**Solução**: Verificar se PostgreSQL está rodando
```bash
# Windows
net start postgresql-x64-12

# Linux/Mac
sudo service postgresql start
```

### Erro: "BioBERT não carregado"
**Solução**: Instalar dependências
```bash
pip install transformers torch
```

### Erro: "Port 8000 already in use"
**Solução**: Matar processo na porta 8000
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Erro: "Module not found" no frontend
**Solução**: Reinstalar dependências
```bash
cd regulacao-app
rm -rf node_modules
npm install
```

---

## 📞 SUPORTE

### Logs
- Backend: Console onde rodou `python main_unified.py`
- Frontend: Console onde rodou `npm start`
- Banco: `psql -U postgres -d regulacao_db`

### Arquivos de Log
- Backend: `backend/logs/` (se configurado)
- Frontend: Console do navegador (F12)

---

## 🎉 CONCLUSÃO

Se todos os testes passaram, o sistema está **100% funcional** e pronto para uso!

**Próximos Passos**:
1. Treinar equipe
2. Configurar ambiente de produção
3. Monitorar primeiros casos reais
4. Coletar feedback dos usuários

---

**Data**: 27/12/2024  
**Status**: ✅ SISTEMA VALIDADO E PRONTO PARA USO
