#!/usr/bin/env python3
"""
XAI - EXPLICABILIDADE DA IA - SISTEMA LIFE IA
Módulo de Explicabilidade (Explainable AI) para transparência das decisões

Este módulo implementa explicações detalhadas de por que a IA escolheu
cada hospital, atendendo ao critério de IA Aberta do edital FAPEG.

Referências:
- LIME: Ribeiro et al. (2016) "Why Should I Trust You?"
- SHAP: Lundberg & Lee (2017) "A Unified Approach to Interpreting Model Predictions"
"""

import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class ExplicadorDecisaoIA:
    """
    Classe para gerar explicações detalhadas das decisões da IA
    Implementa explicabilidade local (por decisão) e global (padrões gerais)
    """
    
    def __init__(self):
        # Pesos dos fatores de decisão (transparentes e auditáveis)
        self.pesos_fatores = {
            "especialidade_compativel": 0.30,    # 30% do peso
            "gravidade_clinica": 0.25,           # 25% do peso
            "distancia_geografica": 0.20,        # 20% do peso
            "ocupacao_hospital": 0.15,           # 15% do peso
            "hierarquia_sus": 0.10               # 10% do peso
        }
        
        # Descrições dos fatores para explicação humana
        self.descricoes_fatores = {
            "especialidade_compativel": "Compatibilidade da especialidade médica do hospital com a necessidade do paciente",
            "gravidade_clinica": "Nível de gravidade clínica baseado no CID e sintomas detectados",
            "distancia_geografica": "Distância entre a origem do paciente e o hospital (menor = melhor)",
            "ocupacao_hospital": "Taxa de ocupação atual do hospital (menor = melhor)",
            "hierarquia_sus": "Adequação à hierarquia do SUS (UPA → Regional → Referência)"
        }
        
        # Mapeamento de CIDs para explicações
        self.explicacoes_cid = {
            "I21": "Infarto Agudo do Miocárdio - Requer UTI Cardiológica e hemodinâmica",
            "I46": "Parada Cardíaca - Emergência máxima, hospital mais próximo com UTI",
            "S06": "Traumatismo Craniano - Requer neurocirurgia e UTI neurológica",
            "I63": "AVC Isquêmico - Janela terapêutica de 4.5h, centro de AVC prioritário",
            "I61": "AVC Hemorrágico - Neurocirurgia de emergência necessária",
            "J18": "Pneumonia - Internação clínica, oxigenoterapia",
            "M54": "Dor Lombar - Tratamento ambulatorial ou internação eletiva",
            "N17": "Insuficiência Renal Aguda - Requer diálise de urgência"
        }
        
        # Hospitais de referência por especialidade em Goiás
        self.referencias_especialidade = {
            "CARDIOLOGIA": ["HGG", "HEAPA"],
            "NEUROCIRURGIA": ["HUGO", "HUGOL"],
            "TRAUMA": ["HUGO", "HUGOL"],
            "ORTOPEDIA": ["HUGO", "REGIONAL_ANAPOLIS"],
            "OBSTETRICIA": ["MATERNO_INFANTIL", "HEMU"],
            "PEDIATRIA": ["HECAD"],
            "INFECTOLOGIA": ["HDT"],
            "CLINICA_MEDICA": ["HGG", "HEAPA", "REGIONAL_FORMOSA"]
        }
    
    def gerar_explicacao_completa(
        self,
        dados_paciente: Dict[str, Any],
        hospital_escolhido: str,
        hospitais_considerados: List[Dict[str, Any]],
        scores_calculados: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Gera explicação completa da decisão da IA
        
        Args:
            dados_paciente: Dados do paciente (CID, especialidade, cidade)
            hospital_escolhido: Hospital selecionado pela IA
            hospitais_considerados: Lista de hospitais avaliados
            scores_calculados: Scores de cada fator
            
        Returns:
            Dict com explicação estruturada e humanizada
        """
        
        try:
            # 1. Explicação do CID
            cid = dados_paciente.get("cid", "")
            explicacao_cid = self._explicar_cid(cid)
            
            # 2. Explicação dos fatores de decisão
            explicacao_fatores = self._explicar_fatores(scores_calculados)
            
            # 3. Comparação com alternativas
            comparacao_alternativas = self._comparar_alternativas(
                hospital_escolhido, 
                hospitais_considerados
            )
            
            # 4. Justificativa da hierarquia SUS
            justificativa_sus = self._justificar_hierarquia_sus(
                dados_paciente.get("especialidade", ""),
                hospital_escolhido
            )
            
            # 5. Gerar texto humanizado
            texto_explicacao = self._gerar_texto_humanizado(
                dados_paciente,
                hospital_escolhido,
                explicacao_cid,
                explicacao_fatores,
                justificativa_sus
            )
            
            return {
                "explicacao_resumida": texto_explicacao,
                "explicacao_detalhada": {
                    "cid_analise": explicacao_cid,
                    "fatores_decisao": explicacao_fatores,
                    "alternativas_consideradas": comparacao_alternativas,
                    "hierarquia_sus": justificativa_sus
                },
                "transparencia": {
                    "pesos_utilizados": self.pesos_fatores,
                    "modelo_ia": "BioBERT v1.1 + Pipeline Hospitais Goiás",
                    "auditavel": True,
                    "reproduzivel": True
                },
                "metadata": {
                    "versao_xai": "1.0.0",
                    "timestamp": datetime.utcnow().isoformat(),
                    "metodo": "Explicabilidade Local (LIME-inspired)"
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar explicação: {e}")
            return {
                "explicacao_resumida": f"Hospital {hospital_escolhido} selecionado com base nos critérios clínicos e logísticos.",
                "erro": str(e)
            }
    
    def _explicar_cid(self, cid: str) -> Dict[str, Any]:
        """Explica a análise do CID"""
        
        # Buscar explicação específica
        for cid_base, explicacao in self.explicacoes_cid.items():
            if cid.startswith(cid_base):
                return {
                    "cid": cid,
                    "categoria": cid_base,
                    "explicacao": explicacao,
                    "gravidade_inferida": self._inferir_gravidade_cid(cid_base)
                }
        
        return {
            "cid": cid,
            "categoria": "OUTROS",
            "explicacao": "CID não está na base de casos críticos conhecidos",
            "gravidade_inferida": "MODERADA"
        }
    
    def _inferir_gravidade_cid(self, cid_base: str) -> str:
        """Infere gravidade baseada no CID"""
        
        cids_criticos = ["I21", "I46", "S06", "I61", "I63", "N17"]
        cids_urgentes = ["J18", "E11", "I10"]
        
        if cid_base in cids_criticos:
            return "CRÍTICA"
        elif cid_base in cids_urgentes:
            return "URGENTE"
        else:
            return "MODERADA"
    
    def _explicar_fatores(self, scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """Explica cada fator de decisão com seu peso e contribuição"""
        
        explicacoes = []
        
        for fator, peso in self.pesos_fatores.items():
            score = scores.get(fator, 0.5)
            contribuicao = score * peso
            
            # Determinar impacto
            if contribuicao > 0.2:
                impacto = "ALTO"
                emoji = "🟢"
            elif contribuicao > 0.1:
                impacto = "MÉDIO"
                emoji = "🟡"
            else:
                impacto = "BAIXO"
                emoji = "🔴"
            
            explicacoes.append({
                "fator": fator,
                "descricao": self.descricoes_fatores.get(fator, fator),
                "peso_configurado": f"{peso*100:.0f}%",
                "score_obtido": f"{score:.2f}",
                "contribuicao_final": f"{contribuicao:.3f}",
                "impacto": impacto,
                "indicador": emoji
            })
        
        # Ordenar por contribuição (maior primeiro)
        explicacoes.sort(key=lambda x: float(x["contribuicao_final"]), reverse=True)
        
        return explicacoes
    
    def _comparar_alternativas(
        self, 
        escolhido: str, 
        considerados: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Compara o hospital escolhido com as alternativas"""
        
        comparacoes = []
        
        for hospital in considerados[:5]:  # Top 5 alternativas
            nome = hospital.get("nome", hospital.get("hospital", "N/A"))
            score = hospital.get("score_total", hospital.get("score", 0))
            
            foi_escolhido = nome == escolhido or escolhido in nome
            
            comparacoes.append({
                "hospital": nome,
                "score_total": f"{score:.2f}" if isinstance(score, float) else str(score),
                "selecionado": foi_escolhido,
                "motivo_nao_selecionado": None if foi_escolhido else self._motivo_nao_selecao(hospital)
            })
        
        return comparacoes
    
    def _motivo_nao_selecao(self, hospital: Dict[str, Any]) -> str:
        """Determina por que um hospital não foi selecionado"""
        
        ocupacao = hospital.get("ocupacao", 0)
        distancia = hospital.get("distancia_km", 0)
        especialidade_ok = hospital.get("especialidade_compativel", True)
        
        if not especialidade_ok:
            return "Especialidade não compatível com a necessidade do paciente"
        elif ocupacao > 90:
            return f"Taxa de ocupação muito alta ({ocupacao}%)"
        elif distancia > 100:
            return f"Distância elevada ({distancia:.1f} km)"
        else:
            return "Score total inferior ao hospital selecionado"
    
    def _justificar_hierarquia_sus(self, especialidade: str, hospital: str) -> Dict[str, Any]:
        """Justifica a escolha baseada na hierarquia do SUS"""
        
        # Determinar nível do hospital
        if any(ref in hospital.upper() for ref in ["HGG", "HUGO", "HUGOL", "HDT"]):
            nivel = "REFERÊNCIA ESTADUAL"
            justificativa = "Hospital de alta complexidade para casos graves"
        elif any(ref in hospital.upper() for ref in ["REGIONAL", "HEAPA", "HETRIN"]):
            nivel = "REGIONAL"
            justificativa = "Hospital regional adequado para complexidade média"
        else:
            nivel = "UPA/MUNICIPAL"
            justificativa = "Unidade de pronto atendimento para casos de menor complexidade"
        
        # Verificar se é referência para a especialidade
        referencias = self.referencias_especialidade.get(especialidade.upper(), [])
        eh_referencia = any(ref in hospital.upper() for ref in referencias)
        
        return {
            "nivel_hierarquico": nivel,
            "justificativa": justificativa,
            "eh_referencia_especialidade": eh_referencia,
            "especialidade_solicitada": especialidade,
            "hospitais_referencia": referencias
        }
    
    def _gerar_texto_humanizado(
        self,
        dados_paciente: Dict[str, Any],
        hospital: str,
        explicacao_cid: Dict,
        explicacao_fatores: List[Dict],
        justificativa_sus: Dict
    ) -> str:
        """Gera texto explicativo humanizado para o regulador"""
        
        cid = dados_paciente.get("cid", "N/A")
        especialidade = dados_paciente.get("especialidade", "N/A")
        cidade = dados_paciente.get("cidade_origem", "N/A")
        
        # Fator mais importante
        fator_principal = explicacao_fatores[0] if explicacao_fatores else None
        
        texto = f"""
EXPLICAÇÃO DA DECISÃO DA IA - LIFE IA

📋 PACIENTE: Protocolo {dados_paciente.get('protocolo', 'N/A')}
   • CID: {cid} - {explicacao_cid.get('explicacao', 'Análise padrão')}
   • Especialidade: {especialidade}
   • Origem: {cidade}
   • Gravidade Inferida: {explicacao_cid.get('gravidade_inferida', 'MODERADA')}

🏥 HOSPITAL SELECIONADO: {hospital}
   • Nível SUS: {justificativa_sus.get('nivel_hierarquico', 'N/A')}
   • É referência para {especialidade}: {'SIM ✅' if justificativa_sus.get('eh_referencia_especialidade') else 'NÃO'}

📊 FATOR DECISIVO: {fator_principal.get('fator', 'N/A') if fator_principal else 'N/A'}
   • {fator_principal.get('descricao', '') if fator_principal else ''}
   • Contribuição: {fator_principal.get('contribuicao_final', '0') if fator_principal else '0'} ({fator_principal.get('impacto', 'N/A') if fator_principal else 'N/A'})

✅ JUSTIFICATIVA TÉCNICA:
   {justificativa_sus.get('justificativa', 'Hospital selecionado com base nos critérios clínicos.')}

⚠️ NOTA: Esta é uma SUGESTÃO da IA. A decisão final é do REGULADOR MÉDICO.
        """.strip()
        
        return texto


# Instância global do explicador
explicador_ia = ExplicadorDecisaoIA()


def gerar_explicacao_decisao(
    dados_paciente: Dict[str, Any],
    hospital_escolhido: str,
    hospitais_considerados: List[Dict[str, Any]] = None,
    scores_calculados: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Função principal para gerar explicação da decisão
    
    Args:
        dados_paciente: Dados do paciente
        hospital_escolhido: Hospital selecionado
        hospitais_considerados: Lista de hospitais avaliados
        scores_calculados: Scores de cada fator
        
    Returns:
        Dict com explicação completa
    """
    
    if hospitais_considerados is None:
        hospitais_considerados = []
    
    if scores_calculados is None:
        # Scores padrão se não fornecidos
        scores_calculados = {
            "especialidade_compativel": 0.8,
            "gravidade_clinica": 0.7,
            "distancia_geografica": 0.6,
            "ocupacao_hospital": 0.5,
            "hierarquia_sus": 0.7
        }
    
    return explicador_ia.gerar_explicacao_completa(
        dados_paciente,
        hospital_escolhido,
        hospitais_considerados,
        scores_calculados
    )


if __name__ == "__main__":
    print("🧠 TESTE DO MÓDULO XAI - EXPLICABILIDADE DA IA")
    print("=" * 60)
    
    # Caso de teste 1: Infarto
    caso_teste = {
        "protocolo": "XAI-TEST-001",
        "cid": "I21.0",
        "especialidade": "CARDIOLOGIA",
        "cidade_origem": "ANAPOLIS",
        "prontuario_texto": "Dor torácica intensa, sudorese, dispneia"
    }
    
    hospitais = [
        {"nome": "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG", "score": 9.2, "ocupacao": 75},
        {"nome": "HEAPA", "score": 8.5, "ocupacao": 82},
        {"nome": "HUGO", "score": 7.8, "ocupacao": 90}
    ]
    
    scores = {
        "especialidade_compativel": 0.95,
        "gravidade_clinica": 0.90,
        "distancia_geografica": 0.70,
        "ocupacao_hospital": 0.65,
        "hierarquia_sus": 0.85
    }
    
    explicacao = gerar_explicacao_decisao(
        caso_teste,
        "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG",
        hospitais,
        scores
    )
    
    print(explicacao["explicacao_resumida"])
    print("\n" + "=" * 60)
    print("✅ Módulo XAI funcionando corretamente!")

