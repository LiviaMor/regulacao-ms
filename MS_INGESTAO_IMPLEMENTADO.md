# MS-Ingestao - Microserviço de Ingestão e Tendência

## ✅ Implementação Concluída

Data: 27/12/2024

## Resumo

Implementado o microserviço **MS-Ingestao** que atua como a "Memória de Curto Prazo" do sistema de regulação médica, permitindo:

1. **Ingestão de dados de ocupação** hospitalar em tempo real
2. **Cálculo de tendências** (ALTA, QUEDA, ESTÁVEL) baseado nas últimas 6 horas
3. **Alertas preditivos** de saturação quando ocupação > 90% + tendência ALTA
4. **Endpoint enriquecido para IA** com contexto temporal para o Llama

## Arquivos Criados/Modificados

### Novos Arquivos
- `backend/microservices/ms-ingestao/main.py` - Microserviço principal
- `backend/microservices/ms-ingestao/__init__.py` - Módulo Python
- `backend/microservices/ms-ingestao/README.md` - Documentação
- `teste_ms_ingestao.py` - Script de testes

### Arquivos Modificados
- `backend/microservices/shared/database.py` - Adicionado modelo `HistoricoOcupacao`
- `backend/microservices/docker-compose.microservices.yml` - Adicionado serviço ms-ingestao
- `backend/microservices/nginx.conf` - Adicionado roteamento para ms-ingestao
- `backend/microservices/README.md` - Documentação atualizada

## Endpoint Principal para IA

```
GET /api/v1/inteligencia/hospitais-disponiveis
```

### Resposta Enriquecida

```json
{
  "hospitais": [
    {
      "hospital": "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG",
      "sigla": "HGG",
      "taxa_ocupacao": 85.5,
      "leitos_disponiveis": 7,
      "tendencia": "ALTA",
      "variacao_6h": 8.2,
      "alerta_saturacao": false,
      "previsao_saturacao_min": 120,
      "mensagem_ia": "HGG tem 7 leitos vagos, com tendência de ALTA na ocupação..."
    }
  ],
  "contexto_llm": {
    "hospitais_com_alerta": 2,
    "hospitais_tendencia_alta": 4,
    "recomendacao_ia": "⚠️ ATENÇÃO: 2 hospital(is) em alerta de saturação..."
  }
}
```

## Mudança no Prompt do Llama

### Antes
```
"O Hospital X tem 2 leitos vagos."
```

### Agora
```
"O Hospital X tem 2 leitos vagos, mas a tendência é de ocupação total 
nos próximos 40 minutos devido ao aumento de demanda na região. 
Considere o Hospital Y, que tem 3 leitos e tendência de queda."
```

## Lógica de Tendência

```python
# Janela de análise: 6 horas
variacao = ocupacao_atual - ocupacao_6h_atras

if variacao > 5:
    tendencia = "ALTA"      # Subiu mais de 5%
elif variacao < -5:
    tendencia = "QUEDA"     # Caiu mais de 5%
else:
    tendencia = "ESTAVEL"   # Variação dentro de ±5%

# Alerta de saturação
alerta = ocupacao > 90% AND tendencia == "ALTA"
```

## Porta do Serviço

**8004**

## Como Executar

### Local
```bash
cd backend/microservices/ms-ingestao
uvicorn main:app --host 0.0.0.0 --port 8004 --reload
```

### Docker
```bash
cd backend/microservices
docker-compose -f docker-compose.microservices.yml up ms-ingestao
```

### Testar
```bash
python teste_ms_ingestao.py
```

## Endpoints Disponíveis

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Health check |
| POST | `/ingerir-ocupacao` | Ingere um registro |
| POST | `/ingerir-ocupacao-batch` | Ingere múltiplos registros |
| GET | `/api/v1/inteligencia/hospitais-disponiveis` | **Endpoint para IA** |
| GET | `/tendencia/{unidade_id}` | Tendência de um hospital |
| GET | `/historico/{unidade_id}` | Histórico de ocupação |
| GET | `/estatisticas` | Estatísticas do serviço |
| POST | `/simular-historico` | Simula dados para testes |
| DELETE | `/limpar-historico-antigo` | Manutenção |

## Integração com Sistema Existente

O MS-Ingestao foi projetado para:
- ✅ Não quebrar endpoints existentes
- ✅ Usar o mesmo banco de dados compartilhado
- ✅ Integrar com o pipeline de hospitais de Goiás
- ✅ Fornecer dados enriquecidos para o MS-Regulacao e Llama
