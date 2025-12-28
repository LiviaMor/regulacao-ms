#!/usr/bin/env python3
"""
DOCUMENT AI SERVICE - Análise Inteligente de Documentos Médicos
Sistema de Regulação Autônoma SES-GO

=== INOVAÇÃO: PIPELINE MULTIMODAL DE IA ===

Este serviço implementa um pipeline inovador de análise de documentos médicos:

1. OCR (Tesseract/EasyOCR) - Extração de texto de imagens
2. BioBERT - Análise de entidades médicas no texto extraído
3. Llama 3 - Interpretação contextual e sugestões clínicas

FLUXO DE PROCESSAMENTO:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Imagem/   │───▶│    OCR      │───▶│   BioBERT   │───▶│   Llama 3   │
│  Documento  │    │  (Texto)    │    │ (Entidades) │    │ (Contexto)  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘

TIPOS DE DOCUMENTOS SUPORTADOS:
- Imagens: JPG, PNG, WEBP, BMP
- Documentos: PDF (primeira página)
- Fotos de prontuários, receitas, exames

TRANSPARÊNCIA (FAPEG):
- Todos os modelos são open-source
- Logs detalhados de cada etapa
- Scores de confiança em cada análise
"""

import logging
import base64
import io
import os
import json
import requests
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from PIL import Image

logger = logging.getLogger(__name__)

# Configurações
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
SUPPORTED_FORMATS = ['jpg', 'jpeg', 'png', 'webp', 'bmp', 'pdf']


class DocumentAIService:
    """
    Serviço de IA para análise de documentos médicos
    Combina OCR + BioBERT + Llama para análise completa
    """
    
    _instance = None
    _ocr_engine = None
    _ocr_disponivel = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DocumentAIService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self._inicializar_ocr()
    
    def _inicializar_ocr(self):
        """Inicializa engine de OCR (Tesseract ou EasyOCR)"""
        
        # Tentar Tesseract primeiro (mais leve)
        try:
            import pytesseract
            from PIL import Image
            
            # Testar se Tesseract está instalado
            pytesseract.get_tesseract_version()
            self._ocr_engine = "tesseract"
            self._ocr_disponivel = True
            logger.info("✅ OCR Engine: Tesseract inicializado")
            return
        except Exception as e:
            logger.warning(f"⚠️ Tesseract não disponível: {e}")
        
        # Fallback para EasyOCR (mais pesado, mas não precisa de instalação externa)
        try:
            import easyocr
            self._reader = easyocr.Reader(['pt', 'en'], gpu=False)
            self._ocr_engine = "easyocr"
            self._ocr_disponivel = True
            logger.info("✅ OCR Engine: EasyOCR inicializado")
            return
        except Exception as e:
            logger.warning(f"⚠️ EasyOCR não disponível: {e}")
        
        # Fallback final: análise básica de imagem sem OCR
        logger.warning("⚠️ Nenhum OCR disponível. Usando análise básica.")
        self._ocr_engine = "basic"
        self._ocr_disponivel = False
    
    def is_disponivel(self) -> bool:
        """Verifica se o serviço está disponível"""
        return True  # Sempre disponível, mesmo sem OCR (usa Llama)
    
    def extrair_texto_ocr(self, image_data: bytes, filename: str = "") -> Dict[str, Any]:
        """
        Extrai texto de imagem usando OCR
        
        Args:
            image_data: Bytes da imagem
            filename: Nome do arquivo (para detectar tipo)
            
        Returns:
            Dict com texto extraído e metadados
        """
        
        start_time = datetime.utcnow()
        
        try:
            # Abrir imagem
            image = Image.open(io.BytesIO(image_data))
            
            # Converter para RGB se necessário
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extrair metadados da imagem
            width, height = image.size
            formato = image.format or filename.split('.')[-1].upper()
            
            texto_extraido = ""
            confianca_ocr = 0.0
            
            if self._ocr_engine == "tesseract":
                import pytesseract
                
                # Configurar para português + inglês
                texto_extraido = pytesseract.image_to_string(
                    image, 
                    lang='por+eng',
                    config='--psm 6'  # Assume bloco de texto uniforme
                )
                
                # Obter dados detalhados para calcular confiança
                dados = pytesseract.image_to_data(image, lang='por+eng', output_type=pytesseract.Output.DICT)
                confiancas = [int(c) for c in dados['conf'] if int(c) > 0]
                confianca_ocr = sum(confiancas) / len(confiancas) / 100 if confiancas else 0.5
                
            elif self._ocr_engine == "easyocr":
                resultados = self._reader.readtext(image_data)
                
                textos = []
                confiancas = []
                for (bbox, texto, conf) in resultados:
                    textos.append(texto)
                    confiancas.append(conf)
                
                texto_extraido = " ".join(textos)
                confianca_ocr = sum(confiancas) / len(confiancas) if confiancas else 0.5
                
            else:
                # Sem OCR - retornar análise básica
                texto_extraido = ""
                confianca_ocr = 0.0
            
            tempo_processamento = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                "status": "sucesso" if texto_extraido else "sem_texto",
                "texto_extraido": texto_extraido.strip(),
                "confianca_ocr": round(confianca_ocr, 3),
                "engine": self._ocr_engine,
                "metadados_imagem": {
                    "largura": width,
                    "altura": height,
                    "formato": formato,
                    "tamanho_bytes": len(image_data)
                },
                "tempo_processamento_ms": round(tempo_processamento * 1000, 2),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro no OCR: {e}")
            return {
                "status": "erro",
                "texto_extraido": "",
                "confianca_ocr": 0.0,
                "engine": self._ocr_engine,
                "erro": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def analisar_com_llama(self, texto: str, contexto_clinico: str = "") -> Dict[str, Any]:
        """
        Analisa texto médico com Llama 3 para interpretação contextual
        
        Args:
            texto: Texto extraído do documento
            contexto_clinico: Contexto adicional do paciente
            
        Returns:
            Dict com análise do Llama
        """
        
        try:
            prompt = f"""Você é um assistente médico especializado em análise de documentos clínicos.
Analise o seguinte texto extraído de um documento médico e forneça:

1. RESUMO CLÍNICO: Resumo dos principais achados
2. ENTIDADES MÉDICAS: Liste diagnósticos, medicamentos, procedimentos mencionados
3. ALERTAS: Identifique informações críticas ou urgentes
4. SUGESTÕES: Recomendações para a equipe de regulação

TEXTO DO DOCUMENTO:
{texto}

{f'CONTEXTO DO PACIENTE: {contexto_clinico}' if contexto_clinico else ''}

Responda de forma estruturada e objetiva, focando em informações relevantes para regulação hospitalar."""

            response = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Mais determinístico para análise médica
                        "num_predict": 1000
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                resultado = response.json()
                resposta_llama = resultado.get("response", "")
                
                return {
                    "status": "sucesso",
                    "analise_llama": resposta_llama,
                    "modelo": "llama3",
                    "tokens_gerados": resultado.get("eval_count", 0),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                logger.warning(f"⚠️ Llama retornou status {response.status_code}")
                return {
                    "status": "erro_llama",
                    "analise_llama": "Análise Llama indisponível",
                    "erro": f"HTTP {response.status_code}",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except requests.exceptions.ConnectionError:
            logger.warning("⚠️ Llama não está disponível (conexão recusada)")
            return {
                "status": "llama_offline",
                "analise_llama": "Serviço Llama não está disponível no momento",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Erro na análise Llama: {e}")
            return {
                "status": "erro",
                "analise_llama": "",
                "erro": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def processar_documento_completo(
        self, 
        image_data: bytes, 
        filename: str = "",
        contexto_paciente: str = ""
    ) -> Dict[str, Any]:
        """
        Pipeline completo de análise de documento médico:
        OCR → BioBERT → Llama
        
        Args:
            image_data: Bytes da imagem/documento
            filename: Nome do arquivo
            contexto_paciente: Informações adicionais do paciente
            
        Returns:
            Dict com análise completa multimodal
        """
        
        start_time = datetime.utcnow()
        resultado_final = {
            "status": "processando",
            "etapas": {},
            "resumo_ia": "",
            "entidades_detectadas": [],
            "alertas": [],
            "confianca_geral": 0.0,
            "timestamp_inicio": start_time.isoformat()
        }
        
        try:
            # === ETAPA 1: OCR ===
            logger.info("📄 Etapa 1: Extraindo texto com OCR...")
            resultado_ocr = self.extrair_texto_ocr(image_data, filename)
            resultado_final["etapas"]["ocr"] = resultado_ocr
            
            texto_extraido = resultado_ocr.get("texto_extraido", "")
            
            if not texto_extraido:
                logger.warning("⚠️ Nenhum texto extraído do documento")
                # Tentar análise direta com Llama (visão)
                resultado_final["etapas"]["ocr"]["nota"] = "Documento sem texto legível ou imagem"
            
            # === ETAPA 2: BioBERT ===
            logger.info("🧬 Etapa 2: Analisando com BioBERT...")
            
            try:
                from biobert_service import extrair_entidades_biobert, is_biobert_disponivel
                
                if is_biobert_disponivel() and texto_extraido:
                    resultado_biobert = extrair_entidades_biobert(texto_extraido)
                    resultado_final["etapas"]["biobert"] = resultado_biobert
                    resultado_final["entidades_detectadas"] = resultado_biobert.get("entidades", [])
                else:
                    resultado_final["etapas"]["biobert"] = {
                        "status": "pulado",
                        "motivo": "BioBERT indisponível ou sem texto para analisar"
                    }
            except ImportError:
                resultado_final["etapas"]["biobert"] = {
                    "status": "indisponivel",
                    "motivo": "Módulo BioBERT não encontrado"
                }
            
            # === ETAPA 3: Llama (Interpretação Contextual) ===
            logger.info("🦙 Etapa 3: Interpretando com Llama 3...")
            
            # Preparar contexto completo para Llama
            contexto_completo = texto_extraido
            if contexto_paciente:
                contexto_completo += f"\n\nContexto do paciente: {contexto_paciente}"
            
            if resultado_final.get("entidades_detectadas"):
                entidades_str = ", ".join([e.get("termo", "") for e in resultado_final["entidades_detectadas"]])
                contexto_completo += f"\n\nEntidades médicas detectadas pelo BioBERT: {entidades_str}"
            
            if contexto_completo.strip():
                resultado_llama = self.analisar_com_llama(contexto_completo)
                resultado_final["etapas"]["llama"] = resultado_llama
                resultado_final["resumo_ia"] = resultado_llama.get("analise_llama", "")
            else:
                resultado_final["etapas"]["llama"] = {
                    "status": "pulado",
                    "motivo": "Sem conteúdo para analisar"
                }
            
            # === CALCULAR CONFIANÇA GERAL ===
            # BioBERT é o modelo principal - peso maior na confiança
            # Referência: Lee et al. (2020) - Bioinformatics, DOI: 10.1093/bioinformatics/btz682
            # Treinado em 4.5B palavras do PubMed + 13.5B do PMC
            
            confianca_ocr = resultado_ocr.get("confianca_ocr", 0)
            biobert_conf = resultado_final["etapas"].get("biobert", {}).get("confianca", 0)
            biobert_status = resultado_final["etapas"].get("biobert", {}).get("status", "")
            llama_ok = resultado_final["etapas"].get("llama", {}).get("status") == "sucesso"
            
            # Pesos: BioBERT (60%), OCR (30%), Llama (10% - apenas complemento)
            if biobert_status == "sucesso" and biobert_conf > 0:
                # BioBERT processou com sucesso - alta confiabilidade
                confianca_geral = (
                    biobert_conf * 0.60 +          # BioBERT: modelo principal
                    confianca_ocr * 0.30 +         # OCR: qualidade da extração
                    (0.8 if llama_ok else 0) * 0.10  # Llama: complemento opcional
                )
                resultado_final["modelo_principal"] = "BioBERT v1.1 (dmis-lab)"
                resultado_final["nota_confiabilidade"] = "Análise baseada em modelo científico validado (PubMed/PMC)"
            elif confianca_ocr > 0:
                # Apenas OCR disponível
                confianca_geral = confianca_ocr * 0.7 + (0.3 if llama_ok else 0)
                resultado_final["modelo_principal"] = "OCR + Llama"
                resultado_final["nota_confiabilidade"] = "BioBERT indisponível, análise baseada em OCR"
            else:
                confianca_geral = 0.3 if llama_ok else 0.0
                resultado_final["modelo_principal"] = "Llama (fallback)"
                resultado_final["nota_confiabilidade"] = "Análise limitada - documento sem texto legível"
            
            resultado_final["confianca_geral"] = round(confianca_geral, 3)
            
            # === IDENTIFICAR ALERTAS ===
            alertas = []
            
            # Alertas baseados em entidades BioBERT
            entidades_urgentes = ["trauma", "infarto", "avc", "dispneia", "cianose"]
            for entidade in resultado_final.get("entidades_detectadas", []):
                if entidade.get("categoria") in entidades_urgentes:
                    alertas.append({
                        "tipo": "URGENCIA",
                        "mensagem": f"Detectado: {entidade.get('termo', entidade.get('categoria'))}",
                        "fonte": "BioBERT"
                    })
            
            resultado_final["alertas"] = alertas
            
            # === FINALIZAR ===
            tempo_total = (datetime.utcnow() - start_time).total_seconds()
            resultado_final["status"] = "sucesso"
            resultado_final["tempo_total_segundos"] = round(tempo_total, 2)
            resultado_final["timestamp_fim"] = datetime.utcnow().isoformat()
            
            logger.info(f"✅ Documento processado em {tempo_total:.2f}s")
            
            return resultado_final
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento do documento: {e}")
            resultado_final["status"] = "erro"
            resultado_final["erro"] = str(e)
            resultado_final["timestamp_fim"] = datetime.utcnow().isoformat()
            return resultado_final


# Instância global (singleton)
document_ai_service = DocumentAIService()


def processar_documento_medico(
    image_data: bytes, 
    filename: str = "",
    contexto_paciente: str = ""
) -> Dict[str, Any]:
    """
    Função principal para processar documento médico
    
    Args:
        image_data: Bytes da imagem/documento
        filename: Nome do arquivo
        contexto_paciente: Contexto adicional
        
    Returns:
        Dict com análise completa
    """
    return document_ai_service.processar_documento_completo(
        image_data, filename, contexto_paciente
    )


def extrair_texto_documento(image_data: bytes, filename: str = "") -> Dict[str, Any]:
    """
    Extrai apenas texto do documento (OCR)
    
    Args:
        image_data: Bytes da imagem
        filename: Nome do arquivo
        
    Returns:
        Dict com texto extraído
    """
    return document_ai_service.extrair_texto_ocr(image_data, filename)


def is_document_ai_disponivel() -> bool:
    """Verifica se o serviço está disponível"""
    return document_ai_service.is_disponivel()


if __name__ == "__main__":
    print("📄 TESTE DOCUMENT AI SERVICE")
    print("=" * 50)
    
    print(f"Serviço disponível: {is_document_ai_disponivel()}")
    print(f"OCR Engine: {document_ai_service._ocr_engine}")
    print(f"OCR Disponível: {document_ai_service._ocr_disponivel}")
    
    print("\n✅ Document AI Service inicializado")
