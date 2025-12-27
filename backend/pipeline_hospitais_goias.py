#!/usr/bin/env python3
"""
PIPELINE INTELIGENTE DE HOSPITAIS DE GOIÁS
Sistema de IA para encaminhamento correto baseado em especialidades reais
"""

from typing import Dict, List, Optional, Tuple
import logging

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
        self.score_disponibilidade = 10  # Simulado - em produção viria de API real

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

if __name__ == "__main__":
    # Testes do pipeline
    print("🏥 PIPELINE DE HOSPITAIS DE GOIÁS - TESTE")
    print("=" * 50)
    
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
    
    for caso in casos_teste:
        print(f"\n📋 {caso['nome']}")
        hospital, justificativa = selecionar_hospital_goias(
            caso['cid'], caso['especialidade'], caso['sintomas'], gravidade=caso['gravidade']
        )
        print(f"🏥 Hospital: {hospital}")
        print(f"💡 Justificativa: {justificativa}")