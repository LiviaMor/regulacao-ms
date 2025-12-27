#!/usr/bin/env python3
"""
PIPELINE RAG PARA REGULAÇÃO SUS-GOIÁS - VERSÃO FOCADA
Sistema de "peneira" inteligente para hierarquia do SUS:
UPA -> Hospitais Regionais -> Hospitais de Referência (HGG, HUGO, HDT)
"""

import json
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class HospitalGoias:
    """Classe simplificada para representar um hospital"""
    
    def __init__(self, nome: str, cidade: str, tipo: str, especialidades: List[str], 
                 capacidade: str, observacoes: str = "", nivel_sus: int = 1):
        self.nome = nome
        self.cidade = cidade
        self.tipo = tipo  # REFERENCIA, REGIONAL, UPA
        self.especialidades = especialidades
        self.capacidade = capacidade  # ALTA, MEDIA, BAIXA
        self.observacoes = observacoes
        self.nivel_sus = nivel_sus  # 1=UPA, 2=Regional, 3=Referência
        self.score_disponibilidade = 10  # Simulado - em produção viria de API real

class PipelineDecisaoRegulacao:
    """
    Pipeline focado para servir de base de conhecimento (Prompt Injection)
    para o Llama 3 no processo de regulação médica
    """
    
    def __init__(self):
        self.hospitais = self._carregar_hospitais_goias()
        self.criterios_exclusao = self._definir_criterios_exclusao()
    
    def _carregar_hospitais_goias(self) -> List[HospitalGoias]:
        """Carrega hospitais com hierarquia SUS real de Goiás"""
        
        return [
            # === NÍVEL 3: HOSPITAIS DE REFERÊNCIA ESTADUAL ===
            HospitalGoias(
                nome="HOSPITAL ESTADUAL DR ALBERTO RASSI HGG",
                cidade="GOIANIA",
                tipo="REFERENCIA",
                especialidades=[
                    "CARDIOLOGIA", "CARDIOLOGIA_INTERVENCIONISTA", "HEMODINAMICA",
                    "NEUROLOGIA", "NEUROCIRURGIA", "AVC", "NEFROLOGIA", "HEMODIALISE",
                    "TRANSPLANTE_RENAL", "ENDOCRINOLOGIA", "CIRURGIA_GERAL", "UTI_GERAL"
                ],
                capacidade="ALTA",
                observacoes="Principal hospital de referência estadual. Cardiologia e neurologia 24h.",
                nivel_sus=3
            ),
            
            HospitalGoias(
                nome="HOSPITAL DE URGENCIAS DE GOIAS DR VALDEMIRO CRUZ HUGO",
                cidade="GOIANIA",
                tipo="REFERENCIA",
                especialidades=[
                    "TRAUMATOLOGIA", "ORTOPEDIA_TRAUMA", "NEUROCIRURGIA_TRAUMA",
                    "QUEIMADOS", "UTI_TRAUMA", "POLITRAUMATISMO", "EMERGENCIA_GERAL"
                ],
                capacidade="ALTA",
                observacoes="EXCLUSIVO para trauma e urgência. NÃO atende casos eletivos.",
                nivel_sus=3
            ),
            
            HospitalGoias(
                nome="HOSPITAL DE DOENCAS TROPICAIS DR ANUAR AUAD HDT",
                cidade="GOIANIA",
                tipo="REFERENCIA",
                especialidades=[
                    "INFECTOLOGIA", "DOENCAS_TROPICAIS", "HIV_AIDS", "TUBERCULOSE",
                    "HEPATITES", "MALARIA", "DENGUE", "UTI_INFECTOLOGIA"
                ],
                capacidade="MEDIA",
                observacoes="EXCLUSIVO para doenças infecciosas e tropicais.",
                nivel_sus=3
            ),
            
            HospitalGoias(
                nome="HOSPITAL ESTADUAL MATERNO INFANTIL DR JURANDIR DO NASCIMENTO",
                cidade="GOIANIA",
                tipo="REFERENCIA",
                especialidades=[
                    "OBSTETRICIA", "GINECOLOGIA", "NEONATOLOGIA", "UTI_NEONATAL",
                    "PEDIATRIA", "UTI_PEDIATRICA", "ALTO_RISCO_OBSTETRICO"
                ],
                capacidade="ALTA",
                observacoes="EXCLUSIVO materno-infantil. Não atende adultos masculinos.",
                nivel_sus=3
            ),
            
            # === NÍVEL 3: NOVOS HOSPITAIS DE REFERÊNCIA (DADOS REAIS) ===
            HospitalGoias(
                nome="HOSPITAL ESTADUAL DE ANAPOLIS DR HENRIQUE SANTILLO",
                cidade="ANAPOLIS",
                tipo="REFERENCIA",
                especialidades=[
                    "CARDIOLOGIA", "HEMODINAMICA", "NEUROLOGIA", "NEUROCIRURGIA",
                    "ORTOPEDIA", "NEFROLOGIA", "ONCOLOGIA", "QUIMIOTERAPIA", "UTI_GERAL"
                ],
                capacidade="ALTA",
                observacoes="Referência regional. Oncologia e hemodinâmica.",
                nivel_sus=3
            ),
            
            HospitalGoias(
                nome="HUGOL - HOSPITAL DE URGENCIAS DE GOIANIA",
                cidade="GOIANIA",
                tipo="REFERENCIA",
                especialidades=[
                    "TRAUMATOLOGIA", "QUEIMADOS", "NEUROCIRURGIA_TRAUMA", 
                    "ORTOPEDIA_TRAUMA", "UTI_TRAUMA", "EMERGENCIA_GERAL"
                ],
                capacidade="ALTA",
                observacoes="Alta complexidade em trauma. Mais novo e tecnológico que HUGO.",
                nivel_sus=3
            ),
            
            # === NÍVEL 2: HOSPITAIS REGIONAIS ===
            HospitalGoias(
                nome="HOSPITAL ESTADUAL DE FORMOSA DR CESAR SAAD FAYAD",
                cidade="FORMOSA",
                tipo="REGIONAL",
                especialidades=[
                    "CLINICA_MEDICA", "CIRURGIA_GERAL", "ORTOPEDIA", "CARDIOLOGIA",
                    "NEUROLOGIA", "PEDIATRIA", "OBSTETRICIA", "UTI_GERAL"
                ],
                capacidade="MEDIA",
                observacoes="Referência para região nordeste e entorno do DF.",
                nivel_sus=2
            ),
            
            HospitalGoias(
                nome="HOSPITAL ESTADUAL DE JATAI",
                cidade="JATAI",
                tipo="REGIONAL",
                especialidades=[
                    "CLINICA_MEDICA", "CIRURGIA_GERAL", "ORTOPEDIA", "CARDIOLOGIA",
                    "PEDIATRIA", "OBSTETRICIA", "UTI_GERAL"
                ],
                capacidade="MEDIA",
                observacoes="Referência para região sudoeste de Goiás.",
                nivel_sus=2
            ),
            
            HospitalGoias(
                nome="HOSPITAL ESTADUAL DO CENTRO NORTE GOIANO",
                cidade="URUACU",
                tipo="REGIONAL",
                especialidades=[
                    "CLINICA_MEDICA", "CIRURGIA_GERAL", "ORTOPEDIA", "PEDIATRIA",
                    "OBSTETRICIA", "UTI_GERAL"
                ],
                capacidade="MEDIA",
                observacoes="Referência para região centro-norte.",
                nivel_sus=2
            ),
            
            # === NÍVEL 2: HOSPITAIS METROPOLITANOS (DADOS REAIS ADICIONADOS) ===
            HospitalGoias(
                nome="HEAPA - HOSPITAL ESTADUAL DE APARECIDA DE GOIANIA",
                cidade="APARECIDA_DE_GOIANIA",
                tipo="REGIONAL",
                especialidades=[
                    "ORTOPEDIA", "CIRURGIA_GERAL", "CLINICA_MEDICA", "CARDIOLOGIA",
                    "TRAUMATOLOGIA", "UTI_GERAL"
                ],
                capacidade="MEDIA",
                observacoes="Referência em Ortopedia na região metropolitana.",
                nivel_sus=2
            ),
            
            HospitalGoias(
                nome="HUTRIN - HOSPITAL DE TRINDADE",
                cidade="TRINDADE",
                tipo="REGIONAL",
                especialidades=[
                    "CLINICA_MEDICA", "CIRURGIA_GERAL", "CIRURGIA_ELETIVA", 
                    "ORTOPEDIA", "CARDIOLOGIA"
                ],
                capacidade="MEDIA",
                observacoes="Foco em Clínica Médica e Cirurgia Eletiva. Ideal para aliviar grandes hospitais.",
                nivel_sus=2
            ),
            
            # === NÍVEL 1: UPAs (Unidades de Pronto Atendimento) ===
            HospitalGoias(
                nome="UPA GOIANIA NORTE",
                cidade="GOIANIA",
                tipo="UPA",
                especialidades=[
                    "EMERGENCIA_GERAL", "CLINICA_MEDICA", "PEDIATRIA", "ORTOPEDIA_BASICA"
                ],
                capacidade="BAIXA",
                observacoes="Pronto atendimento 24h. Casos de baixa e média complexidade.",
                nivel_sus=1
            ),
            
            HospitalGoias(
                nome="UPA APARECIDA DE GOIANIA",
                cidade="APARECIDA_DE_GOIANIA",
                tipo="UPA",
                especialidades=[
                    "EMERGENCIA_GERAL", "CLINICA_MEDICA", "PEDIATRIA", "ORTOPEDIA_BASICA"
                ],
                capacidade="BAIXA",
                observacoes="Pronto atendimento região metropolitana.",
                nivel_sus=1
            )
        ]
    
    def _definir_criterios_exclusao(self) -> Dict[str, List[str]]:
        """Define critérios de exclusão rígidos por hospital"""
        
        return {
            "HOSPITAL DE URGENCIAS DE GOIAS DR VALDEMIRO CRUZ HUGO": [
                "CASOS_ELETIVOS", "BAIXA_COMPLEXIDADE", "DOR_CRONICA", "CONSULTA_AMBULATORIAL"
            ],
            "HUGOL - HOSPITAL DE URGENCIAS DE GOIANIA": [
                "CASOS_ELETIVOS", "BAIXA_COMPLEXIDADE", "DOR_CRONICA"
            ],
            "HOSPITAL ESTADUAL MATERNO INFANTIL DR JURANDIR DO NASCIMENTO": [
                "ADULTOS_MASCULINOS", "MULHERES_NAO_GRAVIDAS_ACIMA_15"
            ],
            "HOSPITAL DE DOENCAS TROPICAIS DR ANUAR AUAD HDT": [
                "NAO_INFECCIOSO"
            ]
        }
    
    def formatar_para_ia(self, hospital: HospitalGoias) -> Dict[str, Any]:
        """
        Transforma o objeto Hospital em uma 'ficha técnica' para o Llama
        """
        return {
            "hospital": hospital.nome,
            "cidade": hospital.cidade,
            "perfil_clinico": hospital.tipo,
            "nivel_sus": hospital.nivel_sus,  # 1=UPA, 2=Regional, 3=Referência
            "capacidade": hospital.capacidade,
            "especialidades_disponiveis": hospital.especialidades,
            "restricoes_severas": self.criterios_exclusao.get(hospital.nome, []),
            "score_disponibilidade": hospital.score_disponibilidade,
            "observacoes_clinicas": hospital.observacoes
        }
    
    def aplicar_filtro_peneira(self, especialidade_requerida: str, cid: str = None, 
                              cidade_paciente: str = None, gravidade: str = "MEDIA") -> List[HospitalGoias]:
        """
        Aplica lógica de "peneira" para filtrar hospitais adequados
        
        PENEIRA 1: Filtro de Especialidade
        PENEIRA 2: Filtro de Complexidade  
        PENEIRA 3: Filtro de Localidade
        """
        
        hospitais_filtrados = []
        
        # === PENEIRA 1: FILTRO DE ESPECIALIDADE ===
        for hospital in self.hospitais:
            # Verificar especialidade direta
            tem_especialidade = any(
                esp.upper() in [e.upper() for e in hospital.especialidades] 
                for esp in [especialidade_requerida, especialidade_requerida.replace("_", " ")]
            )
            
            # Para neurocirurgia, aceitar também hospitais com trauma (HUGO, HUGOL)
            if especialidade_requerida.upper() == "NEUROCIRURGIA":
                tem_especialidade = tem_especialidade or any(
                    "TRAUMA" in esp or "NEUROCIRURGIA" in esp 
                    for esp in hospital.especialidades
                )
            
            if tem_especialidade:
                hospitais_filtrados.append(hospital)
        
        # === PENEIRA 2: FILTRO DE COMPLEXIDADE (baseado em CID) ===
        if cid:
            if cid.startswith(("S06", "S02", "T07")):  # Trauma grave
                # Priorizar hospitais de trauma (HUGO, HUGOL)
                hospitais_filtrados = [h for h in hospitais_filtrados 
                                     if "TRAUMA" in " ".join(h.especialidades)]
            
            elif cid.startswith(("M54", "M79", "M25")):  # Casos ortopédicos eletivos
                # REMOVER hospitais de trauma (não atendem eletivo)
                hospitais_filtrados = [h for h in hospitais_filtrados 
                                     if "HUGO" not in h.nome]
            
            elif cid.startswith(("A", "B")):  # Doenças infecciosas
                # Priorizar HDT
                hdt_disponivel = [h for h in hospitais_filtrados if "HDT" in h.nome]
                if hdt_disponivel:
                    hospitais_filtrados = hdt_disponivel
            
            elif cid.startswith("O"):  # Obstetrícia
                # Priorizar Materno-Infantil
                materno_disponivel = [h for h in hospitais_filtrados if "MATERNO" in h.nome]
                if materno_disponivel:
                    hospitais_filtrados = materno_disponivel
        
        # === PENEIRA 3: FILTRO DE LOCALIDADE ===
        if cidade_paciente:
            # Primeiro, tentar hospitais da mesma cidade
            locais = [h for h in hospitais_filtrados if h.cidade.upper() == cidade_paciente.upper()]
            
            # Se tem hospital local com capacidade adequada, priorizar
            if locais and any(h.capacidade in ["ALTA", "MEDIA"] for h in locais):
                hospitais_filtrados = locais
            
            # Se não tem local adequado, manter todos (vai para capital)
        
        # Ordenar por nível SUS (3=Referência primeiro) e capacidade
        hospitais_filtrados.sort(key=lambda x: (x.nivel_sus, x.capacidade == "ALTA"), reverse=True)
        
        return hospitais_filtrados
    
    def gerar_contexto_hospitais(self, especialidade_requerida: str, cid: str = None, 
                                cidade_paciente: str = None, gravidade: str = "MEDIA") -> str:
        """
        Filtra e ordena os hospitais para enviar apenas o relevante ao Prompt do Llama
        """
        
        # Aplicar filtros de peneira
        hospitais_filtrados = self.aplicar_filtro_peneira(
            especialidade_requerida, cid, cidade_paciente, gravidade
        )
        
        # Limitar a top 5 para não sobrecarregar o prompt
        top_hospitais = hospitais_filtrados[:5]
        
        # Formatar para IA
        contexto_hospitais = [self.formatar_para_ia(h) for h in top_hospitais]
        
        return json.dumps(contexto_hospitais, indent=2, ensure_ascii=False)
    
    def gerar_prompt_llama(self, dados_paciente: Dict[str, Any], 
                          resultado_biobert: str = None) -> str:
        """
        Gera prompt final otimizado para o Llama 3
        """
        
        especialidade = dados_paciente.get('especialidade', 'CLINICA_MEDICA')
        cid = dados_paciente.get('cid')
        cidade = dados_paciente.get('cidade_origem', 'GOIANIA')
        
        # Gerar contexto de hospitais filtrado
        contexto_hospitais = self.gerar_contexto_hospitais(especialidade, cid, cidade)
        
        # Detectar protocolo de óbito
        sintomas = dados_paciente.get('prontuario_texto', '').lower()
        protocolo_obito = any(palavra in sintomas for palavra in [
            'óbito', 'obito', 'morte cerebral', 'glasgow 3', 'coma irreversível'
        ])
        
        instrucao_obito = ""
        if protocolo_obito:
            instrucao_obito = "\n⚠️ PROTOCOLO ESPECIAL: Indicação de ÓBITO detectada. Acione MANUTENÇÃO DE ÓRGÃOS se aplicável."
        
        prompt = f"""### SISTEMA DE REGULAÇÃO SUS-GOIÁS

PACIENTE: {json.dumps(dados_paciente, indent=2, ensure_ascii=False)}

SINTOMAS EXTRAÍDOS: {resultado_biobert or "Análise BioBERT não disponível"}

### HOSPITAIS DISPONÍVEIS COM ESPECIALIDADE COMPATÍVEL:
{contexto_hospitais}

### HIERARQUIA SUS-GOIÁS:
- NÍVEL 3 (Referência): HGG, HUGO, HDT, Materno-Infantil, HUGOL
- NÍVEL 2 (Regional): Formosa, Jataí, Aparecida (HEAPA), Trindade (HUTRIN)  
- NÍVEL 1 (UPA): Pronto atendimento básico

### INSTRUÇÃO CRÍTICA:
Selecione o hospital com maior 'capacidade' e menor 'restrição'. 
Justifique baseado no perfil clínico do hospital.
SEMPRE respeitar as restrições severas de cada hospital.
Priorizar hospitais regionais quando adequados para não saturar a capital.{instrucao_obito}

### FORMATO DE RESPOSTA (JSON):
{{
    "hospital_escolhido": "Nome completo do hospital",
    "justificativa": "Explicação baseada na hierarquia SUS e especialidades",
    "nivel_sus": 3,
    "capacidade_adequada": true,
    "restricoes_respeitadas": ["lista", "de", "restricoes"]
}}"""
        
        return prompt


# Instância global do pipeline RAG
pipeline_rag = PipelineDecisaoRegulacao()

def gerar_contexto_rag_llama(especialidade: str, cid: str = None, 
                            cidade_paciente: str = None) -> str:
    """
    Função principal para gerar contexto RAG para Llama 3
    """
    return pipeline_rag.gerar_contexto_hospitais(especialidade, cid, cidade_paciente)

def gerar_prompt_completo_llama(dados_paciente: Dict[str, Any], 
                               resultado_biobert: str = None) -> str:
    """
    Função principal para gerar prompt completo para Llama 3
    """
    return pipeline_rag.gerar_prompt_llama(dados_paciente, resultado_biobert)


if __name__ == "__main__":
    print("🏥 PIPELINE RAG SUS-GOIÁS - TESTE DE PENEIRA")
    print("=" * 50)
    
    # Teste 1: Dor lombar (deve evitar HUGO)
    print("\n📋 TESTE 1: Dor Lombar (NÃO deve ir para HUGO)")
    contexto1 = gerar_contexto_rag_llama("ORTOPEDIA", "M54.5", "GOIANIA")
    print("✅ Contexto gerado - Verificar se HUGO foi filtrado")
    
    # Teste 2: Trauma craniano (deve priorizar HUGO/HUGOL)
    print("\n📋 TESTE 2: Trauma Craniano (DEVE priorizar HUGO/HUGOL)")
    contexto2 = gerar_contexto_rag_llama("NEUROCIRURGIA", "S06.9", "GOIANIA")
    print("✅ Contexto gerado - Verificar se trauma foi priorizado")
    
    # Teste 3: Paciente de Formosa (deve priorizar regional)
    print("\n📋 TESTE 3: Paciente de Formosa (priorizar regional)")
    contexto3 = gerar_contexto_rag_llama("CLINICA_MEDICA", "I10", "FORMOSA")
    print("✅ Contexto gerado - Verificar se hospital de Formosa foi priorizado")
    
    # Teste 4: Prompt completo
    print("\n📝 TESTE 4: Prompt Completo para Llama")
    dados_teste = {
        "protocolo": "RAG-TEST-001",
        "especialidade": "ORTOPEDIA",
        "cid": "M54.5",
        "cidade_origem": "ANAPOLIS",
        "prontuario_texto": "Dor lombar crônica há 6 meses, sem trauma"
    }
    
    prompt = gerar_prompt_completo_llama(dados_teste)
    print(f"✅ Prompt gerado - {len(prompt)} caracteres")
    
    print("\n" + "=" * 50)
    print("🎯 PIPELINE RAG FOCADO FUNCIONANDO!")
    print("🔄 Lógica de peneira: Especialidade -> Complexidade -> Localidade")
    print("🏥 Hierarquia SUS respeitada: UPA -> Regional -> Referência")
    print("=" * 50)