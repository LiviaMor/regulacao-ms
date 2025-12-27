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

// Helper para alerts compatíveis com web
const showAlert = (title: string, message: string) => {
  if (Platform.OS === 'web') {
    window.alert(`${title}\n\n${message}`);
  } else {
    Alert.alert(title, message);
  }
};

const showConfirm = (title: string, message: string, onConfirm: () => void) => {
  if (Platform.OS === 'web') {
    if (window.confirm(`${title}\n\n${message}`)) {
      onConfirm();
    }
  } else {
    Alert.alert(title, message, [
      { text: 'Cancelar', style: 'cancel' },
      { text: 'Confirmar', onPress: onConfirm }
    ]);
  }
};

// Configuração da API baseada na plataforma
const API_BASE_URL = Platform.select({
  web: 'http://localhost:8000',
  default: 'http://10.0.2.2:8000' // Android Emulator
});

interface PacienteTransferencia {
  protocolo: string;
  data_autorizacao: string;
  especialidade: string;
  unidade_origem: string;
  unidade_destino: string;
  cidade_origem: string;
  tipo_transporte: 'USA' | 'USB' | 'AEROMÉDICO';
  status_ambulancia: 'PENDENTE' | 'SOLICITADA' | 'A_CAMINHO' | 'NO_LOCAL' | 'TRANSPORTANDO' | 'CONCLUIDA';
  status_paciente: string;
  classificacao_risco: 'VERMELHO' | 'AMARELO' | 'VERDE';
  observacoes?: string;
  data_solicitacao_ambulancia?: string;
}

interface AreaTransferenciaProps {
  userToken: string;
}

const AreaTransferencia: React.FC<AreaTransferenciaProps> = ({ userToken }) => {
  const [pacientes, setPacientes] = useState<PacienteTransferencia[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [processando, setProcessando] = useState<string | null>(null);

  const fetchPacientesTransferencia = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/pacientes-transferencia`, {
        headers: {
          'Authorization': `Bearer ${userToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setPacientes(data);
      } else {
        throw new Error('Erro ao buscar pacientes');
      }
    } catch (error) {
      console.error('Erro ao buscar pacientes em transferência:', error);
      showAlert('Erro', 'Não foi possível carregar os pacientes em transferência');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchPacientesTransferencia();
  };

  const solicitarAmbulancia = async (protocolo: string, tipoTransporte: string) => {
    try {
      setProcessando(protocolo);
      
      const response = await fetch(`${API_BASE_URL}/solicitar-ambulancia`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${userToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          protocolo,
          tipo_transporte: tipoTransporte,
          observacoes: `Ambulância ${tipoTransporte} solicitada via sistema`
        })
      });

      if (response.ok) {
        const data = await response.json();
        showAlert('Sucesso', data.message);
        fetchPacientesTransferencia(); // Recarregar lista
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Erro ao solicitar ambulância');
      }
    } catch (error) {
      console.error('Erro ao solicitar ambulância:', error);
      showAlert('Erro', error instanceof Error ? error.message : 'Não foi possível solicitar ambulância');
    } finally {
      setProcessando(null);
    }
  };

  const atualizarStatusAmbulancia = async (protocolo: string, novoStatus: string) => {
    try {
      setProcessando(protocolo);
      
      const response = await fetch(`${API_BASE_URL}/atualizar-status-ambulancia`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${userToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          protocolo,
          novo_status: novoStatus
        })
      });

      if (response.ok) {
        const data = await response.json();
        showAlert('Sucesso', data.message);
        fetchPacientesTransferencia(); // Recarregar lista
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Erro ao atualizar status');
      }
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
      showAlert('Erro', error instanceof Error ? error.message : 'Não foi possível atualizar status');
    } finally {
      setProcessando(null);
    }
  };

  const handleSolicitarAmbulancia = (paciente: PacienteTransferencia) => {
    // Mostrar opções de tipo de transporte
    const mensagem = `Selecione o tipo de transporte para ${paciente.protocolo}:\n\nUSA - Unidade de Suporte Avançado\nUSB - Unidade de Suporte Básico\nAEROMÉDICO - Helicóptero`;
    
    if (Platform.OS === 'web') {
      const tipo = window.prompt(mensagem, 'USA');
      if (tipo && ['USA', 'USB', 'AEROMÉDICO'].includes(tipo.toUpperCase())) {
        solicitarAmbulancia(paciente.protocolo, tipo.toUpperCase());
      }
    } else {
      Alert.alert(
        'Tipo de Transporte',
        mensagem,
        [
          { text: 'USA', onPress: () => solicitarAmbulancia(paciente.protocolo, 'USA') },
          { text: 'USB', onPress: () => solicitarAmbulancia(paciente.protocolo, 'USB') },
          { text: 'AEROMÉDICO', onPress: () => solicitarAmbulancia(paciente.protocolo, 'AEROMÉDICO') },
          { text: 'Cancelar', style: 'cancel' }
        ]
      );
    }
  };

  const handleAtualizarStatus = (paciente: PacienteTransferencia) => {
    const statusOptions = ['A_CAMINHO', 'NO_LOCAL', 'TRANSPORTANDO', 'CONCLUIDA'];
    const statusLabels = {
      'A_CAMINHO': 'A Caminho',
      'NO_LOCAL': 'No Local',
      'TRANSPORTANDO': 'Transportando',
      'CONCLUIDA': 'Concluída'
    };
    
    if (Platform.OS === 'web') {
      const opcoes = statusOptions.map((s, i) => `${i + 1}. ${statusLabels[s as keyof typeof statusLabels]}`).join('\n');
      const escolha = window.prompt(`Atualizar status da ambulância:\n\n${opcoes}\n\nDigite o número:`);
      
      if (escolha) {
        const index = parseInt(escolha) - 1;
        if (index >= 0 && index < statusOptions.length) {
          atualizarStatusAmbulancia(paciente.protocolo, statusOptions[index]);
        }
      }
    } else {
      Alert.alert(
        'Atualizar Status',
        'Selecione o novo status:',
        statusOptions.map(status => ({
          text: statusLabels[status as keyof typeof statusLabels],
          onPress: () => atualizarStatusAmbulancia(paciente.protocolo, status)
        })).concat([{ text: 'Cancelar', style: 'cancel' }])
      );
    }
  };

  useEffect(() => {
    fetchPacientesTransferencia();
  }, []);

  const getRiskColor = (risco: string) => {
    switch (risco) {
      case 'VERMELHO': return '#D32F2F';
      case 'AMARELO': return '#F57C00';
      case 'VERDE': return '#388E3C';
      default: return '#666';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PENDENTE': return '#9E9E9E';
      case 'SOLICITADA': return '#FF9800';
      case 'A_CAMINHO': return '#2196F3';
      case 'NO_LOCAL': return '#9C27B0';
      case 'TRANSPORTANDO': return '#4CAF50';
      case 'CONCLUIDA': return '#1B5E20';
      default: return '#666';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'PENDENTE': return 'PENDENTE';
      case 'SOLICITADA': return 'SOLICITADA';
      case 'A_CAMINHO': return 'A CAMINHO';
      case 'NO_LOCAL': return 'NO LOCAL';
      case 'TRANSPORTANDO': return 'TRANSPORTANDO';
      case 'CONCLUIDA': return 'CONCLUÍDA';
      default: return status;
    }
  };

  const getTransportIcon = (tipo: string) => {
    switch (tipo) {
      case 'USA': return 'USA'; // Unidade de Suporte Avançado
      case 'USB': return 'USB'; // Unidade de Suporte Básico
      case 'AEROMÉDICO': return 'AEROMÉDICO'; // Helicóptero
      default: return tipo;
    }
  };

  const formatTime = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleTimeString('pt-BR', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    } catch {
      return 'N/A';
    }
  };

  const getTempoDecorrido = (dataAutorizacao: string) => {
    try {
      const agora = new Date();
      const autorizacao = new Date(dataAutorizacao);
      const diffMs = agora.getTime() - autorizacao.getTime();
      const diffMin = Math.floor(diffMs / (1000 * 60));
      
      if (diffMin < 60) {
        return `${diffMin}min`;
      } else {
        const horas = Math.floor(diffMin / 60);
        const minutos = diffMin % 60;
        return `${horas}h${minutos}min`;
      }
    } catch {
      return 'N/A';
    }
  };

  const renderPaciente = ({ item }: { item: PacienteTransferencia }) => {
    const isProcessando = processando === item.protocolo;
    
    return (
      <View style={styles.pacienteCard}>
        {/* Header com protocolo e risco */}
        <View style={styles.pacienteHeader}>
          <Text style={styles.protocolo}>{item.protocolo}</Text>
          <View style={[
            styles.riskBadge, 
            { backgroundColor: getRiskColor(item.classificacao_risco) }
          ]}>
            <Text style={styles.riskText}>{item.classificacao_risco}</Text>
          </View>
        </View>

        {/* Status da ambulância */}
        <View style={[
          styles.statusContainer,
          { backgroundColor: getStatusColor(item.status_ambulancia) }
        ]}>
          <Text style={styles.statusText}>
            {getStatusIcon(item.status_ambulancia)}
          </Text>
          <Text style={styles.tempoDecorrido}>
            {getTempoDecorrido(item.data_autorizacao)}
          </Text>
        </View>

        {/* Informações do transporte */}
        <View style={styles.transporteInfo}>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Origem:</Text>
            <Text style={styles.infoValue} numberOfLines={2}>
              {item.unidade_origem}
            </Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Destino:</Text>
            <Text style={styles.infoValue} numberOfLines={2}>
              {item.unidade_destino}
            </Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Transporte:</Text>
            <Text style={styles.infoValue}>
              {getTransportIcon(item.tipo_transporte)}
            </Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Especialidade:</Text>
            <Text style={styles.infoValue}>{item.especialidade}</Text>
          </View>
          
          {item.data_solicitacao_ambulancia && (
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Solicitada em:</Text>
              <Text style={styles.infoValue}>
                {formatTime(item.data_solicitacao_ambulancia)}
              </Text>
            </View>
          )}
        </View>

        {/* Botões de ação */}
        <View style={styles.actionButtons}>
          {item.status_ambulancia === 'PENDENTE' && (
            <TouchableOpacity
              style={[styles.actionButton, { backgroundColor: '#FF9800' }]}
              onPress={() => handleSolicitarAmbulancia(item)}
              disabled={isProcessando}
            >
              {isProcessando ? (
                <ActivityIndicator color="#FFF" size="small" />
              ) : (
                <Text style={styles.actionButtonText}>🚑 Solicitar Ambulância</Text>
              )}
            </TouchableOpacity>
          )}
          
          {item.status_ambulancia !== 'PENDENTE' && item.status_ambulancia !== 'CONCLUIDA' && (
            <TouchableOpacity
              style={[styles.actionButton, { backgroundColor: '#2196F3' }]}
              onPress={() => handleAtualizarStatus(item)}
              disabled={isProcessando}
            >
              {isProcessando ? (
                <ActivityIndicator color="#FFF" size="small" />
              ) : (
                <Text style={styles.actionButtonText}>Atualizar Status</Text>
              )}
            </TouchableOpacity>
          )}
          
          {item.status_ambulancia === 'CONCLUIDA' && (
            <View style={[styles.actionButton, { backgroundColor: '#1B5E20', opacity: 0.7 }]}>
              <Text style={styles.actionButtonText}>✓ Transferência Concluída</Text>
            </View>
          )}
        </View>
      </View>
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#004A8D" />
        <Text style={styles.loadingText}>Carregando transferências...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Área de Transferência</Text>
        <Text style={styles.headerSubtitle}>
          {pacientes.length} paciente{pacientes.length !== 1 ? 's' : ''} aguardando ambulância
        </Text>
      </View>

      <FlatList
        data={pacientes}
        renderItem={renderPaciente}
        keyExtractor={(item) => item.protocolo}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        contentContainerStyle={styles.list}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>Nenhuma transferência pendente</Text>
            <Text style={styles.emptySubtext}>
              Todas as ambulâncias foram despachadas!
            </Text>
          </View>
        }
      />
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
  statusContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 12,
    borderRadius: 8,
    marginBottom: 15,
  },
  statusText: {
    color: '#FFF',
    fontSize: 14,
    fontWeight: 'bold',
  },
  tempoDecorrido: {
    color: '#FFF',
    fontSize: 12,
    opacity: 0.9,
  },
  transporteInfo: {
    marginBottom: 15,
  },
  infoRow: {
    flexDirection: 'row',
    marginBottom: 8,
    alignItems: 'flex-start',
  },
  infoLabel: {
    fontSize: 12,
    color: '#666',
    width: 80,
    marginRight: 8,
  },
  infoValue: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
    flex: 1,
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'center',
  },
  actionButton: {
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 8,
    alignItems: 'center',
    minWidth: 150,
  },
  actionButtonText: {
    color: '#FFF',
    fontWeight: 'bold',
    fontSize: 14,
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
});

export default AreaTransferencia;