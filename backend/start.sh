#!/bin/bawssh

echo "🚀 Iniciando Sistema de Regulação Autônoma SES-GO"
echo "=================================================="

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Por favor, instale o Docker primeiro."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não encontrado. Por favor, instale o Docker Compose primeiro."
    exit 1
fi

# Criar diretórios necessários
mkdir -p models
mkdir -p logs

# Verificar se Ollama está rodando
echo "🔍 Verificando Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "⚠️  Ollama não está rodando. Iniciando..."
    echo "   Execute: ollama serve"
    echo "   Em seguida: ollama pull llama3"
fi

# Construir e iniciar os serviços
echo "🏗️  Construindo e iniciando microserviços..."
docker-compose up --build -d

# Aguardar serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 30

# Verificar status dos serviços
echo "📊 Status dos serviços:"
echo "MS-Ingestion: http://localhost:8001/health"
echo "MS-Intelligence: http://localhost:8002/health"
echo "MS-Logistics: http://localhost:8003/health"
echo "API Gateway: http://localhost/health"

# Testar conectividade
echo "🧪 Testando conectividade..."
curl -s http://localhost:8001/health && echo "✅ MS-Ingestion OK" || echo "❌ MS-Ingestion FALHOU"
curl -s http://localhost:8002/health && echo "✅ MS-Intelligence OK" || echo "❌ MS-Intelligence FALHOU"
curl -s http://localhost:8003/health && echo "✅ MS-Logistics OK" || echo "❌ MS-Logistics FALHOU"

echo ""
echo "🎉 Sistema iniciado com sucesso!"
echo ""
echo "📱 Para iniciar o app React Native:"
echo "   cd regulacao-app"
echo "   npm install"
echo "   npm start"
echo ""
echo "🔧 Credenciais padrão:"
echo "   Email: admin@sesgo.gov.br"
echo "   Senha: admin123"
echo ""
echo "📚 Documentação da API: http://localhost:8001/docs"