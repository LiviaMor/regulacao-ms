import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Platform } from 'react-native';

// Configuração da API baseada na plataforma
const API_BASE_URL = Platform.select({
  web: 'http://localhost:8000',
  default: 'http://10.0.2.2:8000' // Android Emulator
});

interface TransparenciaStats {
  total_solicitacoes: number;
  total_decisoes_ia: number;
  tempo_medio_regulacao: number;
  disponibilidade_sistema: string;
  ultima_atualizacao: string;
}

const TransparenciaWidget = () => {
  const [stats, setStats] = useState<TransparenciaStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchStats = async () => {
    try {
      setIsLoading(true);
      
      // Simular dados de transparência (em produção, viria da API de auditoria)
      const mockStats: TransparenciaStats = {
        total_solicitacoes: 2751,
        total_decisoes_ia: 1847,
        tempo_medio_regulacao: 3.2,
        disponibilidade_sistema: "99.8%",
        ultima_atualizacao: new Date().toISOString()
      };
      
      setStats(mockStats);
    } catch (error) {
      console.error('Erro ao buscar estatísticas:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    
    // Atualizar a cada 5 minutos
    const interval = setInterval(fetchStats, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (!stats) return null;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Transparência e Auditoria</Text>
        <Text style={styles.subtitle}>Dados Públicos em Tempo Real</Text>
      </View>

      <View style={styles.statsGrid}>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{stats.total_solicitacoes.toLocaleString()}</Text>
          <Text style={styles.statLabel}>Solicitações Processadas</Text>
        </View>

        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{stats.total_decisoes_ia.toLocaleString()}</Text>
          <Text style={styles.statLabel}>Decisões da IA</Text>
        </View>

        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{stats.tempo_medio_regulacao}h</Text>
          <Text style={styles.statLabel}>Tempo Médio</Text>
        </View>

        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{stats.disponibilidade_sistema}</Text>
          <Text style={styles.statLabel}>Disponibilidade</Text>
        </View>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          Todos os dados são auditáveis e rastreáveis
        </Text>
        <Text style={styles.footerText}>
          Conformidade com LGPD e transparência pública
        </Text>
        <Text style={styles.lastUpdate}>
          Última atualização: {new Date(stats.ultima_atualizacao).toLocaleTimeString('pt-BR')}
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#E8F5E8',
    margin: 15,
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#4CAF50',
  },
  header: {
    alignItems: 'center',
    marginBottom: 15,
  },
  title: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2E7D32',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 12,
    color: '#388E3C',
    textAlign: 'center',
    marginTop: 2,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  statCard: {
    width: '48%',
    backgroundColor: '#FFF',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#C8E6C9',
  },
  statNumber: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2E7D32',
  },
  statLabel: {
    fontSize: 11,
    color: '#4CAF50',
    textAlign: 'center',
    marginTop: 2,
  },
  footer: {
    borderTopWidth: 1,
    borderTopColor: '#C8E6C9',
    paddingTop: 10,
  },
  footerText: {
    fontSize: 11,
    color: '#388E3C',
    marginBottom: 3,
  },
  lastUpdate: {
    fontSize: 10,
    color: '#4CAF50',
    textAlign: 'center',
    marginTop: 5,
    fontStyle: 'italic',
  },
});

export default TransparenciaWidget;