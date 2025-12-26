import requests
import json
from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModel
import torch

# --- Scraper da SES-GO (implementado anteriormente) ---
class SESGoScraper:
    """
    Scraper para extrair dados de regulação diretamente da API CDA do painel Pentaho da SES-GO.
    """
    def __init__(self):
        self.cda_api_url = "https://indicadores.saude.go.gov.br/pentaho/plugin/cda/api/doQuery"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01'
        }
        self.cda_path = "/regulacao_transparencia/paineis/painel.cda"

    def _fetch_cda_data(self, data_access_id, params=None):
        query_params = {
            'path': self.cda_path,
            'dataAccessId': data_access_id,
            'outputIndexId': '1', 'pageSize': '0', 'pageStart': '0', 'sortBy': ''
        }
        if params:
            query_params.update(params)
        
        try:
            response = requests.get(self.cda_api_url, headers=self.headers, params=query_params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar dados da API CDA para '{data_access_id}': {e}")
            return None

    def fetch_leitos_disponiveis(self):
        """ Busca apenas os dados de leitos, que usaremos no prompt da IA. """
        # Para este exemplo, vamos focar nos pacientes 'em regulação' para simular a disponibilidade.
        # Numa implementação real, usaríamos um dataset de leitos vagos.
        dados_em_regulacao = self._fetch_cda_data("dsLFElistaEmRegulacao")
        if dados_em_regulacao and 'resultset' in dados_em_regulacao:
            # Simulação: agrupa por hospital e conta as solicitações, assumindo que isso
            # reflete a pressão sobre os leitos.
            leitos_por_hospital = {}
            for row in dados_em_regulacao['resultset']:
                hospital = row[9] # Nome da unidade solicitante
                leitos_por_hospital[hospital] = leitos_por_hospital.get(hospital, 0) + 1
            
            # Formata para o prompt
            lista_formatada = [f"- {hospital}: {count} solicitações pendentes" for hospital, count in leitos_por_hospital.items()]
            return "\n".join(lista_formatada)
        return "N/A"

# --- MS-Regulador (IA Core) ---

app = Flask(__name__)

# Inicialização do BioBERT (pode ser pesado, será carregado ao iniciar o server)
print("Carregando modelo BioBERT (pode levar alguns minutos)...")
try:
    tokenizer = AutoTokenizer.from_pretrained("dmis-lab/biobert-v1.1-pubmed")
    model = AutoModel.from_pretrained("dmis-lab/biobert-v1.1-pubmed")
    print("Modelo BioBERT carregado com sucesso.")
    biobert_disponivel = True
except Exception as e:
    print(f"AVISO: Não foi possível carregar o BioBERT. A extração de entidades será simulada. Erro: {e}")
    biobert_disponivel = False

def extrair_entidades_biobert(prontuario_texto):
    """
    Usa o BioBERT para extrair entidades médicas chave de um texto de prontuário.
    """
    if not biobert_disponivel or not prontuario_texto:
        return "Extração simulada: Paciente com dor abdominal aguda, febre. Suspeita de apendicite."

    inputs = tokenizer(prontuario_texto, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Lógica de extração simplificada: Apenas para demonstração, isso não extrai entidades nomeadas.
    # Uma implementação real usaria um modelo de NER (Named Entity Recognition) sobre o BioBERT.
    # Aqui, estamos apenas usando os embeddings da última camada para mostrar o uso.
    last_hidden_states = outputs.last_hidden_state
    # Simulação de extração a partir dos embeddings.
    return f"Texto processado pelo BioBERT. (Features extraídas com dimensão: {last_hidden_states.shape[-1]})"


def chamar_llama_docker(prompt_estruturado):
    """
    Envia o prompt estruturado para a API do Llama (Ollama) e retorna a decisão.
    """
    ollama_endpoint = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3", # Modelo default, pode ser alterado
        "prompt": prompt_estruturado,
        "format": "json", # Pede para o Llama retornar a resposta em JSON
        "stream": False
    }
    
    try:
        response = requests.post(ollama_endpoint, json=payload, timeout=120)
        response.raise_for_status()
        
        # A resposta do Ollama vem com o JSON dentro da chave "response"
        response_data = response.json()
        decisao_json = json.loads(response_data.get("response", "{}"))
        return decisao_json

    except requests.exceptions.ConnectionError:
        return {"erro": "Não foi possível conectar ao motor Llama no endereço 'http://localhost:11434'. Verifique se o Ollama está em execução."}
    except Exception as e:
        return {"erro": f"Ocorreu um erro ao chamar o motor Llama: {str(e)}"}

@app.route('/processar-regulacao', methods=['POST'])
def processar_ia():
    dados_paciente = request.json
    prontuario = dados_paciente.get('prontuario_texto')

    # Guardrail
    if not dados_paciente.get('cid'):
        return jsonify({"erro": "CID obrigatório para análise logística"}), 400

    # 1. Pipeline: Extração com BioBERT
    extracao_biobert = extrair_entidades_biobert(prontuario)
    
    # 2. Pipeline: Busca de dados de leitos
    scraper = SESGoScraper()
    lista_hospitais_vagos = scraper.fetch_leitos_disponiveis()

    # 3. Pipeline: Montagem do Prompt Estruturado
    prompt = f"""### ROLE
Você é o Especialista Sênior de Regulação Médica da SES-GO. Sua missão é realizar o pareamento (match) entre pacientes e leitos com base em risco clínico e logística.

### CONTEXTO DO PACIENTE (Dados Extraídos via BioBERT/API)
- Protocolo: {dados_paciente.get('solicitacao', 'N/A')} | Especialidade: {dados_paciente.get('especialidade', 'N/A')}
- CID-10: {dados_paciente.get('cid', 'N/A')} ({dados_paciente.get('cid_desc', 'N/A')})
- Quadro Clínico Resumido: {extracao_biobert}
- Histórico DATASUS: {dados_paciente.get('historico_paciente', 'N/A')}
- Prioridade Atual: {dados_paciente.get('prioridade_descricao', 'N/A')}

### DISPONIBILIDADE DE LEITOS (Dados SES-GO indicadores.saude.go.gov.br)
{lista_hospitais_vagos}

### PROTOCOLOS DE DECISÃO
1. Prioridade Absoluta: Risco de vida iminente > Tempo de fila.
2. Logística: Se dois hospitais têm a mesma especialidade, escolha o de menor tempo de deslocamento.
3. Transplante: Se óbito confirmado, acionar protocolo de manutenção de órgãos conforme diretriz_transplante_xyz.

### TAREFA
Analise os dados e retorne um JSON estrito com:
1. \"score_prioridade\": (0 a 10)
2. \"unidade_destino_sugerida\": (Nome da Unidade)
3. \"justificativa_clinica\": (Breve explicação baseada no protocolo)
4. \"proximos_passos\": (Ações para o MS-Logistica)

RESPOSTA EM JSON:
"""
    
    # 4. Pipeline: Chamada ao motor Llama
    decisao = chamar_llama_docker(prompt)
    
    return jsonify(decisao)


# --- Ponto de Entrada para Execução do Servidor ---

if __name__ == '__main__':
    print("Para testar o endpoint, envie uma requisição POST para http://127.0.0.1:5000/processar-regulacao")
    print("Exemplo de payload JSON:")
    print("""
    {
      "solicitacao": "PROTO-12345",
      "especialidade": "CARDIOLOGIA",
      "cid": "I21.9",
      "cid_desc": "Infarto agudo do miocárdio",
      "prontuario_texto": "Paciente de 65 anos, sexo masculino, apresenta dor torácica intensa há 2 horas...",
      "historico_paciente": "HAS, Diabetes Mellitus tipo 2.",
      "prioridade_descricao": "Emergência"
    }
    """)
    app.run(debug=True, port=5000)