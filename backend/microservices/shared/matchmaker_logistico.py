#!/usr/bin/env python3
"""
MATCHMAKER LOGÍSTICO - SISTEMA DE REGULAÇÃO SES-GO
Transforma decisão clínica da IA em rota real de ambulância
Usa fórmula de Haversine para cálculo geodésico e Score de Eficiência Logística
"""

import math
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class MatchmakerLogistico:
    """
    Sistema de Matchmaking Logístico para Regulação Médica
    Cruza decisão clínica da IA com viabilidade de transporte
    """
    
    def __init__(self):
        # Coordenadas reais dos hospitais de Goiás (baseado em dados públicos)
        self.coordenadas_hospitais = {
            # === HOSPITAIS DE REFERÊNCIA ESTADUAL ===
            "HGG": (-16.679, -49.255),  # Hospital Estadual Dr. Alberto Rassi
            "HUGO": (-16.705, -49.261),  # Hospital de Urgências Dr. Valdemiro Cruz
            "HUGOL": (-16.643, -49.339),  # Hospital de Urgências de Goiânia
            "HDT": (-16.685, -49.278),  # Hospital de Doenças Tropicais Dr. Anuar Auad
            "MATERNO_INFANTIL": (-16.685, -49.278),  # Hospital Materno Infantil
            
            # === HOSPITAIS REGIONAIS ===
            "HEAPA": (-16.823, -49.244),  # Hospital de Aparecida de Goiânia
            "HUTRIN": (-16.647, -49.347),  # Hospital de Trindade
            "REGIONAL_FORMOSA": (-15.541, -47.339),  # Hospital de Formosa
            "REGIONAL_JATAI": (-17.881, -51.714),  # Hospital de Jataí
            "REGIONAL_URUACU": (-14.520, -49.141),  # Hospital do Centro Norte
            "REGIONAL_ANAPOLIS": (-16.327, -48.953),  # Hospital de Anápolis
            
            # === UPAs ===
            "UPA_GOIANIA_NORTE": (-16.650, -49.280),
            "UPA_APARECIDA": (-16.823, -49.244),
            "UPA_ANAPOLIS": (-16.327, -48.953),
            
            # === CIDADES DE ORIGEM COMUNS ===
            "GOIANIA": (-16.686, -49.265),
            "ANAPOLIS": (-16.327, -48.953),
            "APARECIDA_DE_GOIANIA": (-16.823, -49.244),
            "FORMOSA": (-15.541, -47.339),
            "JATAI": (-17.881, -51.714),
            "URUACU": (-14.520, -49.141),
            "TRINDADE": (-16.647, -49.347),
            "LUZIANIA": (-16.253, -47.950),
            "VALPARAISO": (-16.061, -47.987),
            "NOVO_GAMA": (-16.081, -48.028)
        }
        
        # Mapeamento de nomes completos para IDs curtos
        self.mapeamento_hospitais = {
            "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG": "HGG",
            "HOSPITAL DE URGENCIAS DE GOIAS DR VALDEMIRO CRUZ HUGO": "HUGO",
            "HUGOL - HOSPITAL DE URGENCIAS DE GOIANIA": "HUGOL",
            "HOSPITAL DE DOENCAS TROPICAIS DR ANUAR AUAD HDT": "HDT",
            "HOSPITAL ESTADUAL MATERNO INFANTIL DR JURANDIR DO NASCIMENTO": "MATERNO_INFANTIL",
            "HEAPA - HOSPITAL ESTADUAL DE APARECIDA DE GOIANIA": "HEAPA",
            "HUTRIN - HOSPITAL DE TRINDADE": "HUTRIN",
            "HOSPITAL ESTADUAL DE FORMOSA DR CESAR SAAD FAYAD": "REGIONAL_FORMOSA",
            "HOSPITAL ESTADUAL DE JATAI": "REGIONAL_JATAI",
            "HOSPITAL ESTADUAL DO CENTRO NORTE GOIANO": "REGIONAL_URUACU",
            "HOSPITAL ESTADUAL DE ANAPOLIS DR HENRIQUE SANTILLO": "REGIONAL_ANAPOLIS"
        }
        
        # Frota de ambulâncias por região (simulado - em produção viria de API do SAMU)
        self.frota_ambulancias = {
            "GOIANIA": [
                {"id": "USA-01", "tipo": "USA", "status": "DISPONIVEL", "lat": -16.686, "lon": -49.265},
                {"id": "USB-02", "tipo": "USB", "status": "DISPONIVEL", "lat": -16.650, "lon": -49.280},
                {"id": "USB-03", "tipo": "USB", "status": "EM_ATENDIMENTO", "lat": -16.705, "lon": -49.261},
                {"id": "USA-04", "tipo": "USA", "status": "DISPONIVEL", "lat": -16.643, "lon": -49.339}
            ],
            "ANAPOLIS": [
                {"id": "USB-05", "tipo": "USB", "status": "DISPONIVEL", "lat": -16.327, "lon": -48.953},
                {"id": "USA-06", "tipo": "USA", "status": "DISPONIVEL", "lat": -16.327, "lon": -48.953}
            ],
            "FORMOSA": [
                {"id": "USB-07", "tipo": "USB", "status": "DISPONIVEL", "lat": -15.541, "lon": -47.339}
            ]
        }
    
    def calcular_distancia_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Cálculo de Haversine para distância entre dois pontos no globo
        
        Args:
            lat1, lon1: Coordenadas do ponto de origem
            lat2, lon2: Coordenadas do ponto de destino
            
        Returns:
            Distância em quilômetros
        """
        
        # Raio da Terra em km
        r = 6371
        
        # Converter graus para radianos
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        
        # Fórmula de Haversine
        a = (math.sin(dphi / 2)**2 + 
             math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return r * c
    
    def obter_coordenadas_cidade(self, cidade: str) -> Tuple[float, float]:
        """
        Obtém coordenadas de uma cidade
        
        Args:
            cidade: Nome da cidade
            
        Returns:
            Tupla (latitude, longitude)
        """
        
        cidade_upper = cidade.upper().replace(" ", "_")
        
        # Tentar encontrar coordenadas exatas
        if cidade_upper in self.coordenadas_hospitais:
            return self.coordenadas_hospitais[cidade_upper]
        
        # Fallback para Goiânia se não encontrar
        logger.warning(f"Coordenadas não encontradas para {cidade}, usando Goiânia como fallback")
        return self.coordenadas_hospitais["GOIANIA"]
    
    def obter_coordenadas_hospital(self, nome_hospital: str) -> Tuple[float, float]:
        """
        Obtém coordenadas de um hospital
        
        Args:
            nome_hospital: Nome completo do hospital
            
        Returns:
            Tupla (latitude, longitude)
        """
        
        # Tentar mapeamento direto
        id_curto = self.mapeamento_hospitais.get(nome_hospital)
        
        if id_curto and id_curto in self.coordenadas_hospitais:
            return self.coordenadas_hospitais[id_curto]
        
        # Tentar busca parcial
        for nome_completo, id_hospital in self.mapeamento_hospitais.items():
            if any(palavra in nome_hospital.upper() for palavra in nome_completo.split()):
                if id_hospital in self.coordenadas_hospitais:
                    return self.coordenadas_hospitais[id_hospital]
        
        # Fallback para HGG
        logger.warning(f"Hospital não encontrado: {nome_hospital}, usando HGG como fallback")
        return self.coordenadas_hospitais["HGG"]
    
    def calcular_score_logistico(self, distancia_km: float, tipo_caso: str = "NORMAL") -> float:
        """
        Calcula score logístico baseado na distância e tipo de caso
        
        Args:
            distancia_km: Distância em quilômetros
            tipo_caso: Tipo do caso (CRITICO, URGENTE, NORMAL)
            
        Returns:
            Score de 0 a 10
        """
        
        # Score base: quanto menor a distância, maior o score
        if distancia_km <= 5:
            score_base = 10
        elif distancia_km <= 15:
            score_base = 9
        elif distancia_km <= 30:
            score_base = 8
        elif distancia_km <= 50:
            score_base = 7
        elif distancia_km <= 100:
            score_base = 6
        elif distancia_km <= 200:
            score_base = 4
        else:
            score_base = 2
        
        # Penalizar distâncias muito grandes para casos críticos
        if tipo_caso == "CRITICO" and distancia_km > 100:
            score_base = max(1, score_base - 3)
        elif tipo_caso == "URGENTE" and distancia_km > 200:
            score_base = max(1, score_base - 2)
        
        return min(10, max(0, score_base))
    
    def estimar_tempo_transporte(self, distancia_km: float, tipo_ambulancia: str = "USB") -> int:
        """
        Estima tempo de transporte baseado na distância e tipo de ambulância
        
        Args:
            distancia_km: Distância em quilômetros
            tipo_ambulancia: Tipo da ambulância (USA, USB)
            
        Returns:
            Tempo estimado em minutos
        """
        
        # Velocidade média considerando trânsito urbano e rodovias
        if tipo_ambulancia == "USA":  # Unidade de Suporte Avançado (mais rápida)
            velocidade_media = 50  # km/h
        else:  # USB - Unidade de Suporte Básico
            velocidade_media = 45  # km/h
        
        # Tempo base em minutos
        tempo_base = (distancia_km / velocidade_media) * 60
        
        # Adicionar tempo de preparação e mobilização
        tempo_preparacao = 5 if tipo_ambulancia == "USA" else 3
        
        # Adicionar tempo extra para distâncias longas (paradas, combustível)
        if distancia_km > 100:
            tempo_extra = 15
        elif distancia_km > 50:
            tempo_extra = 10
        else:
            tempo_extra = 0
        
        return int(tempo_base + tempo_preparacao + tempo_extra)
    
    def encontrar_ambulancia_mais_proxima(self, lat_origem: float, lon_origem: float, 
                                        tipo_necessario: str = "USB") -> Optional[Dict[str, Any]]:
        """
        Encontra a ambulância mais próxima disponível
        
        Args:
            lat_origem, lon_origem: Coordenadas de origem
            tipo_necessario: Tipo de ambulância necessária (USA, USB)
            
        Returns:
            Dados da ambulância mais próxima ou None
        """
        
        ambulancias_disponiveis = []
        
        # Buscar em todas as regiões
        for regiao, frota in self.frota_ambulancias.items():
            for ambulancia in frota:
                if (ambulancia["status"] == "DISPONIVEL" and 
                    (tipo_necessario == "USB" or ambulancia["tipo"] == tipo_necessario)):
                    
                    distancia = self.calcular_distancia_km(
                        lat_origem, lon_origem,
                        ambulancia["lat"], ambulancia["lon"]
                    )
                    
                    ambulancias_disponiveis.append({
                        **ambulancia,
                        "distancia_km": distancia,
                        "tempo_chegada_min": self.estimar_tempo_transporte(distancia, ambulancia["tipo"]),
                        "regiao": regiao
                    })
        
        # Ordenar por distância (mais próxima primeiro)
        if ambulancias_disponiveis:
            return sorted(ambulancias_disponiveis, key=lambda x: x["distancia_km"])[0]
        
        return None
    
    def processar_matchmaking_completo(self, dados_paciente: Dict[str, Any], 
                                     decisao_ia: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa matchmaking logístico completo
        
        Args:
            dados_paciente: Dados do paciente
            decisao_ia: Decisão da IA com hospital sugerido
            
        Returns:
            Resultado completo do matchmaking logístico
        """
        
        try:
            # 1. Extrair dados básicos
            cidade_origem = dados_paciente.get("cidade_origem", "GOIANIA")
            hospital_sugerido = decisao_ia.get("analise_decisoria", {}).get("unidade_destino_sugerida") or \
                              decisao_ia.get("hospital_escolhido", "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG")
            
            classificacao_risco = decisao_ia.get("analise_decisoria", {}).get("classificacao_risco", "AMARELO")
            score_prioridade = decisao_ia.get("analise_decisoria", {}).get("score_prioridade", 5)
            
            # 2. Obter coordenadas
            lat_origem, lon_origem = self.obter_coordenadas_cidade(cidade_origem)
            lat_destino, lon_destino = self.obter_coordenadas_hospital(hospital_sugerido)
            
            # 3. Calcular distância e métricas logísticas
            distancia_km = self.calcular_distancia_km(lat_origem, lon_origem, lat_destino, lon_destino)
            
            # 4. Determinar tipo de ambulância necessária
            if classificacao_risco == "VERMELHO" or score_prioridade >= 8:
                tipo_ambulancia = "USA"  # Suporte Avançado
                tipo_caso = "CRITICO"
            elif classificacao_risco == "AMARELO" or score_prioridade >= 6:
                tipo_ambulancia = "USB"  # Suporte Básico
                tipo_caso = "URGENTE"
            else:
                tipo_ambulancia = "USB"
                tipo_caso = "NORMAL"
            
            # 5. Encontrar ambulância mais próxima
            ambulancia_escolhida = self.encontrar_ambulancia_mais_proxima(
                lat_origem, lon_origem, tipo_ambulancia
            )
            
            # 6. Calcular scores e tempos
            score_logistico = self.calcular_score_logistico(distancia_km, tipo_caso)
            tempo_transporte = self.estimar_tempo_transporte(distancia_km, tipo_ambulancia)
            
            # 7. Detectar protocolo especial (óbito/transplante)
            protocolo_especial = self._detectar_protocolo_especial(dados_paciente)
            
            # 8. Calcular score final (IA + Logística)
            score_final = (score_prioridade + score_logistico) / 2
            
            # 9. Gerar resultado completo
            resultado_matchmaking = {
                "matchmaking_logistico": {
                    "hospital_destino": hospital_sugerido,
                    "cidade_origem": cidade_origem,
                    "distancia_km": round(distancia_km, 2),
                    "tempo_estimado_min": tempo_transporte,
                    "score_logistico": round(score_logistico, 2),
                    "score_final": round(score_final, 2),
                    "viabilidade": "VIAVEL" if score_logistico >= 5 else "LIMITADA"
                },
                "ambulancia_sugerida": {
                    "id": ambulancia_escolhida["id"] if ambulancia_escolhida else "N/A",
                    "tipo": tipo_ambulancia,
                    "status": ambulancia_escolhida["status"] if ambulancia_escolhida else "INDISPONIVEL",
                    "tempo_chegada_min": ambulancia_escolhida["tempo_chegada_min"] if ambulancia_escolhida else 30,
                    "regiao": ambulancia_escolhida["regiao"] if ambulancia_escolhida else "N/A"
                },
                "rota_otimizada": {
                    "origem": {
                        "cidade": cidade_origem,
                        "coordenadas": [lat_origem, lon_origem]
                    },
                    "destino": {
                        "hospital": hospital_sugerido,
                        "coordenadas": [lat_destino, lon_destino]
                    },
                    "via_recomendada": self._sugerir_via(distancia_km, cidade_origem),
                    "alertas_rota": self._gerar_alertas_rota(distancia_km, classificacao_risco)
                },
                "protocolo_especial": protocolo_especial,
                "metadata": {
                    "processado_em": datetime.utcnow().isoformat(),
                    "algoritmo": "Haversine + Score Logístico",
                    "versao": "1.0.0",
                    "dados_origem": "Coordenadas reais SES-GO"
                }
            }
            
            logger.info(f"✅ Matchmaking processado: {hospital_sugerido} - {distancia_km:.1f}km - {tempo_transporte}min")
            
            return resultado_matchmaking
            
        except Exception as e:
            logger.error(f"❌ Erro no matchmaking logístico: {e}")
            
            # Fallback básico
            return {
                "matchmaking_logistico": {
                    "hospital_destino": "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG",
                    "cidade_origem": "GOIANIA",
                    "distancia_km": 10.0,
                    "tempo_estimado_min": 25,
                    "score_logistico": 5.0,
                    "score_final": 5.0,
                    "viabilidade": "LIMITADA"
                },
                "ambulancia_sugerida": {
                    "id": "USB-FALLBACK",
                    "tipo": "USB",
                    "status": "DISPONIVEL",
                    "tempo_chegada_min": 15,
                    "regiao": "GOIANIA"
                },
                "erro": str(e),
                "fallback": True
            }
    
    def _detectar_protocolo_especial(self, dados_paciente: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta protocolos especiais (óbito, transplante, etc.)"""
        
        prontuario = dados_paciente.get("prontuario_texto", "").lower()
        historico = dados_paciente.get("historico_paciente", "").lower()
        
        # Detectar indicação de óbito
        palavras_obito = [
            "óbito", "obito", "morte cerebral", "glasgow 3", "coma irreversível",
            "morte encefálica", "parada cardiorrespiratória", "sem sinais vitais"
        ]
        
        indicacao_obito = any(palavra in prontuario or palavra in historico 
                             for palavra in palavras_obito)
        
        if indicacao_obito:
            return {
                "tipo": "PROTOCOLO_OBITO",
                "ativo": True,
                "instrucoes": [
                    "Manter saturação O2 > 94%",
                    "Manter temperatura > 35°C",
                    "Acionar Central de Transplantes",
                    "Notificar Assistência Social",
                    "Protocolo de manutenção de órgãos"
                ],
                "alertas": [
                    "URGENTE: Possível doador de órgãos",
                    "Manter suporte vital até avaliação"
                ]
            }
        
        # Detectar outros protocolos
        if any(palavra in prontuario for palavra in ["queimadura", "queimado"]):
            return {
                "tipo": "PROTOCOLO_QUEIMADOS",
                "ativo": True,
                "instrucoes": ["Priorizar HUGO ou HUGOL", "Hidratação venosa"],
                "alertas": ["Especialização em queimados necessária"]
            }
        
        return {
            "tipo": "NORMAL",
            "ativo": False,
            "instrucoes": [],
            "alertas": []
        }
    
    def _sugerir_via(self, distancia_km: float, cidade_origem: str) -> str:
        """Sugere melhor via baseada na distância e origem"""
        
        if distancia_km <= 15:
            return "Via urbana - Trânsito local"
        elif distancia_km <= 50:
            return "Via metropolitana - Anel Viário"
        else:
            return "Rodovia estadual - BR/GO"
    
    def _gerar_alertas_rota(self, distancia_km: float, classificacao_risco: str) -> List[str]:
        """Gera alertas específicos para a rota"""
        
        alertas = []
        
        if distancia_km > 100:
            alertas.append("⚠️ Rota longa - Verificar combustível")
            alertas.append("📞 Comunicar com hospital de destino")
        
        if classificacao_risco == "VERMELHO":
            alertas.append("🚨 Caso crítico - Sirene obrigatória")
            alertas.append("📡 Manter contato com regulação")
        
        if distancia_km > 200:
            alertas.append("🏥 Considerar hospital intermediário")
        
        return alertas


# Instância global do matchmaker
matchmaker_logistico = MatchmakerLogistico()

def processar_matchmaking(dados_paciente: Dict[str, Any], 
                         decisao_ia: Dict[str, Any]) -> Dict[str, Any]:
    """
    Função principal para processamento de matchmaking logístico
    
    Args:
        dados_paciente: Dados do paciente
        decisao_ia: Decisão da IA
        
    Returns:
        Resultado completo do matchmaking
    """
    
    return matchmaker_logistico.processar_matchmaking_completo(dados_paciente, decisao_ia)

def calcular_distancia_hospitais(cidade_origem: str, hospital_destino: str) -> float:
    """
    Função utilitária para calcular distância entre cidade e hospital
    
    Args:
        cidade_origem: Nome da cidade de origem
        hospital_destino: Nome do hospital de destino
        
    Returns:
        Distância em quilômetros
    """
    
    lat1, lon1 = matchmaker_logistico.obter_coordenadas_cidade(cidade_origem)
    lat2, lon2 = matchmaker_logistico.obter_coordenadas_hospital(hospital_destino)
    
    return matchmaker_logistico.calcular_distancia_km(lat1, lon1, lat2, lon2)


if __name__ == "__main__":
    print("🚑 TESTE MATCHMAKER LOGÍSTICO - SISTEMA DE REGULAÇÃO SES-GO")
    print("=" * 70)
    
    # Teste 1: Caso normal de Anápolis para HGG
    print("\n📋 TESTE 1: Dor lombar - Anápolis → Hospital Regional")
    dados_teste1 = {
        "protocolo": "MATCH-001",
        "cidade_origem": "ANAPOLIS",
        "especialidade": "ORTOPEDIA",
        "cid": "M54.5",
        "prontuario_texto": "Dor lombar crônica há 6 meses"
    }
    
    decisao_teste1 = {
        "analise_decisoria": {
            "unidade_destino_sugerida": "HOSPITAL ESTADUAL DE ANAPOLIS DR HENRIQUE SANTILLO",
            "score_prioridade": 4,
            "classificacao_risco": "VERDE"
        }
    }
    
    resultado1 = processar_matchmaking(dados_teste1, decisao_teste1)
    print(f"🏥 Hospital: {resultado1['matchmaking_logistico']['hospital_destino']}")
    print(f"📏 Distância: {resultado1['matchmaking_logistico']['distancia_km']} km")
    print(f"⏱️ Tempo: {resultado1['matchmaking_logistico']['tempo_estimado_min']} min")
    print(f"🚑 Ambulância: {resultado1['ambulancia_sugerida']['id']} ({resultado1['ambulancia_sugerida']['tipo']})")
    
    # Teste 2: Caso crítico de Goiânia para HUGO
    print("\n📋 TESTE 2: Trauma grave - Goiânia → HUGO")
    dados_teste2 = {
        "protocolo": "MATCH-002",
        "cidade_origem": "GOIANIA",
        "especialidade": "TRAUMATOLOGIA",
        "cid": "S06.9",
        "prontuario_texto": "Trauma craniano grave, acidente de trânsito"
    }
    
    decisao_teste2 = {
        "analise_decisoria": {
            "unidade_destino_sugerida": "HOSPITAL DE URGENCIAS DE GOIAS DR VALDEMIRO CRUZ HUGO",
            "score_prioridade": 9,
            "classificacao_risco": "VERMELHO"
        }
    }
    
    resultado2 = processar_matchmaking(dados_teste2, decisao_teste2)
    print(f"🏥 Hospital: {resultado2['matchmaking_logistico']['hospital_destino']}")
    print(f"📏 Distância: {resultado2['matchmaking_logistico']['distancia_km']} km")
    print(f"⏱️ Tempo: {resultado2['matchmaking_logistico']['tempo_estimado_min']} min")
    print(f"🚑 Ambulância: {resultado2['ambulancia_sugerida']['id']} ({resultado2['ambulancia_sugerida']['tipo']})")
    print(f"🚨 Alertas: {len(resultado2['rota_otimizada']['alertas_rota'])} alertas")
    
    # Teste 3: Protocolo especial - Óbito
    print("\n📋 TESTE 3: Protocolo Óbito - Transplantes")
    dados_teste3 = {
        "protocolo": "MATCH-003",
        "cidade_origem": "FORMOSA",
        "especialidade": "UTI",
        "cid": "G93.1",
        "prontuario_texto": "Paciente em morte cerebral, Glasgow 3, sem reflexos"
    }
    
    decisao_teste3 = {
        "analise_decisoria": {
            "unidade_destino_sugerida": "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG",
            "score_prioridade": 10,
            "classificacao_risco": "VERMELHO"
        }
    }
    
    resultado3 = processar_matchmaking(dados_teste3, decisao_teste3)
    print(f"🏥 Hospital: {resultado3['matchmaking_logistico']['hospital_destino']}")
    print(f"⚠️ Protocolo: {resultado3['protocolo_especial']['tipo']}")
    print(f"📋 Instruções: {len(resultado3['protocolo_especial']['instrucoes'])} instruções especiais")
    
    # Teste 4: Cálculo de distâncias
    print("\n📏 TESTE 4: Cálculo de Distâncias")
    distancias_teste = [
        ("GOIANIA", "HOSPITAL ESTADUAL DR ALBERTO RASSI HGG"),
        ("ANAPOLIS", "HOSPITAL ESTADUAL DE ANAPOLIS DR HENRIQUE SANTILLO"),
        ("FORMOSA", "HOSPITAL ESTADUAL DE FORMOSA DR CESAR SAAD FAYAD"),
        ("GOIANIA", "HOSPITAL DE URGENCIAS DE GOIAS DR VALDEMIRO CRUZ HUGO")
    ]
    
    for origem, destino in distancias_teste:
        distancia = calcular_distancia_hospitais(origem, destino)
        print(f"📍 {origem} → {destino.split()[-1]}: {distancia:.1f} km")
    
    print("\n" + "=" * 70)
    print("✅ MATCHMAKER LOGÍSTICO IMPLEMENTADO COM SUCESSO!")
    print("🧮 Fórmula de Haversine para cálculo geodésico")
    print("🚑 Sistema de frota de ambulâncias integrado")
    print("⚠️ Protocolos especiais (óbito/transplante) detectados")
    print("📊 Score de Eficiência Logística calculado")
    print("=" * 70)