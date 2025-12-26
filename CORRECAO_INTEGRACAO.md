# 🔧 Correção da Integração Frontend-Backend

## Problemas Identificados e Corrigidos

### ❌ **Problema 1: Autenticação não funcionando**
**Causa**: Backend estava salvando senha sem hash, mas tentando verificar com hash
**Solução**: ✅ Corrigido - agora usa hash correto para senha

### ❌ **Problema 2: URLs incorretas no frontend**
**Causa**: Frontend tentava acessar `/api/...` mas backend roda na porta 8000 diretamente
**Solução**: ✅ Corrigido - URLs atualizadas para `http://localhost:8000`

### ❌ **Problema 3: Dados reais não carregando**
**Causa**: Banco PostgreSQL não configurado, dados JSON não carregados
**Solução**: ✅ Corrigido - usando SQLite + carregamento automático de dados

## 🚀 Como Testar a Correção

### 1. Iniciar o Backend
```bash
# Opção 1: Script simples (recomendado)
python start_backend_simple.py

# Opção 2: Diretamente
python backend/main_unified.py
```

### 2. Testar a Integração
```bash
# Executar testes automatizados
python test_frontend_backend.py
```

### 3. Iniciar o Frontend
```bash
cd regulacao-app
npm install  # se necessário
npm start
```

## 🧪 Testes Manuais

### Backend (http://localhost:8000)

1. **Health Check**: GET `/health`
   - ✅ Deve retornar `{"status": "healthy"}`

2. **Dashboard**: GET `/dashboard/leitos`
   - ✅ Deve retornar dados reais dos arquivos JSON

3. **Login**: POST `/login`
   ```json
   {
     "email": "admin@sesgo.gov.br",
     "senha": "admin123"
   }
   ```
   - ✅ Deve retornar token JWT

4. **Fila Regulação**: GET `/fila-regulacao` (com token)
   - ✅ Deve retornar lista de pacientes

### Frontend (Expo/React Native)

1. **Tab Dashboard**: 
   - ✅ Deve mostrar dados reais dos hospitais
   - ✅ Deve atualizar automaticamente

2. **Tab Área Hospital**:
   - ✅ Login rápido deve funcionar
   - ✅ Processamento IA deve retornar CardDecisaoIA

3. **Tab Regulação**:
   - ✅ Login deve funcionar com admin@sesgo.gov.br / admin123
   - ✅ Fila deve carregar pacientes reais

## 📊 Dados Esperados

Após carregar os dados JSON, você deve ver:

- **Status Summary**: EM_REGULACAO, INTERNADA, COM_ALTA, etc.
- **Unidades com Pressão**: Hospitais com pacientes em fila
- **Especialidades em Demanda**: CARDIOLOGIA, ORTOPEDIA, etc.

## 🔐 Credenciais de Teste

- **Email**: admin@sesgo.gov.br
- **Senha**: admin123
- **Tipo**: ADMIN (pode fazer tudo)

## 🐛 Troubleshooting

### Backend não inicia
```bash
# Verificar dependências
pip install -r requirements.txt

# Verificar porta
netstat -an | grep 8000
```

### Frontend não conecta
1. Verificar se backend está em http://localhost:8000
2. Verificar console do navegador/app para erros de CORS
3. Testar endpoints manualmente com curl/Postman

### Login não funciona
1. Verificar se usuário admin foi criado (logs do backend)
2. Testar login direto na API: POST /login
3. Verificar se senha está sendo hasheada corretamente

### Dados não aparecem
1. Executar: POST /load-json-data
2. Verificar se arquivos JSON existem na raiz do projeto
3. Verificar logs do backend para erros de carregamento

## 📝 Arquivos Modificados

- ✅ `backend/main_unified.py` - Correção de hash de senha
- ✅ `backend/shared/database.py` - SQLite por padrão
- ✅ `regulacao-app/components/*.tsx` - URLs corrigidas
- ✅ `regulacao-app/app/(tabs)/*.tsx` - URLs corrigidas

## 🎯 Resultado Esperado

Após as correções:

1. **Backend**: Roda em http://localhost:8000 com dados reais
2. **Frontend**: Conecta corretamente e mostra dados
3. **Login**: Funciona com admin@sesgo.gov.br / admin123
4. **Dashboard**: Mostra hospitais e estatísticas reais
5. **IA**: Processa regulações e retorna CardDecisaoIA
6. **Regulador**: Pode autorizar transferências

## 🚀 Próximos Passos

1. Executar `python start_backend_simple.py`
2. Executar `python test_frontend_backend.py`
3. Se tudo OK, iniciar frontend: `cd regulacao-app && npm start`
4. Testar login e funcionalidades no app