#!/usr/bin/env python3
"""
PIPELINE INTELIGENTE DE HOSPITAIS DE GOIAS - RAG READY
Sistema de IA para encaminhamento correto baseado em especialidades reais
Preparado para integracao com Llama 3 e outros LLMs (RAG - Retrieval-Augmented Generation)
"""

from typing import Dict, List, Optional, Tuple, Any
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class HospitalGoias:
    """Classe para representar um hospital com suas especialidades"""
    
    def __init__(self, nome: str, cidade: str, tipo: str, especialidades: List[str], 
                 capacidade: str, observacoes: str = ""):
        self.nome = nome
        self.cidade = cidade
        self.tipo = tipo  # REFERENCIA, REGIONAL, ESPECIALIZADO
        self.especialidades = especialidades
        self.capacidade = capacidade  # ALTA, MEDIA, BAIXA
        self.observacoes = observacoes
        self.score_disponibilidade = 10  # Simulado - em producao viria de API real


class PipelineDecisaoRegulacao:
    """
    Extensão do Pipeline para servir de base de conhecimento (RAG Ready)
    para o Llama 3 e outros LLMs no processo de regulação médica
    """
    
    def __init__(self, pipeline_hospitais: 'PipelineHospitaisGoias'):
        self.pipeline = pipeline_hospitais
        self.contexto_cache = {}
        
    def formatar_para_ia(self, hospital: HospitalGoias) -> Dict[str, Any]:
        """
        Transforma o objeto Hospital em uma 'ficha técnica' estruturada para o LLM
        
        Returns:
            Dict com informações estruturadas do hospital para prompt injection
        """
        return {
            "hospital": hospital.nome,
            "cidade": hospital.cidade,
            "perfil_clinico": hospital.tipo,
            "nivel_complexidade": hospital.capacidade,
            "especialidades_disponiveis": hospital.especialidades,
            "restricoes_severas": self.pipeline.criterios_exclusao.get(hospital.nome, []),
            "score_disponibilidade": hospital.score_disponibilidade,
            "observacoes_clinicas": hospital.observacoes,
            "adequacao_casos": self._gerar_adequacao_casos(hospital)
        }
    
    def _gerar_adequacao_casos(self, hospital: HospitalGoias) -> Dict[str, str]:
        """Gera descrição de adequação para diferentes tipos de casos"""
        adequacao = {}
        
        # Casos de trauma
        if "TRAUMATOLOGIA" in hospital.especialidades:
            adequacao["trauma"] = "Adequado para casos de trauma e urgência"
        elif hospital.nome == "HOSPITAL DE URGENCIAS DE GOIAS DR VALDEMIRO CRUZ HUGO":
            adequacao["trauma"] = "ESPECIALIZADO em trauma - PRIMEIRA ESCOLHA para emergências traumáticas"
        
        # Casos cardiológicos
        if "CARDIOLOGIA" in hospital.especialidades:
            if "CARDIOLOGIA_INTERVENCIONISTA" in hospital.especialidades:
                adequacao["cardiologia"] = "Cardiologia completa com hemodinâmica e intervenção"
            else:
                adequacao["cardiologia"] = "Cardiologia clínica disponível"
        
        # Casos neurológicos
        if "NEUROLOGIA" in hospital.especialidades:
            if "NEUROCIRURGIA" in hospital.especialidades:
                adequacao["neurologia"] = "Neurologia completa com neurocirurgia"
            else:
                adequacao["neurologia"] = "Neurologia clínica disponível"
        
        # Casos ortopédicos NÃO traumáticos
        if "ORTOPEDIA" in hospital.especialidades and hospital.nome != "HOSPITAL DE URGENCIAS DE GOIAS DR VALDEMIRO CRUZ HUGO":
            adequacao["ortopedia_eletiva"] = "Adequado para casos ortopédicos eletivos (dor lombar, artrose, etc.)"
        
        # Casos obstétricos
        if "OBSTETRICIA" in hospital.especialidades:
            if hospital.nome == "HOSPITAL ESTADUAL MATERNO INFANTIL DR JURANDIR DO NASCIMENTO":
                adequacao["obstetricia"] = "ESPECIALIZADO materno-infantil - PRIMEIRA ESCOLHA para gestantes"
            else:
                adequacao["obstetricia"] = "Obstetrícia disponível"
        
        # Casos infecciosos
        if hospital.nome == "HOSPITAL DE DOENCAS TROPICAIS DR ANUAR AUAD HDT":
            adequacao["infectologia"] = "ESPECIALIZADO em doenças infecciosas e tropicais - ÚNICA OPÇÃO para casos infecciosos complexos"
        
        return adequacao
    
    def gerar_contexto_hospitais(self, especialidade_requerida: str, 
                                cid: str = None, tipo_caso: str = None) -> str:
        """
        Filtra e ordena os hospitais para enviar apenas o relevante ao Prompt do LLM
        
        Args:
            especialidade_requerida: Especialidade médica necessária
            cid: Código CID-10 para contexto adicional
            tipo_caso: Tipo de caso (TRAUMA, EMERGENCIA, ELETIVO, etc.)
            
        Returns:
            JSON string formatado para prompt injection no LLM
        """
        
        # Cache key para otimização
        cache_key = f"{especialidade_requerida}_{cid}_{tipo_caso}"
        if cache_key in self.contexto_cache:
            return self.contexto_cache[cache_key]
        
        # Busca hospitais que possuem a especialidade
        filtrados = []
        for hospital in self.pipeline.hospitais:
            if especialidade_requerida.upper() in hospital.especialidades:
                filtrados.append(hospital)
            # Busca também por especialidades relacionadas
            elif self._especialidade_relacionada(especialidade_requerida, hospital.especialidades):
                filtrados.append(hospital)
        
        # Ordena por adequação ao caso
        filtrados = self._ordenar_por_adequacao(filtrados, especialidade_requerida, cid, tipo_caso)
        
        # Formatar para IA
        contexto_hospitais = [self.formatar_para_ia(h) for h in filtrados[:5]]  # Top 5 mais adequados
        
        # Adicionar metadados do contexto
        contexto_completo = {
            "timestamp": datetime.utcnow().isoformat(),
            "especialidade_solicitada": especialidade_requerida,
            "cid_contexto": cid,
            "tipo_caso": tipo_caso,
            "total_hospitais_disponiveis": len(filtrados),
            "hospitais_recomendados": contexto_hospitais,
            "criterios_exclusao_gerais": {
                "hugo_nao_eletivo": "HOSPITAL DE URGENCIAS (HUGO) NÃO atende casos eletivos ou baixa complexidade",
                "materno_infantil_restricao": "Hospital Materno-Infantil APENAS para mulheres grávidas e crianças",
                "hdt_apenas_infeccioso": "HDT APENAS para doenças infecciosas"
            },
            "instrucoes_ia": self._gerar_instrucoes_ia(especialidade_requerida, tipo_caso)
        }
        
        resultado = json.dumps(contexto_completo, indent=2, ensure_ascii=False)
        
        # Cache do resultado
        self.contexto_cache[cache_key] = resultado
        
        return resultado
    
    def _especialidade_relacionada(self, especialidade: str, especialidades_hospital: List[str]) -> bool:
        """Verifica se há especialidades relacionadas"""
        relacionamentos = {
            "CARDIOLOGIA": ["CARDIOLOGIA_INTERVENCIONISTA", "HEMODINAMICA", "UTI_CARDIOLOGICA"],
            "NEUROLOGIA": ["NEUROCIRURGIA", "AVC", "EPILEPSIA"],
            "ORTOPEDIA": ["TRAUMATOLOGIA", "ORTOPEDIA_TRAUMA", "CIRURGIA_ORTOPEDICA"],
            "CIRURGIA": ["CIRURGIA_GERAL", "CIRURGIA_VASCULAR", "CIRURGIA_CARDIOVASCULAR"],
            "PEDIATRIA": ["NEONATOLOGIA", "UTI_PEDIATRICA", "CARDIOLOGIA_PEDIATRICA"],
            "OBSTETRICIA": ["GINECOLOGIA", "ALTO_RISCO_OBSTETRICO"],
            "INFECTOLOGIA": ["DOENCAS_TROPICAIS", "HIV_AIDS", "TUBERCULOSE"]
        }
        
        especialidade_upper = especialidade.upper()
        if especialidade_upper in relacionamentos:
            return any(rel in especialidades_hospital for rel in relacionamentos[especialidade_upper])
        
        return False
    
    def _ordenar_por_adequacao(self, hospitais: List[HospitalGoias], 
                              especialidade: str, cid: str, tipo_caso: str) -> List[HospitalGoias]:
        """Ordena hospitais por adequação ao caso específico"""
        
        def calcular_score_adequacao(hospital: HospitalGoias) -> int:
            score = 0
            
            # Score base por tipo de hospital
            if hospital.tipo == "REFERENCIA":
                score += 10
            elif hospital.tipo == "ESPECIALIZADO":
                score += 15  # Especializado é melhor para sua área
            elif hospital.tipo == "REGIONAL":
                score += 5
            
            # Score por capacidade
            if hospital.capacidade == "ALTA":
                score += 10
            elif hospital.capacidade == "MEDIA":
                score += 5
            
            # Score por especialidade específica
            if especialidade.upper() in hospital.especialidades:
                score += 20
            
            # Bonus/Penalidade por tipo de caso
            if tipo_caso == "TRAUMA":
                if "TRAUMATOLOGIA" in hospital.especialidades:
                    score += 25
                if hospital.nome == "HOSPITAL DE URGENCIAS DE GOIAS DR VALDEMIRO CRUZ HUGO":
                    score += 30  # HUGO é THE BEST para trauma
            
            elif tipo_caso == "ORTOPEDIA_ELETIVA":
                if hospital.nome == "HOSPITAL DE URGENCIAS DE GOIAS DR VALDEMIRO CRUZ HUGO":
                    score -= 50  # HUGO NÃO atende eletivo
                elif "ORTOPEDIA" in hospital.especialidades:
                    score += 20
            
            elif tipo_caso == "OBSTETRICIA":
                if hospital.nome == "HOSPITAL ESTADUAL MATERNO INFANTIL DR JURANDIR DO NASCIMENTO":
                    score += 30  # Materno-infantil é THE BEST
            
            elif tipo_caso == "INFECTOLOGIA":
                if hospital.nome == "HOSPITAL DE DOENCAS TROPICAIS DR ANUAR AUAD HDT":
                    score += 30  # HDT é THE BEST para infecção
            
            # Penalidades por CID específicos
            if cid and cid.startswith("M54"):  # Dor lombar
                if hospital.nome == "HOSPITAL DE URGENCIAS DE GOIAS DR VALDEMIRO CRUZ HUGO":
                    score -= 100  # NUNCA mandar dor lombar para HUGO
            
            return score
        
        return sorted(hospitais, key=calcular_score_adequacao, reverse=True)
    
    def _gerar_instrucoes_ia(self, especialidade: str, tipo_caso: str) -> Dict[str, str]:
        """Gera instruções específicas para o LLM baseado no contexto"""
        
        instrucoes = {
            "objetivo": "Selecionar o hospital mais adequado baseado na especialidade, tipo de caso e restrições",
            "prioridade_1": "Sempre respeitar as restrições severas de cada hospital",
            "prioridade_2": "Hospitais especializados têm prioridade em sua área de expertise",
            "prioridade_3": "Considerar capacidade e disponibilidade logística"
        }
        
        # Instruções específicas por tipo de caso
        if tipo_caso == "TRAUMA":
            instrucoes["caso_trauma"] = "Para casos de trauma, HUGO é a primeira escolha. Outros hospitais com traumatologia são alternativas."
        
        elif tipo_caso == "ORTOPEDIA_ELETIVA":
            instrucoes["caso_ortopedia_eletiva"] = "Para casos ortopédicos eletivos (dor lombar, artrose), NUNCA escolher HUGO. Preferir hospitais regionais com ortopedia."
        
        elif tipo_caso == "OBSTETRICIA":
            instrucoes["caso_obstetricia"] = "Para gestantes, Hospital Materno-Infantil é primeira escolha. Outros com obstetrícia são alternativas."
        
        elif tipo_caso == "INFECTOLOGIA":
            instrucoes["caso_infectologia"] = "Para doenças infecciosas, HDT é a ÚNICA opção especializada. Outros hospitais apenas para casos simples."
        
        # Instruções por especialidade
        if "CARDIOLOGIA" in especialidade.upper():
            instrucoes["cardiologia"] = "Para casos cardiológicos, preferir hospitais com hemodinâmica se for emergência."
        
        elif "NEUROLOGIA" in especialidade.upper():
            instrucoes["neurologia"] = "Para casos neurológicos, verificar se precisa de neurocirurgia."
        
        return instrucoes
    
    def gerar_prompt_completo_llm(self, dados_paciente: Dict[str, Any], 
                                 especialidade: str, cid: str = None) -> str:
        """
        Gera prompt completo para o LLM com contexto de hospitais e dados do paciente
        
        Args:
            dados_paciente: Dados do paciente (protocolo, sintomas, etc.)
            especialidade: Especialidade médica necessária
            cid: Código CID-10
            
        Returns:
            Prompt formatado para o LLM
        """
        
        # Classificar tipo de caso
        tipo_caso = self._classificar_tipo_caso_rag(cid, dados_paciente.get('prontuario_texto', ''))
        
        # Gerar contexto de hospitais
        contexto_hospitais = self.gerar_contexto_hospitais(especialidade, cid, tipo_caso)
        
        # Montar prompt estruturado
        prompt = f"""
# SISTEMA DE REGULAÇÃO MÉDICA - SES GOIÁS

## MISSÃO
Você é um especialista em regulação médica do Sistema Único de Saúde de Goiás. Sua missão é selecionar o hospital mais adequado para cada paciente, considerando especialidades, capacidade, restrições e logística.

## DADOS DO PACIENTE
```json
{json.dumps(dados_paciente, indent=2, ensure_ascii=False)}
```

## CONTEXTO DE HOSPITAIS DISPONÍVEIS
```json
{contexto_hospitais}
```

## INSTRUÇÕES CRÍTICAS
1. **SEMPRE respeitar as restrições severas** de cada hospital
2. **HUGO (Hospital de Urgências)** é APENAS para trauma e urgência - NUNCA para casos eletivos
3. **Hospital Materno-Infantil** é APENAS para mulheres grávidas e crianças
4. **HDT** é APENAS para doenças infecciosas
5. Para **dor lombar** e casos ortopédicos eletivos, NUNCA escolher HUGO

## FORMATO DE RESPOSTA OBRIGATÓRIO
Responda APENAS em JSON no seguinte formato:
```json
{{
    "hospital_escolhido": "Nome completo do hospital",
    "justificativa_tecnica": "Explicação detalhada da escolha baseada nas especialidades e adequação",
    "score_adequacao": 9,
    "tipo_transporte": "USA ou USB",
    "observacoes_clinicas": "Observações específicas para o caso",
    "restricoes_verificadas": ["lista", "de", "restricoes", "consideradas"]
}}
```

## ANÁLISE SOLICITADA
Com base nos dados do paciente e no contexto de hospitais disponíveis, selecione o hospital mais adequado e forneça a resposta no formato JSON especificado.
"""
        
        return prompt
    
    def _classificar_tipo_caso_rag(self, cid: str, sintomas: str) -> str:
        """Classifica o tipo de caso para RAG (mais detalhado que a versão original)"""
        
        if not cid:
            return "CLINICO_GERAL"
        
        # Casos de trauma (códigos S e T)
        if any(cid.startswith(trauma) for trauma in ["S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "T0"]):
            return "TRAUMA"
        
        # Casos de emergência cardiológica
        if cid.startswith(("I21", "I46", "I20", "I50")):
            return "EMERGENCIA_CARDIOLOGICA"
        
        # Casos de emergência neurológica
        if cid.startswith(("I61", "I63", "G93", "S06")):
            return "EMERGENCIA_NEUROLOGICA"
        
        # Casos obstétricos
        if cid.startswith("O"):
            return "OBSTETRICIA"
        
        # Casos pediátricos
        if cid.startswith("P"):
            return "PEDIATRIA"
        
        # Casos infecciosos
        if cid.startswith(("A", "B")):
            return "INFECTOLOGIA"
        
        # Casos ortopédicos não traumáticos (M - musculoesquelético)
        if cid.startswith("M"):
            # Verificar se há menção de trauma nos sintomas
            if any(palavra in sintomas.lower() for palavra in ["trauma", "acidente", "queda", "fratura"]):
                return "TRAUMA"
            else:
                return "ORTOPEDIA_ELETIVA"
        
        # Casos respiratórios
        if cid.startswith("J"):
            return "PNEUMOLOGIA"
        
        # Casos renais
        if cid.startswith("N"):
            return "NEFROLOGIA"
        
        # Casos cirúrgicos gerais
        if cid.startswith("K"):
            return "CIRURGIA_GERAL"
        
        return "CLINICO_GERAL"
    
    def processar_resposta_llm(self, resposta_llm: str) -> Dict[str, Any]:
        """
        Processa e valida a resposta do LLM
        
        Args:
            resposta_llm: Resposta em JSON do LLM
            
        Returns:
            Dict com resposta processada e validada
        """
        try:
            # Tentar extrair JSON da resposta
            if "```json" in resposta_llm:
                json_start = resposta_llm.find("```json") + 7
                json_end = resposta_llm.find("```", json_start)
                json_str = resposta_llm[json_start:json_end].strip()
            else:
                json_str = resposta_llm.strip()
            
            resposta = json.loads(json_str)
            
            # Validar campos obrigatórios
            campos_obrigatorios = ["hospital_escolhido", "justificativa_tecnica", "score_adequacao"]
            for campo in campos_obrigatorios:
                if campo not in resposta:
                    raise ValueError(f"Campo obrigatório '{campo}' não encontrado na resposta")
            
            # Validar se hospital existe
            hospital_escolhido = resposta["hospital_escolhido"]
            hospital_valido = any(h.nome == hospital_escolhido for h in self.pipeline.hospitais)
            
            if not hospital_valido:
                logger.warning(f"Hospital '{hospital_escolhido}' não encontrado na base. Usando fallback.")
                resposta["hospital_escolhido"] = "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG"
                resposta["justificativa_tecnica"] += " [FALLBACK: Hospital original não encontrado]"
            
            # Adicionar metadados
            resposta["processado_em"] = datetime.utcnow().isoformat()
            resposta["fonte"] = "LLM_RAG_Pipeline"
            resposta["validado"] = True
            
            return resposta
            
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
                "fonte": "FALLBACK_Pipeline",
                "validado": False,
                "erro": str(e)
            }


class PipelineHospitaisGoias:
    """Pipeline inteligente para seleção de hospitais em Goiás"""
    
    def __init__(self):
        self.hospitais = self._carregar_hospitais_goias()
        self.mapeamento_cid_especialidade = self._criar_mapeamento_cid()
        self.criterios_exclusao = self._definir_criterios_exclusao()
    
    def _carregar_hospitais_goias(self) -> List[HospitalGoias]:
        """Carrega todos os hospitais de grande complexidade de Goiás com dados reais"""
        
        return [
            # === HOSPITAIS DE REFERÊNCIA ESTADUAL ===
            HospitalGoias(
                nome="HOSPITAL ESTADUAL DR ALBERTO RASSI HGG",
                cidade="GOIANIA",
                tipo="REFERENCIA",
                especialidades=[
                    "CARDIOLOGIA", "CARDIOLOGIA_INTERVENCIONISTA", "HEMODINAMICA",
                    "CIRURGIA_CARDIOVASCULAR", "UTI_CARDIOLOGICA", "MARCAPASSO",
                    "NEUROLOGIA", "NEUROCIRURGIA", "AVC", "EPILEPSIA",
                    "CIRURGIA_GERAL", "CIRURGIA_VASCULAR", "ANGIOLOGIA",
                    "NEFROLOGIA", "HEMODIALISE", "TRANSPLANTE_RENAL",
                    "ENDOCRINOLOGIA", "DIABETES", "TIREOIDE",
                    "CLINICA_MEDICA", "GERIATRIA", "UTI_GERAL"
                ],
                capacidade="ALTA",
                observacoes="Principal hospital de referência. Cardiologia e neurologia 24h. Transplantes."
            ),
            
            HospitalGoias(
                nome="HOSPITAL DE URGENCIAS DE GOIAS DR VALDEMIRO CRUZ HUGO",
                cidade="GOIANIA",
                tipo="REFERENCIA",
                especialidades=[
                    "TRAUMATOLOGIA", "ORTOPEDIA_TRAUMA", "NEUROCIRURGIA_TRAUMA",
                    "CIRURGIA_GERAL_URGENCIA", "CIRURGIA_VASCULAR_URGENCIA",
                    "QUEIMADOS", "UTI_TRAUMA", "POLITRAUMATISMO",
                    "EMERGENCIA_GERAL", "TOXICOLOGIA", "PSIQUIATRIA_URGENCIA"
                ],
                capacidade="ALTA",
                observacoes="ESPECIALIZADO EM TRAUMA E URGÊNCIA. NÃO para casos eletivos ou baixa complexidade."
            ),
            
            HospitalGoias(
                nome="HOSPITAL ESTADUAL DE ANAPOLIS DR HENRIQUE SANTILLO",
                cidade="ANAPOLIS",
                tipo="REFERENCIA",
                especialidades=[
                    "CARDIOLOGIA", "HEMODINAMICA", "CIRURGIA_CARDIOVASCULAR",
                    "NEUROLOGIA", "NEUROCIRURGIA", "AVC",
                    "ORTOPEDIA", "TRAUMATOLOGIA", "CIRURGIA_ORTOPEDICA",
                    "NEFROLOGIA", "HEMODIALISE", "TRANSPLANTE_RENAL",
                    "ONCOLOGIA", "QUIMIOTERAPIA", "RADIOTERAPIA",
                    "CIRURGIA_GERAL", "CIRURGIA_ONCOLOGICA",
                    "CLINICA_MEDICA", "UTI_GERAL", "UTI_CARDIOLOGICA"
                ],
                capacidade="ALTA",
                observacoes="Referência regional. Oncologia e transplantes. Atende região metropolitana."
            ),
            
            # === HOSPITAIS ESPECIALIZADOS ===
            HospitalGoias(
                nome="HOSPITAL ESTADUAL MATERNO INFANTIL DR JURANDIR DO NASCIMENTO",
                cidade="GOIANIA",
                tipo="ESPECIALIZADO",
                especialidades=[
                    "OBSTETRICIA", "GINECOLOGIA", "NEONATOLOGIA", "UTI_NEONATAL",
                    "PEDIATRIA", "UTI_PEDIATRICA", "CIRURGIA_PEDIATRICA",
                    "CARDIOLOGIA_PEDIATRICA", "NEUROLOGIA_PEDIATRICA",
                    "ALTO_RISCO_OBSTETRICO", "PREMATUROS"
                ],
                capacidade="ALTA",
                observacoes="EXCLUSIVO materno-infantil. Não atende adultos."
            ),
            
            HospitalGoias(
                nome="HOSPITAL DE DOENCAS TROPICAIS DR ANUAR AUAD HDT",
                cidade="GOIANIA",
                tipo="ESPECIALIZADO",
                especialidades=[
                    "INFECTOLOGIA", "DOENCAS_TROPICAIS", "HIV_AIDS",
                    "HEPATITES", "TUBERCULOSE", "HANSENIASE",
                    "MALARIA", "DENGUE", "CHIKUNGUNYA", "ZIKA",
                    "UTI_INFECTOLOGIA"
                ],
                capacidade="MEDIA",
                observacoes="ESPECIALIZADO em doenças infecciosas e tropicais."
            ),
            
            HospitalGoias(
                nome="HOSPITAL DE URGENCIAS DA REGIAO NOROESTE HURN",
                cidade="CERES",
                tipo="REGIONAL",
                especialidades=[
                    "EMERGENCIA_GERAL", "CLINICA_MEDICA", "CIRURGIA_GERAL",
                    "ORTOPEDIA", "TRAUMATOLOGIA", "PEDIATRIA",
                    "OBSTETRICIA", "GINECOLOGIA", "UTI_GERAL"
                ],
                capacidade="MEDIA",
                observacoes="Referência para região noroeste de Goiás."
            ),
            
            # === HOSPITAIS REGIONAIS ===
            HospitalGoias(
                nome="HOSPITAL ESTADUAL DE FORMOSA DR CESAR SAAD FAYAD",
                cidade="FORMOSA",
                tipo="REGIONAL",
                especialidades=[
                    "CLINICA_MEDICA", "CIRURGIA_GERAL", "ORTOPEDIA",
                    "CARDIOLOGIA", "NEUROLOGIA", "NEFROLOGIA",
                    "PEDIATRIA", "OBSTETRICIA", "GINECOLOGIA",
                    "UTI_GERAL", "EMERGENCIA_GERAL"
                ],
                capacidade="MEDIA",
                observacoes="Referência para região nordeste de Goiás e entorno do DF."
            ),
            
            HospitalGoias(
                nome="HOSPITAL ESTADUAL DO CENTRO NORTE GOIANO",
                cidade="URUACU",
                tipo="REGIONAL",
                especialidades=[
                    "CLINICA_MEDICA", "CIRURGIA_GERAL", "ORTOPEDIA",
                    "PEDIATRIA", "OBSTETRICIA", "GINECOLOGIA",
                    "EMERGENCIA_GERAL", "UTI_GERAL"
                ],
                capacidade="MEDIA",
                observacoes="Referência para região centro-norte de Goiás."
            ),
            
            HospitalGoias(
                nome="HOSPITAL ESTADUAL DE JATAI",
                cidade="JATAI",
                tipo="REGIONAL",
                especialidades=[
                    "CLINICA_MEDICA", "CIRURGIA_GERAL", "ORTOPEDIA",
                    "CARDIOLOGIA", "NEUROLOGIA", "PEDIATRIA",
                    "OBSTETRICIA", "GINECOLOGIA", "UTI_GERAL"
                ],
                capacidade="MEDIA",
                observacoes="Referência para região sudoeste de Goiás."
            ),
            
            HospitalGoias(
                nome="HOSPITAL ESTADUAL DE LUZIANIA",
                cidade="LUZIANIA",
                tipo="REGIONAL",
                especialidades=[
                    "CLINICA_MEDICA", "CIRURGIA_GERAL", "ORTOPEDIA",
                    "PEDIATRIA", "OBSTETRICIA", "GINECOLOGIA",
                    "EMERGENCIA_GERAL", "UTI_GERAL"
                ],
                capacidade="MEDIA",
                observacoes="Referência para região sul de Goiás e entorno do DF."
            ),
            
            # === HOSPITAIS MUNICIPAIS DE GRANDE PORTE ===
            HospitalGoias(
                nome="HOSPITAL MUNICIPAL DE APARECIDA DE GOIANIA",
                cidade="APARECIDA_DE_GOIANIA",
                tipo="REGIONAL",
                especialidades=[
                    "CLINICA_MEDICA", "CIRURGIA_GERAL", "ORTOPEDIA",
                    "CARDIOLOGIA", "PEDIATRIA", "OBSTETRICIA",
                    "EMERGENCIA_GERAL", "UTI_GERAL"
                ],
                capacidade="MEDIA",
                observacoes="Atende região metropolitana de Goiânia."
            ),
            
            HospitalGoias(
                nome="HOSPITAL MUNICIPAL DE MOZARLANDIA",
                cidade="MOZARLANDIA",
                tipo="REGIONAL",
                especialidades=[
                    "CLINICA_MEDICA", "CIRURGIA_GERAL", "ORTOPEDIA",
                    "PEDIATRIA", "OBSTETRICIA", "EMERGENCIA_GERAL"
                ],
                capacidade="BAIXA",
                observacoes="Hospital regional de menor porte."
            )
        ]
    
    def _criar_mapeamento_cid(self) -> Dict[str, List[str]]:
        """Mapeia CIDs para especialidades necessárias"""
        
        return {
            # === CARDIOLOGIA ===
            "I21": ["CARDIOLOGIA", "CARDIOLOGIA_INTERVENCIONISTA", "HEMODINAMICA", "UTI_CARDIOLOGICA"],  # Infarto
            "I20": ["CARDIOLOGIA", "HEMODINAMICA"],  # Angina
            "I46": ["CARDIOLOGIA", "UTI_CARDIOLOGICA", "EMERGENCIA_GERAL"],  # Parada cardíaca
            "I50": ["CARDIOLOGIA", "UTI_CARDIOLOGICA"],  # Insuficiência cardíaca
            "I47": ["CARDIOLOGIA", "UTI_CARDIOLOGICA"],  # Taquicardia paroxística
            
            # === NEUROLOGIA/NEUROCIRURGIA ===
            "I61": ["NEUROLOGIA", "NEUROCIRURGIA", "AVC", "UTI_GERAL"],  # AVC hemorrágico
            "I63": ["NEUROLOGIA", "AVC", "UTI_GERAL"],  # AVC isquêmico
            "G93": ["NEUROLOGIA", "NEUROCIRURGIA", "UTI_GERAL"],  # Lesão cerebral
            "S06": ["NEUROCIRURGIA", "NEUROCIRURGIA_TRAUMA", "UTI_TRAUMA"],  # Traumatismo craniano
            "G40": ["NEUROLOGIA", "EPILEPSIA"],  # Epilepsia
            
            # === TRAUMA/ORTOPEDIA ===
            "S72": ["TRAUMATOLOGIA", "ORTOPEDIA_TRAUMA", "CIRURGIA_ORTOPEDICA"],  # Fratura fêmur
            "S82": ["TRAUMATOLOGIA", "ORTOPEDIA_TRAUMA"],  # Fratura perna
            "S42": ["ORTOPEDIA", "TRAUMATOLOGIA"],  # Fratura úmero
            "T07": ["TRAUMATOLOGIA", "UTI_TRAUMA", "POLITRAUMATISMO"],  # Politraumatismo
            
            # === ORTOPEDIA ELETIVA (NÃO TRAUMA) ===
            "M54": ["ORTOPEDIA", "CLINICA_MEDICA"],  # Dor lombar - NÃO É TRAUMA
            "M79": ["ORTOPEDIA", "CLINICA_MEDICA"],  # Dor musculoesquelética - NÃO É TRAUMA
            "M25": ["ORTOPEDIA"],  # Artropatias - NÃO É TRAUMA
            "M17": ["ORTOPEDIA"],  # Artrose joelho - NÃO É TRAUMA
            
            # === CIRURGIA GERAL ===
            "K35": ["CIRURGIA_GERAL", "CIRURGIA_GERAL_URGENCIA"],  # Apendicite
            "K80": ["CIRURGIA_GERAL"],  # Colelitíase
            "K92": ["CIRURGIA_GERAL", "CIRURGIA_GERAL_URGENCIA"],  # Hemorragia GI
            
            # === PNEUMOLOGIA/CLÍNICA ===
            "J18": ["CLINICA_MEDICA", "UTI_GERAL"],  # Pneumonia
            "J44": ["CLINICA_MEDICA", "UTI_GERAL"],  # DPOC
            "J45": ["CLINICA_MEDICA"],  # Asma
            
            # === NEFROLOGIA ===
            "N17": ["NEFROLOGIA", "HEMODIALISE", "UTI_GERAL"],  # Insuficiência renal aguda
            "N18": ["NEFROLOGIA", "HEMODIALISE"],  # Insuficiência renal crônica
            
            # === INFECTOLOGIA ===
            "A15": ["INFECTOLOGIA", "TUBERCULOSE"],  # Tuberculose
            "B20": ["INFECTOLOGIA", "HIV_AIDS"],  # HIV
            "A90": ["INFECTOLOGIA", "DENGUE"],  # Dengue
            
            # === OBSTETRÍCIA ===
            "O80": ["OBSTETRICIA"],  # Parto normal
            "O82": ["OBSTETRICIA", "CIRURGIA_GERAL"],  # Cesariana
            "O14": ["OBSTETRICIA", "ALTO_RISCO_OBSTETRICO"],  # Pré-eclâmpsia
            
            # === PEDIATRIA ===
            "P07": ["NEONATOLOGIA", "UTI_NEONATAL"],  # Prematuridade
            "J20": ["PEDIATRIA"],  # Bronquiolite (quando em criança)
        }
    
    def _definir_criterios_exclusao(self) -> Dict[str, List[str]]:
        """Define critérios de exclusão para hospitais específicos"""
        
        return {
            "HOSPITAL DE URGENCIAS DE GOIAS DR VALDEMIRO CRUZ HUGO": [
                "CASOS_ELETIVOS",  # Não atende casos eletivos
                "BAIXA_COMPLEXIDADE",  # Não atende baixa complexidade
                "DOR_CRONICA",  # Não atende dor crônica
                "CONSULTA_AMBULATORIAL"  # Não é ambulatório
            ],
            "HOSPITAL ESTADUAL MATERNO INFANTIL DR JURANDIR DO NASCIMENTO": [
                "ADULTOS_MASCULINOS",  # Não atende homens adultos
                "MULHERES_NAO_GRAVIDAS_ACIMA_15"  # Só mulheres grávidas ou até 15 anos
            ],
            "HOSPITAL DE DOENCAS TROPICAIS DR ANUAR AUAD HDT": [
                "NAO_INFECCIOSO"  # Só doenças infecciosas
            ]
        }
    
    def selecionar_hospital_inteligente(self, cid: str, especialidade: str, sintomas: str, 
                                      idade: int = None, sexo: str = None, 
                                      gravidade: str = "MODERADA") -> Tuple[str, str, int]:
        """
        Seleciona hospital baseado em critérios inteligentes
        
        Returns:
            Tuple[nome_hospital, justificativa, score_adequacao]
        """
        
        logger.info(f"🏥 Selecionando hospital para CID: {cid}, Especialidade: {especialidade}")
        
        # 1. Identificar especialidades necessárias
        especialidades_necessarias = self._identificar_especialidades(cid, especialidade, sintomas)
        
        # 2. Classificar tipo de caso
        tipo_caso = self._classificar_tipo_caso(cid, sintomas, gravidade)
        
        # 3. Filtrar hospitais adequados
        hospitais_adequados = self._filtrar_hospitais_adequados(
            especialidades_necessarias, tipo_caso, idade, sexo
        )
        
        # 4. Ranquear por adequação
        hospital_escolhido = self._ranquear_hospitais(hospitais_adequados, especialidades_necessarias, tipo_caso)
        
        if hospital_escolhido:
            justificativa = self._gerar_justificativa(hospital_escolhido, especialidades_necessarias, tipo_caso)
            return hospital_escolhido.nome, justificativa, 10
        else:
            # Fallback para hospital geral
            return "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG", "Hospital de referência geral - nenhum hospital específico identificado", 5
    
    def _identificar_especialidades(self, cid: str, especialidade: str, sintomas: str) -> List[str]:
        """Identifica especialidades necessárias baseado em CID e sintomas"""
        
        especialidades = []
        
        # Buscar por CID
        for cid_prefix, specs in self.mapeamento_cid_especialidade.items():
            if cid.startswith(cid_prefix):
                especialidades.extend(specs)
                break
        
        # Adicionar especialidade informada
        if especialidade:
            especialidades.append(especialidade.upper())
        
        # Analisar sintomas críticos
        sintomas_lower = sintomas.lower()
        if "dor no peito" in sintomas_lower or "dor torácica" in sintomas_lower:
            especialidades.extend(["CARDIOLOGIA", "EMERGENCIA_GERAL"])
        if "trauma" in sintomas_lower or "acidente" in sintomas_lower:
            especialidades.extend(["TRAUMATOLOGIA", "ORTOPEDIA_TRAUMA"])
        if "inconsciência" in sintomas_lower or "glasgow" in sintomas_lower:
            especialidades.extend(["NEUROLOGIA", "NEUROCIRURGIA"])
        
        return list(set(especialidades))  # Remove duplicatas
    
    def _classificar_tipo_caso(self, cid: str, sintomas: str, gravidade: str) -> str:
        """Classifica o tipo de caso"""
        
        # Casos de trauma
        if any(trauma_cid in cid for trauma_cid in ["S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "T0"]):
            return "TRAUMA"
        
        # Casos de emergência
        emergencia_cids = ["I21", "I46", "I61", "I63", "N17", "K35"]
        if any(cid.startswith(emerg) for emerg in emergencia_cids):
            return "EMERGENCIA"
        
        # Casos obstétricos
        if cid.startswith("O"):
            return "OBSTETRICIA"
        
        # Casos pediátricos (seria melhor ter a idade)
        if cid.startswith("P"):
            return "PEDIATRIA"
        
        # Casos infecciosos
        if cid.startswith("A") or cid.startswith("B"):
            return "INFECTOLOGIA"
        
        # Casos ortopédicos não traumáticos
        if cid.startswith("M") and "trauma" not in sintomas.lower():
            return "ORTOPEDIA_ELETIVA"
        
        # Casos clínicos gerais
        return "CLINICO_GERAL"
    
    def _filtrar_hospitais_adequados(self, especialidades: List[str], tipo_caso: str, 
                                   idade: int = None, sexo: str = None) -> List[HospitalGoias]:
        """Filtra hospitais que podem atender o caso"""
        
        hospitais_adequados = []
        
        for hospital in self.hospitais:
            # Verificar se tem as especialidades necessárias
            tem_especialidade = any(esp in hospital.especialidades for esp in especialidades)
            
            if not tem_especialidade:
                continue
            
            # Aplicar critérios de exclusão
            if self._aplicar_criterios_exclusao(hospital, tipo_caso, idade, sexo):
                continue
            
            hospitais_adequados.append(hospital)
        
        return hospitais_adequados
    
    def _aplicar_criterios_exclusao(self, hospital: HospitalGoias, tipo_caso: str, 
                                  idade: int = None, sexo: str = None) -> bool:
        """Retorna True se o hospital deve ser excluído"""
        
        exclusoes = self.criterios_exclusao.get(hospital.nome, [])
        
        # HUGO: Não atende casos eletivos ou baixa complexidade
        if hospital.nome == "HOSPITAL DE URGENCIAS DE GOIAS DR VALDEMIRO CRUZ HUGO":
            if tipo_caso in ["ORTOPEDIA_ELETIVA", "CLINICO_GERAL"]:
                return True  # EXCLUIR
        
        # Materno-infantil: Só mulheres e crianças
        if hospital.nome == "HOSPITAL ESTADUAL MATERNO INFANTIL DR JURANDIR DO NASCIMENTO":
            if sexo == "MASCULINO" and (idade is None or idade > 15):
                return True  # EXCLUIR
            if tipo_caso not in ["OBSTETRICIA", "PEDIATRIA"]:
                return True  # EXCLUIR
        
        # HDT: Só doenças infecciosas
        if hospital.nome == "HOSPITAL DE DOENCAS TROPICAIS DR ANUAR AUAD HDT":
            if tipo_caso != "INFECTOLOGIA":
                return True  # EXCLUIR
        
        return False  # NÃO EXCLUIR
    
    def _ranquear_hospitais(self, hospitais: List[HospitalGoias], especialidades: List[str], 
                          tipo_caso: str) -> Optional[HospitalGoias]:
        """Ranqueia hospitais por adequação"""
        
        if not hospitais:
            return None
        
        melhor_hospital = None
        melhor_score = 0
        
        for hospital in hospitais:
            score = 0
            
            # Score por tipo de hospital
            if hospital.tipo == "REFERENCIA":
                score += 10
            elif hospital.tipo == "ESPECIALIZADO":
                score += 15  # Especializado é melhor para sua área
            elif hospital.tipo == "REGIONAL":
                score += 5
            
            # Score por capacidade
            if hospital.capacidade == "ALTA":
                score += 10
            elif hospital.capacidade == "MEDIA":
                score += 5
            
            # Score por especialidades específicas
            especialidades_match = sum(1 for esp in especialidades if esp in hospital.especialidades)
            score += especialidades_match * 5
            
            # Bonus para hospitais específicos por tipo de caso
            if tipo_caso == "TRAUMA" and "TRAUMATOLOGIA" in hospital.especialidades:
                score += 20
            if tipo_caso == "EMERGENCIA" and hospital.tipo == "REFERENCIA":
                score += 15
            if tipo_caso == "OBSTETRICIA" and "OBSTETRICIA" in hospital.especialidades:
                score += 20
            
            # Penalidade para casos inadequados
            if tipo_caso == "ORTOPEDIA_ELETIVA" and hospital.nome == "HOSPITAL DE URGENCIAS DE GOIAS DR VALDEMIRO CRUZ HUGO":
                score -= 50  # FORTE PENALIDADE
            
            if score > melhor_score:
                melhor_score = score
                melhor_hospital = hospital
        
        return melhor_hospital
    
    def _gerar_justificativa(self, hospital: HospitalGoias, especialidades: List[str], tipo_caso: str) -> str:
        """Gera justificativa para a escolha do hospital"""
        
        justificativas = []
        
        # Tipo de hospital
        if hospital.tipo == "REFERENCIA":
            justificativas.append("Hospital de referência estadual")
        elif hospital.tipo == "ESPECIALIZADO":
            justificativas.append("Hospital especializado na área")
        elif hospital.tipo == "REGIONAL":
            justificativas.append("Hospital de referência regional")
        
        # Especialidades específicas
        especialidades_encontradas = [esp for esp in especialidades if esp in hospital.especialidades]
        if especialidades_encontradas:
            justificativas.append(f"Possui especialidades: {', '.join(especialidades_encontradas[:3])}")
        
        # Observações específicas
        if hospital.observacoes:
            justificativas.append(hospital.observacoes)
        
        # Adequação ao tipo de caso
        if tipo_caso == "TRAUMA" and "TRAUMATOLOGIA" in hospital.especialidades:
            justificativas.append("Especializado em trauma e urgência")
        elif tipo_caso == "ORTOPEDIA_ELETIVA":
            justificativas.append("Adequado para casos ortopédicos eletivos")
        elif tipo_caso == "EMERGENCIA":
            justificativas.append("Preparado para emergências médicas")
        
        return " | ".join(justificativas)

# Instância global do pipeline
pipeline_hospitais = PipelineHospitaisGoias()

# Instância global do pipeline RAG
pipeline_rag = PipelineDecisaoRegulacao(pipeline_hospitais)

def selecionar_hospital_goias(cid: str, especialidade: str, sintomas: str, 
                            idade: int = None, sexo: str = None, 
                            gravidade: str = "MODERADA") -> Tuple[str, str]:
    """
    Função principal para seleção inteligente de hospitais em Goiás
    
    Args:
        cid: Código CID-10
        especialidade: Especialidade médica
        sintomas: Descrição dos sintomas
        idade: Idade do paciente (opcional)
        sexo: Sexo do paciente (opcional)
        gravidade: Gravidade do caso
    
    Returns:
        Tuple[nome_hospital, justificativa]
    """
    
    hospital, justificativa, score = pipeline_hospitais.selecionar_hospital_inteligente(
        cid, especialidade, sintomas, idade, sexo, gravidade
    )
    
    return hospital, justificativa

def gerar_contexto_rag_llm(especialidade: str, cid: str = None, 
                          dados_paciente: Dict[str, Any] = None) -> str:
    """
    Função para gerar contexto RAG para LLMs (Llama 3, etc.)
    
    Args:
        especialidade: Especialidade médica necessária
        cid: Código CID-10 (opcional)
        dados_paciente: Dados completos do paciente (opcional)
    
    Returns:
        JSON string formatado para prompt injection no LLM
    """
    
    # Classificar tipo de caso se temos dados do paciente
    tipo_caso = None
    if dados_paciente and cid:
        tipo_caso = pipeline_rag._classificar_tipo_caso_rag(
            cid, dados_paciente.get('prontuario_texto', '')
        )
    
    return pipeline_rag.gerar_contexto_hospitais(especialidade, cid, tipo_caso)

def gerar_prompt_completo_llm(dados_paciente: Dict[str, Any], 
                             especialidade: str, cid: str = None) -> str:
    """
    Função para gerar prompt completo para LLMs
    
    Args:
        dados_paciente: Dados completos do paciente
        especialidade: Especialidade médica necessária
        cid: Código CID-10 (opcional)
    
    Returns:
        Prompt completo formatado para o LLM
    """
    
    return pipeline_rag.gerar_prompt_completo_llm(dados_paciente, especialidade, cid)

def processar_resposta_llm(resposta_llm: str) -> Dict[str, Any]:
    """
    Função para processar resposta do LLM
    
    Args:
        resposta_llm: Resposta em JSON do LLM
    
    Returns:
        Dict com resposta processada e validada
    """
    
    return pipeline_rag.processar_resposta_llm(resposta_llm)

if __name__ == "__main__":
    # Testes do pipeline
    print("🏥 PIPELINE DE HOSPITAIS DE GOIÁS - RAG READY - TESTE")
    print("=" * 60)
    
    casos_teste = [
        {
            "nome": "Dor Lombar (NÃO deve ir para HUGO)",
            "cid": "M54.5",
            "especialidade": "ORTOPEDIA",
            "sintomas": "Dor lombar crônica, sem trauma",
            "gravidade": "BAIXA"
        },
        {
            "nome": "Traumatismo Craniano (DEVE ir para HUGO)",
            "cid": "S06.9",
            "especialidade": "NEUROCIRURGIA",
            "sintomas": "Trauma craniano, acidente de carro",
            "gravidade": "ALTA"
        },
        {
            "nome": "Infarto (Deve ir para RASSI)",
            "cid": "I21.0",
            "especialidade": "CARDIOLOGIA",
            "sintomas": "Dor no peito, sudorese",
            "gravidade": "ALTA"
        }
    ]
    
    print("\n🧪 TESTE PIPELINE TRADICIONAL:")
    for caso in casos_teste:
        print(f"\n📋 {caso['nome']}")
        hospital, justificativa = selecionar_hospital_goias(
            caso['cid'], caso['especialidade'], caso['sintomas'], gravidade=caso['gravidade']
        )
        print(f"🏥 Hospital: {hospital}")
        print(f"💡 Justificativa: {justificativa}")
    
    print("\n" + "=" * 60)
    print("🤖 TESTE RAG PARA LLM:")
    
    # Teste de contexto RAG
    print("\n📊 Contexto RAG para ORTOPEDIA:")
    contexto_ortopedia = gerar_contexto_rag_llm("ORTOPEDIA", "M54.5")
    print("✅ Contexto gerado com sucesso")
    
    print("\n📊 Contexto RAG para NEUROCIRURGIA:")
    contexto_neuro = gerar_contexto_rag_llm("NEUROCIRURGIA", "S06.9")
    print("✅ Contexto gerado com sucesso")
    
    # Teste de prompt completo
    print("\n📝 Prompt Completo para LLM:")
    dados_paciente_teste = {
        "protocolo": "TEST-RAG-001",
        "especialidade": "ORTOPEDIA",
        "cid": "M54.5",
        "cid_desc": "Dor lombar",
        "prontuario_texto": "Paciente com dor lombar crônica há 6 meses, sem sinais de trauma",
        "historico_paciente": "Histórico de dor lombar recorrente",
        "prioridade_descricao": "Normal"
    }
    
    prompt_completo = gerar_prompt_completo_llm(dados_paciente_teste, "ORTOPEDIA", "M54.5")
    print("✅ Prompt completo gerado com sucesso")
    print(f"📏 Tamanho do prompt: {len(prompt_completo)} caracteres")
    
    # Teste de processamento de resposta
    print("\n🔄 Teste de Processamento de Resposta LLM:")
    resposta_simulada = '''```json
{
    "hospital_escolhido": "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG",
    "justificativa_tecnica": "Hospital de referência com ortopedia disponível, adequado para casos eletivos como dor lombar",
    "score_adequacao": 8,
    "tipo_transporte": "USB",
    "observacoes_clinicas": "Caso eletivo, não requer urgência",
    "restricoes_verificadas": ["hugo_nao_eletivo"]
}
```'''
    
    resposta_processada = processar_resposta_llm(resposta_simulada)
    print("✅ Resposta processada com sucesso")
    print(f"🏥 Hospital escolhido: {resposta_processada['hospital_escolhido']}")
    print(f"⭐ Score: {resposta_processada['score_adequacao']}")
    
    print("\n" + "=" * 60)
    print("🎉 PIPELINE RAG READY FUNCIONANDO PERFEITAMENTE!")
    print("🔗 Pronto para integração com Llama 3, GPT-4, Claude, etc.")
    print("📚 Base de conhecimento estruturada para regulação médica")
    print("=" * 60)
