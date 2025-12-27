# MS-Ingestao - Microserviço de Ingestão e Tendência

## Visão Geral

O MS-Ingestao atua como a **"Memória de Curto Prazo"** do ecossistema de regulação médica. Ele é responsável por:

1. **Ingerir dados de ocupação** hospitalar em tempo real
2. **Calcular tendências** de ocupação (ALTA, QUEDA, ESTÁVEL)
3. **Gerar alertas preditivos** de saturação
4. **Enriquecer dados** para o LLM (Llama) com contexto temporal

## Arquitetura

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Scraper/API   │────▶│   MS-Ingestao   │────▶│   MS-Regulacao  │
│  (Dados Brutos) │     │ (Memória Curta) │     │   (IA/Llama)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │  PostgreSQL     │
                        │ (historico_     │
                        │  ocupacao)      │
                        └─────────────────┘
```

## Endpoints

### Ingestão de Dados

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/ingerir-ocupacao` | Ingere um registro de ocupação |
| POST | `/ingerir-ocupacao-batch` | Ingere múltiplos registros |

### Consulta de Tendências

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/inteligencia/hospitais-disponiveis` | **Endpoint principal para IA** - Retorna hospitais com tendência |
| GET | `/tendencia/{unidade_id}` | Tendência detalhada de um hospital |
| GET | `/historico/{unidade_id}` | Histórico de ocupação |

### Administração

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Health check do serviço |
| GET | `/estatisticas` | Estatísticas do serviço |
| DELETE | `/limpar-historico-antigo` | Remove registros antigos |
| POST | `/simular-historico` | Simula dados para testes |

## Lógica de Tendência

### Cálculo

```python
variacao = ocupacao_atual - ocupacao_6h_atras

if variacao > 5:
    tendencia = "ALTA"
elif variacao < -5:
    tendencia = "QUEDA"
else:
    tendencia = "ESTAVEL"
```

### Alerta de Saturação

```python
alerta_saturacao = ocupacao > 90% AND tendencia == "ALTA"
```

### Previsão de Saturação

Se tendência é ALTA, calcula tempo estimado até 100%:

```python
taxa_por_hora = variacao / 6  # horas
horas_ate_saturacao = (100 - ocupacao_atual) / taxa_por_hora
previsao_minutos = horas_ate_saturacao * 60
```

## Exemplo de Resposta para IA

### Antes (sem tendência):
```
"O Hospital X tem 2 leitos vagos."
```

### Agora (com tendência):
```
"O Hospital X tem 2 leitos vagos, mas a tendência é de ocupação total 
nos próximos 40 minutos devido ao aumento de demanda na região. 
Considere o Hospital Y, que tem 3 leitos e tendência de queda."
```

## Modelo de Dados

```sql
CREATE TABLE historico_ocupacao (
    id SERIAL PRIMARY KEY,
    unidade_id VARCHAR NOT NULL,
    unidade_nome VARCHAR,
    tipo_leito VARCHAR,
    ocupacao_percentual FLOAT,
    leitos_totais INTEGER,
    leitos_ocupados INTEGER,
    leitos_disponiveis INTEGER,
    data_coleta TIMESTAMP DEFAULT NOW(),
    fonte_dados VARCHAR DEFAULT 'SCRAPER'
);

CREATE INDEX idx_unidade_data ON historico_ocupacao(unidade_id, data_coleta);
```

## Configuração

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `DATABASE_URL` | URL do PostgreSQL | `sqlite:///./regulacao.db` |
| `JWT_SECRET_KEY` | Chave JWT | - |

## Execução

### Local
```bash
cd backend/microservices/ms-ingestao
uvicorn main:app --host 0.0.0.0 --port 8004 --reload
```

### Docker
```bash
docker-compose -f docker-compose.microservices.yml up ms-ingestao
```

## Testes

```bash
python teste_ms_ingestao.py
```

## Integração com LLM

O endpoint `/api/v1/inteligencia/hospitais-disponiveis` retorna dados enriquecidos que podem ser injetados diretamente no prompt do Llama:

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
      "mensagem_ia": "HGG tem 7 leitos vagos, com tendência de ALTA na ocupação (Ocupação atual: 85.5%)"
    }
  ],
  "contexto_llm": {
    "hospitais_com_alerta": 2,
    "hospitais_tendencia_alta": 4,
    "recomendacao_ia": "⚠️ ATENÇÃO: 2 hospital(is) em alerta de saturação..."
  }
}
```

## Porta

**8004** (padrão)
