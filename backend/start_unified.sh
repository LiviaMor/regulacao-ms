#!/bin/bash

echo "🚀 Iniciando Sistema de Regulação SES-GO Unificado"

# Aguardar banco de dados
echo "⏳ Aguardando banco de dados..."
while ! pg_isready -h db -p 5432 -U regulacao_user; do
    echo "Aguardando PostgreSQL..."
    sleep 2
done

echo "✅ Banco de dados conectado"

# Criar tabelas se necessário
echo "🗄️ Inicializando banco de dados..."
python -c "
from shared.database import create_tables
create_tables()
print('Tabelas criadas/verificadas')
"

# Aguardar Ollama se disponível
echo "🤖 Verificando Ollama..."
if curl -s http://llm_engine:11434/api/tags > /dev/null; then
    echo "✅ Ollama disponível"
else
    echo "⚠️ Ollama não disponível - IA funcionará em modo simulado"
fi

# Iniciar aplicação unificada
echo "🌟 Iniciando API unificada..."
exec uvicorn main_unified:app --host 0.0.0.0 --port 8000 --reload