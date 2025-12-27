import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface StatusProcessamentoProps {
  biobert_usado?: boolean;
  biobert_disponivel?: boolean;
  matchmaker_usado?: boolean;
  tempo_processamento?: number;
  pipeline_rag?: boolean;
}

const StatusProcessamento: React.FC<StatusProcessamentoProps> = ({
  biobert_usado = false,
  biobert_disponivel = false,
  matchmaker_usado = false,
  tempo_processamento = 0,
  pipeline_rag = false
}) => {
  const getStatusIcon = (usado: boolean, disponivel: boolean = true) => {
    if (!disponivel) return '🔴';
    return usado ? '✅' : '❌';
  };

  const getStatusText = (usado: boolean, disponivel: boolean = true) => {
    if (!disponivel) return 'Indisponível';
    return usado ? 'Usado' : 'Não usado';
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🔧 Status do Processamento</Text>
      
      <View style={styles.statusRow}>
        <Text style={styles.statusLabel}>⏱️ Tempo:</Text>
        <Text style={styles.statusValue}>
          {tempo_processamento > 0 ? `${tempo_processamento.toFixed(2)}s` : 'N/A'}
        </Text>
      </View>
      
      <View style={styles.statusRow}>
        <Text style={styles.statusLabel}>🧬 BioBERT:</Text>
        <Text style={[
          styles.statusValue,
          { color: biobert_usado ? '#4CAF50' : '#FF5722' }
        ]}>
          {getStatusIcon(biobert_usado, biobert_disponivel)} {getStatusText(biobert_usado, biobert_disponivel)}
        </Text>
      </View>
      
      <View style={styles.statusRow}>
        <Text style={styles.statusLabel}>🚑 Matchmaker:</Text>
        <Text style={[
          styles.statusValue,
          { color: matchmaker_usado ? '#4CAF50' : '#FF5722' }
        ]}>
          {getStatusIcon(matchmaker_usado)} {getStatusText(matchmaker_usado)}
        </Text>
      </View>
      
      <View style={styles.statusRow}>
        <Text style={styles.statusLabel}>🤖 Pipeline RAG:</Text>
        <Text style={[
          styles.statusValue,
          { color: pipeline_rag ? '#4CAF50' : '#FF5722' }
        ]}>
          {getStatusIcon(pipeline_rag)} {getStatusText(pipeline_rag)}
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#F5F5F5',
    padding: 12,
    borderRadius: 8,
    marginVertical: 8,
    borderWidth: 1,
    borderColor: '#E0E0E0'
  },
  title: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#666',
    marginBottom: 8
  },
  statusRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4
  },
  statusLabel: {
    fontSize: 12,
    color: '#666',
    flex: 1
  },
  statusValue: {
    fontSize: 12,
    fontWeight: '600',
    flex: 1,
    textAlign: 'right'
  }
});

export default StatusProcessamento;