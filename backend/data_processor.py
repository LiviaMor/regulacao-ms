"""
Sistema de Processamento de Dados SES-GO
Inspirado em técnicas de ETL para melhorar o dashboard
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SESGoDataProcessor:
    """
    Processador de dados SES-GO com técnicas avançadas de ETL
    Inspirado em boas práticas de normalização e agregação de dados
    """
    
    def __init__(self, data_dir: str = "."):
        self.data_dir = Path(data_dir)
        self.data_files = {
            'em_regulacao': 'dados_em_regulacao.json',
            'admitidos': 'dados_admitidos.json', 
            'alta': 'dados_alta.json',
            'em_transito': 'dados_em_transito.json'
        }
        
        # Mapeamento de colunas (baseado na análise dos dados)
        self.column_mapping = {
            0: 'id',
            1: 'protocolo',
            2: 'data_solicitacao',
            3: 'status',
            4: 'tipo_leito',
            5: 'tipo_leito_desc',
            6: 'cpf_mascarado',
            7: 'codigo_procedimento',
            8: 'especialidade',
            9: 'unidade_solicitante_completa',
            10: 'cidade_origem',
            11: 'unidade_destino_completa',
            12: 'data_atualizacao',
            13: 'complexo_regulador'
        }

    def _load_json_data(self, filename: str) -> List[List]:
        """Carrega dados JSON com tratamento de erro robusto"""
        file_path = self.data_dir / filename
        
        if not file_path.exists():
            logger.warning(f"Arquivo não encontrado: {filename}")
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Carregados {len(data)} registros de {filename}")
                return data
        except Exception as e:
            logger.error(f"Erro ao carregar {filename}: {e}")
            return []

    def _normalize_hospital_name(self, hospital_full: str) -> str:
        """Normaliza nomes de hospitais removendo códigos"""
        if not hospital_full or hospital_full == "null":
            return "N/A"
        
        # Remove códigos numéricos do início (ex: "2535165 / HOSPITAL...")
        if " / " in hospital_full:
            return hospital_full.split(" / ", 1)[1].strip()
        return hospital_full.strip()

    def _parse_datetime(self, date_str: str) -> datetime:
        """Converte string de data para datetime com múltiplos formatos"""
        if not date_str or date_str == "null":
            return datetime.utcnow()
        
        formats = [
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        logger.warning(f"Formato de data não reconhecido: {date_str}")
        return datetime.utcnow()

    def _normalize_city_name(self, city: str) -> str:
        """Normaliza nomes de cidades"""
        if not city or city == "null":
            return "N/A"
        return city.strip().upper()

    def process_raw_data(self) -> Dict[str, pd.DataFrame]:
        """Processa todos os arquivos JSON e retorna DataFrames normalizados"""
        processed_data = {}
        
        for status_key, filename in self.data_files.items():
            raw_data = self._load_json_data(filename)
            
            if not raw_data:
                processed_data[status_key] = pd.DataFrame()
                continue
            
            # Converter para DataFrame
            df = pd.DataFrame(raw_data)
            
            # Renomear colunas baseado no mapeamento
            max_cols = min(len(df.columns), len(self.column_mapping))
            column_names = [self.column_mapping.get(i, f'col_{i}') for i in range(max_cols)]
            df.columns = column_names[:len(df.columns)]
            
            # Normalizar dados
            if 'unidade_solicitante_completa' in df.columns:
                df['unidade_solicitante'] = df['unidade_solicitante_completa'].apply(
                    self._normalize_hospital_name
                )
            
            if 'unidade_destino_completa' in df.columns:
                df['unidade_destino'] = df['unidade_destino_completa'].apply(
                    self._normalize_hospital_name
                )
            
            if 'cidade_origem' in df.columns:
                df['cidade_origem'] = df['cidade_origem'].apply(self._normalize_city_name)
            
            if 'data_solicitacao' in df.columns:
                df['data_solicitacao_parsed'] = df['data_solicitacao'].apply(
                    self._parse_datetime
                )
            
            # Adicionar metadados
            df['status_categoria'] = status_key.upper()
            df['data_processamento'] = datetime.utcnow()
            
            processed_data[status_key] = df
            logger.info(f"Processados {len(df)} registros para {status_key}")
        
        return processed_data

    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Gera dados agregados para o dashboard"""
        processed_data = self.process_raw_data()
        
        # Combinar todos os DataFrames
        all_data = pd.concat([df for df in processed_data.values() if not df.empty], 
                           ignore_index=True)
        
        if all_data.empty:
            logger.warning("Nenhum dado disponível para processamento")
            return self._get_fallback_data()
        
        # 1. Resumo por status
        status_summary = []
        for status_key in self.data_files.keys():
            df = processed_data.get(status_key, pd.DataFrame())
            count = len(df) if not df.empty else 0
            status_summary.append({
                "status": status_key.upper().replace('_', ' '),
                "count": count
            })
        
        # 2. Pressão por unidade (hospitais com mais pacientes em regulação)
        em_regulacao_df = processed_data.get('em_regulacao', pd.DataFrame())
        unidades_pressao = []
        
        if not em_regulacao_df.empty and 'unidade_solicitante' in em_regulacao_df.columns:
            pressao_por_unidade = em_regulacao_df.groupby([
                'unidade_solicitante', 'cidade_origem'
            ]).size().reset_index(name='pacientes_em_fila')
            
            # Ordenar por pressão (mais pacientes primeiro)
            pressao_por_unidade = pressao_por_unidade.sort_values(
                'pacientes_em_fila', ascending=False
            ).head(20)  # Top 20
            
            for _, row in pressao_por_unidade.iterrows():
                unidades_pressao.append({
                    "unidade_executante_desc": row['unidade_solicitante'],
                    "cidade": row['cidade_origem'],
                    "pacientes_em_fila": int(row['pacientes_em_fila'])
                })
        
        # 3. Análise por especialidade
        especialidades_demanda = []
        if not em_regulacao_df.empty and 'especialidade' in em_regulacao_df.columns:
            esp_counts = em_regulacao_df['especialidade'].value_counts().head(10)
            for especialidade, count in esp_counts.items():
                if especialidade and especialidade != "null":
                    especialidades_demanda.append({
                        "especialidade": especialidade,
                        "count": int(count)
                    })
        
        # 4. Métricas temporais
        metricas_tempo = self._calculate_time_metrics(all_data)
        
        return {
            "status_summary": status_summary,
            "unidades_pressao": unidades_pressao,
            "especialidades_demanda": especialidades_demanda,
            "metricas_tempo": metricas_tempo,
            "ultima_atualizacao": datetime.utcnow().isoformat(),
            "total_registros": len(all_data),
            "data_quality": self._assess_data_quality(all_data)
        }

    def _calculate_time_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcula métricas temporais dos dados"""
        if df.empty or 'data_solicitacao_parsed' not in df.columns:
            return {}
        
        now = datetime.utcnow()
        
        # Filtrar dados das últimas 24h, 7 dias, 30 dias
        df_24h = df[df['data_solicitacao_parsed'] >= now - timedelta(hours=24)]
        df_7d = df[df['data_solicitacao_parsed'] >= now - timedelta(days=7)]
        df_30d = df[df['data_solicitacao_parsed'] >= now - timedelta(days=30)]
        
        return {
            "solicitacoes_24h": len(df_24h),
            "solicitacoes_7d": len(df_7d),
            "solicitacoes_30d": len(df_30d),
            "tendencia": "crescente" if len(df_24h) > len(df_7d) / 7 else "estável"
        }

    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Avalia qualidade dos dados"""
        if df.empty:
            return {"score": 0, "issues": ["Nenhum dado disponível"]}
        
        total_records = len(df)
        issues = []
        
        # Verificar campos obrigatórios
        required_fields = ['protocolo', 'especialidade', 'unidade_solicitante']
        for field in required_fields:
            if field in df.columns:
                null_count = df[field].isnull().sum()
                null_percentage = (null_count / total_records) * 100
                if null_percentage > 10:
                    issues.append(f"{field}: {null_percentage:.1f}% valores nulos")
        
        # Score de qualidade (0-100)
        score = max(0, 100 - len(issues) * 20)
        
        return {
            "score": score,
            "issues": issues,
            "total_records": total_records
        }

    def _get_fallback_data(self) -> Dict[str, Any]:
        """Dados de fallback quando não há dados reais"""
        return {
            "status_summary": [
                {"status": "EM REGULACAO", "count": 0},
                {"status": "ADMITIDOS", "count": 0},
                {"status": "ALTA", "count": 0},
                {"status": "EM TRANSITO", "count": 0}
            ],
            "unidades_pressao": [],
            "especialidades_demanda": [],
            "metricas_tempo": {},
            "ultima_atualizacao": datetime.utcnow().isoformat(),
            "total_registros": 0,
            "data_quality": {"score": 0, "issues": ["Nenhum arquivo de dados encontrado"]}
        }

    def export_processed_data(self, output_dir: str = "processed_data"):
        """Exporta dados processados para arquivos CSV"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        processed_data = self.process_raw_data()
        
        for status_key, df in processed_data.items():
            if not df.empty:
                csv_path = output_path / f"{status_key}_processed.csv"
                df.to_csv(csv_path, index=False, encoding='utf-8')
                logger.info(f"Exportado: {csv_path}")
        
        # Exportar dados do dashboard
        dashboard_data = self.generate_dashboard_data()
        json_path = output_path / "dashboard_data.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, ensure_ascii=False, indent=2, default=str)
        logger.info(f"Dados do dashboard exportados: {json_path}")

# Função utilitária para uso direto
def process_sesgo_data(data_dir: str = ".") -> Dict[str, Any]:
    """Função utilitária para processar dados SES-GO"""
    processor = SESGoDataProcessor(data_dir)
    return processor.generate_dashboard_data()

if __name__ == "__main__":
    # Teste do processador
    processor = SESGoDataProcessor()
    dashboard_data = processor.generate_dashboard_data()
    
    print("=== DADOS DO DASHBOARD ===")
    print(f"Total de registros: {dashboard_data.get('total_registros', 0)}")
    print(f"Qualidade dos dados: {dashboard_data.get('data_quality', {}).get('score', 0)}/100")
    print(f"Unidades com pressão: {len(dashboard_data.get('unidades_pressao', []))}")
    
    # Exportar dados processados
    processor.export_processed_data()