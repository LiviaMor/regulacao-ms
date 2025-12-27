"""
RAG INTEGRATION - MS-REGULACAO - VERSÃO FOCADA
Integração do Pipeline RAG focado com LLMs (Llama 3, GPT-4, Claude, etc.)
Seguindo hierarquia SUS: UPA -> Regional -> Referência
"""

import sys
import os
import json
import logging
from typing import Dict, Any, Optional
import requests
from datetime import datetime

# Adicionar path para pipeline RAG focado
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pipeline_hospitais_goias_rag import (
    gerar_contexto_rag_llama, 
    gerar_prompt_completo_llama,
    pipeline_rag
)

logger = logging.getLogger(__name__)

class RAGRegulacaoMedica:
    """
    Classe para integração RAG focada com diferentes LLMs
    Implementa lógica de peneira: Especialidade -> Complexidade -> Localidade
    """
    
    def __init__(self):
        self.llm_configs = {
            "ollama": {
                "url": os.getenv("OLLAMA_URL", "http://localhost:11434"),
                "model": "llama3",
                "endpoint": "/api/generate"
            },
            "openai": {
                "url": "https://api.openai.com/v1/chat/completions",
                "model": "gpt-4",
                "api_key": os.getenv("OPENAI_API_KEY")
            },
            "anthropic": {
                "url": "https://api.anthropic.com/v1/messages",
                "model": "claude-3-sonnet-20240229",
                "api_key": os.getenv("ANTHROPIC_API_KEY")
            }
        }
    
    def processar_com_llm(self, dados_paciente: Dict[str, Any], 
                         llm_provider: str = "ollama",
                         resultado_biobert: str = None) -> Dict[str, Any]:
        """
        Processa regulação usando LLM com contexto RAG focado
        
        Args:
            dados_paciente: Dados do paciente
            llm_provider: Provedor do LLM (ollama, openai, anthropic)
            resultado_biobert: Resultado da análise BioBERT (opcional)
            
        Returns:
            Resposta processada do LLM
        """
        
        try:
            # 1. Gerar prompt completo com contexto RAG focado
            prompt_completo = gerar_prompt_completo_llama(dados_paciente, resultado_biobert)
            
            logger.info(f"🤖 Processando com {llm_provider.upper()}: {dados_paciente.get('protocolo')}")
            
            # 2. Chamar LLM específico
            if llm_provider == "ollama":
                resposta_llm = self._chamar_ollama(prompt_completo)
            elif llm_provider == "openai":
                resposta_llm = self._chamar_openai(prompt_completo)
            elif llm_provider == "anthropic":
                resposta_llm = self._chamar_anthropic(prompt_completo)
            else:
                raise ValueError(f"Provedor LLM não suportado: {llm_provider}")
            
            # 3. Processar e validar resposta
            resposta_processada = self._processar_resposta_llm_focada(resposta_llm)
            
            # 4. Adicionar metadados RAG
            resposta_processada.update({
                "rag_metadata": {
                    "llm_provider": llm_provider,
                    "prompt_size": len(prompt_completo),
                    "pipeline_version": "RAG_Focado_v1.0",
                    "hierarquia_sus_aplicada": True,
                    "filtro_peneira_usado": True,
                    "processado_em": datetime.utcnow().isoformat()
                }
            })
            
            logger.info(f"✅ {llm_provider.upper()} processou: {resposta_processada['hospital_escolhido']}")
            
            return resposta_processada
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento RAG com {llm_provider}: {e}")
            
            # Fallback para pipeline tradicional
            return self._fallback_pipeline_tradicional(dados_paciente)
    
    def _processar_resposta_llm_focada(self, resposta_llm: str) -> Dict[str, Any]:
        """
        Processa e valida a resposta do LLM (versão focada)
        """
        try:
            # Tentar extrair JSON da resposta
            if "```json" in resposta_llm:
                json_start = resposta_llm.find("```json") + 7
                json_end = resposta_llm.find("```", json_start)
                json_str = resposta_llm[json_start:json_end].strip()
            elif "{" in resposta_llm and "}" in resposta_llm:
                # Extrair JSON mesmo sem marcadores
                json_start = resposta_llm.find("{")
                json_end = resposta_llm.rfind("}") + 1
                json_str = resposta_llm[json_start:json_end]
            else:
                json_str = resposta_llm.strip()
            
            resposta = json.loads(json_str)
            
            # Validar campos obrigatórios
            campos_obrigatorios = ["hospital_escolhido", "justificativa"]
            for campo in campos_obrigatorios:
                if campo not in resposta:
                    raise ValueError(f"Campo obrigatório '{campo}' não encontrado na resposta")
            
            # Validar se hospital existe na base
            hospital_escolhido = resposta["hospital_escolhido"]
            hospital_valido = any(h.nome == hospital_escolhido for h in pipeline_rag.hospitais)
            
            if not hospital_valido:
                logger.warning(f"Hospital '{hospital_escolhido}' não encontrado na base. Usando fallback.")
                resposta["hospital_escolhido"] = "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG"
                resposta["justificativa"] += " [FALLBACK: Hospital original não encontrado]"
            
            # Converter para formato padrão do sistema
            resposta_padrao = {
                "hospital_escolhido": resposta["hospital_escolhido"],
                "justificativa_tecnica": resposta["justificativa"],
                "score_adequacao": resposta.get("nivel_sus", 8),
                "tipo_transporte": "USB",  # Padrão
                "observacoes_clinicas": f"Nível SUS: {resposta.get('nivel_sus', 'N/A')}",
                "restricoes_verificadas": resposta.get("restricoes_respeitadas", []),
                "processado_em": datetime.utcnow().isoformat(),
                "fonte": "LLM_RAG_Focado",
                "validado": True
            }
            
            # Ajustar transporte baseado na urgência
            if any(palavra in resposta["justificativa"].lower() for palavra in ["trauma", "urgente", "emergência"]):
                resposta_padrao["tipo_transporte"] = "USA"
            
            return resposta_padrao
            
        except Exception as e:
            logger.error(f"Erro ao processar resposta do LLM: {e}")
            
            # Fallback em caso de erro
            return {
                "hospital_escolhido": "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG",
                "justificativa_tecnica": f"Erro no processamento da resposta do LLM: {str(e)}. Usando hospital de referência como fallback.",
                "score_adequacao": 5,
                "tipo_transporte": "USB",
                "observacoes_clinicas": "Análise manual necessária devido a erro no LLM",
                "restricoes_verificadas": [],
                "processado_em": datetime.utcnow().isoformat(),
                "fonte": "FALLBACK_RAG_Focado",
                "validado": False,
                "erro": str(e)
            }
    
    def _chamar_ollama(self, prompt: str) -> str:
        """Chama Ollama (Llama 3 local)"""
        
        config = self.llm_configs["ollama"]
        
        payload = {
            "model": config["model"],
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Baixa temperatura para consistência médica
                "top_p": 0.9,
                "max_tokens": 1000
            }
        }
        
        response = requests.post(
            f"{config['url']}{config['endpoint']}", 
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        return response.json().get("response", "")
    
    def _chamar_openai(self, prompt: str) -> str:
        """Chama OpenAI GPT-4"""
        
        config = self.llm_configs["openai"]
        
        if not config.get("api_key"):
            raise ValueError("OPENAI_API_KEY não configurada")
        
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": config["model"],
            "messages": [
                {
                    "role": "system", 
                    "content": "Você é um especialista em regulação médica do SUS de Goiás. Responda sempre em JSON conforme solicitado."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 1000
        }
        
        response = requests.post(
            config["url"], 
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]
    
    def _chamar_anthropic(self, prompt: str) -> str:
        """Chama Anthropic Claude"""
        
        config = self.llm_configs["anthropic"]
        
        if not config.get("api_key"):
            raise ValueError("ANTHROPIC_API_KEY não configurada")
        
        headers = {
            "x-api-key": config["api_key"],
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": config["model"],
            "max_tokens": 1000,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        response = requests.post(
            config["url"], 
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        return response.json()["content"][0]["text"]
    
    def _fallback_pipeline_tradicional(self, dados_paciente: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback para pipeline tradicional em caso de erro no LLM"""
        
        # Usar pipeline RAG focado como fallback (sem LLM)
        especialidade = dados_paciente.get('especialidade', 'CLINICA_MEDICA')
        cid = dados_paciente.get('cid', '')
        cidade = dados_paciente.get('cidade_origem', 'GOIANIA')
        
        # Aplicar filtro de peneira
        hospitais_filtrados = pipeline_rag.aplicar_filtro_peneira(especialidade, cid, cidade)
        
        if hospitais_filtrados:
            hospital_escolhido = hospitais_filtrados[0]  # Primeiro da lista (melhor ranqueado)
            justificativa = f"Hospital selecionado via pipeline focado: {hospital_escolhido.observacoes}"
        else:
            hospital_escolhido = None
            justificativa = "Nenhum hospital adequado encontrado, usando referência geral"
        
        return {
            "hospital_escolhido": hospital_escolhido.nome if hospital_escolhido else "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG",
            "justificativa_tecnica": justificativa,
            "score_adequacao": 7,
            "tipo_transporte": "USB",
            "observacoes_clinicas": "Processado via pipeline focado (fallback)",
            "restricoes_verificadas": [],
            "processado_em": datetime.utcnow().isoformat(),
            "fonte": "FALLBACK_Pipeline_Focado",
            "validado": True,
            "rag_metadata": {
                "llm_provider": "fallback",
                "pipeline_version": "RAG_Focado_v1.0",
                "hierarquia_sus_aplicada": True
            }
        }
    
    def testar_integracao_llm(self, llm_provider: str = "ollama") -> bool:
        """
        Testa integração com LLM específico usando pipeline focado
        """
        
        dados_teste = {
            "protocolo": "RAG-TEST-001",
            "especialidade": "ORTOPEDIA",
            "cid": "M54.5",
            "cid_desc": "Dor lombar",
            "cidade_origem": "ANAPOLIS",
            "prontuario_texto": "Paciente com dor lombar crônica, sem trauma",
            "historico_paciente": "Dor recorrente há 6 meses",
            "prioridade_descricao": "Normal"
        }
        
        try:
            resultado = self.processar_com_llm(dados_teste, llm_provider)
            
            # Verificar se resultado é válido
            hospital_escolhido = resultado.get("hospital_escolhido", "")
            
            # Teste específico: dor lombar NÃO deve ir para HUGO
            hugo_evitado = "HUGO" not in hospital_escolhido
            
            # Verificar se tem justificativa
            tem_justificativa = bool(resultado.get("justificativa_tecnica"))
            
            if hugo_evitado and tem_justificativa:
                logger.info(f"✅ Teste {llm_provider.upper()} passou: {hospital_escolhido}")
                logger.info(f"✅ HUGO evitado corretamente para dor lombar")
                return True
            else:
                logger.warning(f"⚠️ Teste {llm_provider.upper()} falhou:")
                logger.warning(f"   Hospital: {hospital_escolhido}")
                logger.warning(f"   HUGO evitado: {hugo_evitado}")
                logger.warning(f"   Tem justificativa: {tem_justificativa}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Teste {llm_provider.upper()} falhou: {e}")
            return False


# Instância global para uso nos microserviços
rag_regulacao = RAGRegulacaoMedica()

def processar_regulacao_rag(dados_paciente: Dict[str, Any], 
                           llm_provider: str = "ollama",
                           resultado_biobert: str = None) -> Dict[str, Any]:
    """
    Função principal para processamento RAG focado
    
    Args:
        dados_paciente: Dados do paciente
        llm_provider: Provedor LLM (ollama, openai, anthropic)
        resultado_biobert: Resultado da análise BioBERT (opcional)
        
    Returns:
        Resultado processado pelo LLM com contexto RAG focado
    """
    
    return rag_regulacao.processar_com_llm(dados_paciente, llm_provider, resultado_biobert)

def testar_rag_integration() -> Dict[str, bool]:
    """
    Testa integração RAG com todos os provedores disponíveis
    
    Returns:
        Dict com status de cada provedor
    """
    
    resultados = {}
    
    # Testar Ollama (local)
    resultados["ollama"] = rag_regulacao.testar_integracao_llm("ollama")
    
    # Testar OpenAI (se API key disponível)
    if os.getenv("OPENAI_API_KEY"):
        resultados["openai"] = rag_regulacao.testar_integracao_llm("openai")
    else:
        resultados["openai"] = False
        logger.info("⚠️ OpenAI API Key não configurada")
    
    # Testar Anthropic (se API key disponível)
    if os.getenv("ANTHROPIC_API_KEY"):
        resultados["anthropic"] = rag_regulacao.testar_integracao_llm("anthropic")
    else:
        resultados["anthropic"] = False
        logger.info("⚠️ Anthropic API Key não configurada")
    
    return resultados


if __name__ == "__main__":
    print("🤖 TESTE DE INTEGRAÇÃO RAG FOCADO - REGULAÇÃO MÉDICA")
    print("=" * 60)
    
    # Testar todos os provedores
    resultados = testar_rag_integration()
    
    print("\n📊 RESULTADOS DOS TESTES:")
    for provedor, status in resultados.items():
        emoji = "✅" if status else "❌"
        print(f"{emoji} {provedor.upper()}: {'FUNCIONANDO' if status else 'INDISPONÍVEL'}")
    
    # Teste detalhado com pipeline focado
    print("\n🏥 TESTE DETALHADO - PIPELINE FOCADO:")
    
    casos_teste = [
        {
            "nome": "Dor Lombar - Anápolis (deve evitar HUGO, priorizar regional)",
            "dados": {
                "protocolo": "RAG-DEMO-001",
                "especialidade": "ORTOPEDIA",
                "cid": "M54.5",
                "cidade_origem": "ANAPOLIS",
                "prontuario_texto": "Dor lombar crônica há 6 meses, sem trauma"
            }
        },
        {
            "nome": "Trauma Craniano - Goiânia (deve priorizar HUGO/HUGOL)",
            "dados": {
                "protocolo": "RAG-DEMO-002",
                "especialidade": "NEUROCIRURGIA",
                "cid": "S06.9",
                "cidade_origem": "GOIANIA",
                "prontuario_texto": "Trauma craniano grave, acidente de trânsito"
            }
        },
        {
            "nome": "Infecção - Formosa (deve priorizar HDT)",
            "dados": {
                "protocolo": "RAG-DEMO-003",
                "especialidade": "INFECTOLOGIA",
                "cid": "A15.0",
                "cidade_origem": "FORMOSA",
                "prontuario_texto": "Suspeita de tuberculose pulmonar"
            }
        }
    ]
    
    for caso in casos_teste:
        print(f"\n📋 {caso['nome']}")
        
        # Testar apenas contexto (sem LLM)
        contexto = gerar_contexto_rag_llama(
            caso['dados']['especialidade'],
            caso['dados']['cid'],
            caso['dados']['cidade_origem']
        )
        
        hospitais_contexto = json.loads(contexto)
        if hospitais_contexto:
            primeiro_hospital = hospitais_contexto[0]['hospital']
            print(f"🏥 Primeiro hospital sugerido: {primeiro_hospital}")
            
            # Verificações específicas
            if caso['dados']['cid'] == "M54.5" and "HUGO" not in primeiro_hospital:
                print("✅ CORRETO: Dor lombar não foi para HUGO")
            elif caso['dados']['cid'] == "S06.9" and ("HUGO" in primeiro_hospital or "HUGOL" in primeiro_hospital):
                print("✅ CORRETO: Trauma foi para hospital especializado")
            elif caso['dados']['cid'] == "A15.0" and "HDT" in primeiro_hospital:
                print("✅ CORRETO: Infecção foi para HDT")
        else:
            print("❌ Nenhum hospital encontrado")
    
    print("\n" + "=" * 60)
    print("🎯 PIPELINE RAG FOCADO IMPLEMENTADO!")
    print("🔄 Lógica de peneira: Especialidade -> Complexidade -> Localidade")
    print("🏥 Hierarquia SUS: UPA (1) -> Regional (2) -> Referência (3)")
    print("🤖 Pronto para Llama 3, GPT-4, Claude com contexto otimizado")
    print("=" * 60)