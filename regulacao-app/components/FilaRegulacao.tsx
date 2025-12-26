import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  Alert,
  Platform,
  ActivityIndicator
} from 'react-native';
import CardDecisaoIA from './CardDecisaoIA';

// Configuração da API baseada na plataforma
const API_BASE_URL = Platform.select({
  web: 'http://localhost:8000',
  default: 'http://10.0.2.2:8000' // Android Emulator
});

interface PacienteRegulacao {
  protocolo: string;
  data_solicitacao: string;
  especialidade: string;
  cidade_origem: string;
  unidade_solicitante: string;
  score_prioridade: number;
  classificacao_risco: 'VERMELHO' | 'AMARELO' | 'VERDE';
  justificativa_tecnica: string;
}

interface FilaRegulacaoProps {
  userToken: string;
}

const FilaRegulacao: React.FC<FilaRegulacaoProps> = ({ userToken }) => {
  const [fila, setFila] = useState<PacienteRegulacao[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [selectedPaciente, setSelectedPaciente] = useState<string | null>(null);
  const [decisaoIA, setDecisaoIA] = useState<any>(null);

  const fetchFila = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/fila-regulacao`, {
        headers: {
          'Authorization': `Bearer ${userToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setFila(data);
      } else {
        throw new Error('Erro ao buscar fila');
      }
    } catch (error) {
      console.error('Erro ao buscar fila:', error);
      Alert.alert('Erro', 'Não foi possível carregar a fila de regulação');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchFila();
  };

  const processarPacienteComIA = async (paciente: PacienteRegulacao) => {
    try {
      setSelectedPaciente(paciente.protocolo);
      
      const dadosParaIA = {
        protocolo: paciente.protocolo,
        especialidade: paciente.especialidade,
        cid: "I21.9", // Exemplo - em produção viria do banco
        cid_desc: "Condição médica",
        prontuario_texto: `Paciente de ${paciente.cidade_origem} necessita ${paciente.especialidade}. ${paciente.justificativa_tecnica || 'Análise pendente.'}`,
        historico_paciente: "Histórico não disponível",
        prioridade_descricao: paciente.classificacao_risco || "Normal"
      };

      const response = await fetch(`${API_BASE_URL}/processar-regulacao`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dadosParaIA),
      });

      if (response.ok) {
        const resultado = await response.json();
        setDecisaoIA(resultado);
      } else {
        throw new Error('Erro no processamento IA');
      }
    } catch (error) {
      console.error('Erro no processamento IA:', error);
      Alert.alert('Erro', 'Falha no processamento com IA');
    } finally {
      setSelectedPaciente(null);
    }
  };

  useEffect(() => {
    fetchFila();
  }, []);

  const getRiskColor = (risco: string) => {
    switch (risco) {
      case 'VERMELHO': return '#D32F2F';
      case 'AMARELO': return '#F57C00';
      case 'VERDE': return '#388E3C';
      default: return '#666';
    }
  };

  const getRiskIcon = (risco: string) => {
    switch (risco) {
      case 'VERMELHO': return '🚨';
      case 'AMARELO': return '⚠️';
      case 'VERDE': return '✅';
      default: return '❓';
    }
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString('pt-BR');
    } catch {
      return dateString;
    }
  };

  const renderPaciente = ({ item }: { item: PacienteRegulacao }) => (
    <View style={styles.pacienteCard}>
      {/* Header com protocolo e risco */}
      <View style={styles.pacienteHeader}>
        <Text style={styles.protocolo}>📋 {item.protocolo}</Text>
        <View style={[
          styles.riskBadge, 
          { backgroundColor: getRiskColor(item.classificacao_risco) }
        ]}>
          <Text style={styles.riskText}>
            {getRiskIcon(item.classificacao_risco)} {item.classificacao_risco}
          </Text>
        </View>
      </View>

      {/* Informações do paciente */}
      <View style={styles.pacienteInfo}>
        <Text style={styles.infoLabel}>🏥 Especialidade:</Text>
        <Text style={styles.infoValue}>{item.especialidade}</Text>
        
        <Text style={styles.infoLabel}>📍 Origem:</Text>
        <Text style={styles.infoValue}>{item.cidade_origem}</Text>
        
        <Text style={styles.infoLabel}>🏢 Unidade Solicitante:</Text>
        <Text style={styles.infoValue} numberOfLines={2}>
          {item.unidade_solicitante}
        </Text>
        
        <Text style={styles.infoLabel}>⏰ Solicitação:</Text>
        <Text style={styles.infoValue}>{formatDate(item.data_solicitacao)}</Text>
        
        {item.score_prioridade && (
          <>
            <Text style={styles.infoLabel}>📊 Score de Prioridade:</Text>
            <Text style={[styles.infoValue, { fontWeight: 'bold' }]}>
              {item.score_prioridade}/10
            </Text>
          </>
        )}
        
        {item.justificativa_tecnica && (
          <>
            <Text style={styles.infoLabel}>📝 Justificativa:</Text>
            <Text style={styles.justificativa}>{item.justificativa_tecnica}</Text>
          </>
        )}
      </View>

      {/* Botão de ação */}
      <TouchableOpacity
        style={styles.actionButton}
        onPress={() => processarPacienteComIA(item)}
        disabled={selectedPaciente === item.protocolo}
      >
        {selectedPaciente === item.protocolo ? (
          <ActivityIndicator color="#FFF" />
        ) : (
          <Text style={styles.actionButtonText}>
            🤖 Processar com IA
          </Text>
        )}
      </TouchableOpacity>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#004A8D" />
        <Text style={styles.loadingText}>Carregando fila de regulação...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Fila de Regulação</Text>
        <Text style={styles.headerSubtitle}>
          {fila.length} paciente{fila.length !== 1 ? 's' : ''} aguardando
        </Text>
      </View>

      <FlatList
        data={fila}
        renderItem={renderPaciente}
        keyExtractor={(item) => item.protocolo}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        contentContainerStyle={styles.list}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>✅ Nenhum paciente na fila</Text>
            <Text style={styles.emptySubtext}>
              Todos os pacientes foram regulados com sucesso!
            </Text>
          </View>
        }
      />

      {/* Modal/Card da decisão IA */}
      {decisaoIA && (
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <CardDecisaoIA
              decisaoIA={decisaoIA}
              protocolo={decisaoIA.protocolo || 'N/A'}
              userToken={userToken}
              onTransferenciaAutorizada={() => {
                setDecisaoIA(null);
                fetchFila(); // Recarregar fila
              }}
            />
            <TouchableOpacity
              style={styles.closeButton}
              onPress={() => setDecisaoIA(null)}
            >
              <Text style={styles.closeButtonText}>❌ Fechar</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F7FA',
  },
  header: {
    padding: 20,
    backgroundColor: '#004A8D',
    borderBottomLeftRadius: 15,
    borderBottomRightRadius: 15,
  },
  headerTitle: {
    color: '#FFF',
    fontSize: 20,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  headerSubtitle: {
    color: '#E3F2FD',
    fontSize: 14,
    textAlign: 'center',
    marginTop: 4,
  },
  list: {
    padding: 15,
  },
  pacienteCard: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  pacienteHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  protocolo: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
  },
  riskBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    minWidth: 80,
    alignItems: 'center',
  },
  riskText: {
    color: '#FFF',
    fontSize: 12,
    fontWeight: 'bold',
  },
  pacienteInfo: {
    marginBottom: 15,
  },
  infoLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 8,
    marginBottom: 2,
  },
  infoValue: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  justificativa: {
    fontSize: 13,
    color: '#555',
    fontStyle: 'italic',
    backgroundColor: '#F8F9FA',
    padding: 8,
    borderRadius: 6,
    marginTop: 4,
  },
  actionButton: {
    backgroundColor: '#4CAF50',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  actionButtonText: {
    color: '#FFF',
    fontWeight: 'bold',
    fontSize: 16,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F5F7FA',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  emptyContainer: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#4CAF50',
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
  modalOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    margin: 20,
    maxHeight: '80%',
  },
  closeButton: {
    backgroundColor: '#FF5722',
    padding: 12,
    alignItems: 'center',
    borderBottomLeftRadius: 12,
    borderBottomRightRadius: 12,
  },
  closeButtonText: {
    color: '#FFF',
    fontWeight: 'bold',
  },
});

export default FilaRegulacao;