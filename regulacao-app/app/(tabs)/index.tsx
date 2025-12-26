import React, { useMemo, useEffect, useState } from 'react';
import { Platform, Alert } from 'react-native';
import DashboardPublico from '@/components/DashboardPublico';

// Configuração da API baseada na plataforma
const API_BASE_URL = Platform.select({
  web: 'http://localhost:8000',
  default: 'http://10.0.2.2:8000' // Android Emulator
});

// Dados de fallback (caso a API não esteja disponível)
const fallbackData = [
    [
        1,
        "202503677132",
        "11/11/2025 15:41:52",
        "EM_REGULACAO",
        "Enfermaria Adulto",
        "ENFERMARIA ADULTO",
        "008.***.***-39",
        "0303040203",
        "NEUROCIRURGIA",
        "2535165 / HOSPITAL MUNICIPAL DE MOZARLANDIA",
        "MOZARLANDIA",
        "COMPLEXO REGULADOR ESTADUAL CRE"
    ],
    [
        1,
        "202503703540",
        "13/11/2025 15:28:15",
        "EM_REGULACAO",
        "Enfermaria Adulto",
        "ENFERMARIA ADULTO",
        "012.***.***-38",
        "0303060263",
        "CIRURGIA VASCULAR",
        "2535270 / HOSPITAL MUNICIPAL DE SANTA TEREZINHA DE GOIAS",
        "SANTA TEREZINHA DE GOIAS",
        "COMPLEXO REGULADOR ESTADUAL CRE"
    ],
    [
        1,
        "202503727610",
        "15/11/2025 15:48:18",
        "EM_REGULACAO",
        "UTI Adulto",
        "UTI ADULTO",
        "034.***.***-05",
        "0406010684",
        "CARDIOLOGIA",
        "5584108 / HOSPITAL MUNICIPAL DE RUBIATABA",
        "RUBIATABA",
        "COMPLEXO REGULADOR ESTADUAL CRE"
    ]
];

export default function HomeScreen() {
  const [dadosLeitos, setDadosLeitos] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Processar dados de fallback
  const dadosLeitosFallback = useMemo(() => {
    const hospitalData = fallbackData.reduce((acc, current) => {
      const hospitalName = current[9]; // O nome do hospital está na 10ª coluna (índice 9)
      const cidade = current[10]; // Cidade está na 11ª coluna (índice 10)
      
      if (!acc[hospitalName]) {
        acc[hospitalName] = {
          unidade_executante_desc: hospitalName.split(' / ')[1] || hospitalName,
          cidade: cidade,
          pacientes_em_fila: 0,
        };
      }
      acc[hospitalName].pacientes_em_fila += 1;
      return acc;
    }, {} as Record<string, { unidade_executante_desc: string; cidade: string; pacientes_em_fila: number }>);

    // Converte o objeto em um array e ordena por número de pacientes
    return Object.values(hospitalData).sort((a, b) => b.pacientes_em_fila - a.pacientes_em_fila);
  }, []);

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`${API_BASE_URL}/dashboard/leitos`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        // Timeout de 10 segundos
        signal: AbortSignal.timeout(10000)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.unidades_pressao && data.unidades_pressao.length > 0) {
        setDadosLeitos(data.unidades_pressao);
      } else {
        // Se não há dados da API, usar fallback
        setDadosLeitos(dadosLeitosFallback);
      }
    } catch (error) {
      console.warn('API não disponível, usando dados de fallback:', error.message);
      setDadosLeitos(dadosLeitosFallback);
      
      // Mostrar alerta apenas em desenvolvimento
      if (__DEV__) {
        Alert.alert(
          'Modo Offline', 
          'Conectando ao servidor... Exibindo dados de demonstração.',
          [{ text: 'OK' }]
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  return <DashboardPublico dadosLeitos={dadosLeitos} />;
}