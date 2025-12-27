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
  tipo_transporte: 'USA' | 'USB' | 'AEROMÉDICO';
  status_ambulancia: 'SOLICITADA' | 'A_CAMINHO' | 'NO_LOCAL' | 'TRANSPORTANDO';
  previsao_chegada?: string;
  observacoes?: string;
  regulador_responsavel: string;
  classificacao_risco: 'VERMELHO' | 'AMARELO' | 'VERDE';
}

const AreaTransferencia = () => {
  const [pacientes, setPacientes] = useState<PacienteTransferencia[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);

  // Dados simulados para demonstração
  const dadosSimulados: PacienteTransferencia[] = [
    {
      protocolo: 'REG-2024-001',
      data_autorizacao: new Date(Date.now() - 30 * 60 * 1000).toISOString(), // 30 min atrás
      especialidade: 'CARDIOLOGIA',
      unidade_origem: 'HOSPITAL MUNICIPAL DE GOIÂNIA',
      unidade_destino: 'HOSPITAL ESTADUAL DR ALBERTO RASSI HGG',
      tipo_transporte: 'USA',
      status_ambulancia: 'A_CAMINHO',
      previsao_chegada: new Date(Date.now() + 15 * 60 * 1000).toISOString(), // 15 min
      regulador_responsavel: 'Dr. João Silva',
      classificacao_risco: 'VERMELHO'
    },
    {
      protocolo: 'REG-2024-002',
      data_autorizacao: new Date(Date.now() - 45 * 60 * 1000).toISOString(), // 45 min atrás
      especialidade: 'TRAUMATOLOGIA',
      unidade_origem: 'UPA JARDIM AMÉRICA',
      unidade_destino: 'HOSPITAL DE URGÊNCIAS DE GOIÁS DR VALDEMIRO CRUZ HUGO',
      tipo_transporte: 'USA',
      status_ambulancia: 'TRANSPORTANDO',
      previsao_chegada: new Date(Date.now() + 25 * 60 * 1000).toISOString(), // 25 min
      regulador_responsavel: 'Dra. Maria Santos',
      classificacao_risco: 'VERMELHO'
    },
    {
      protocolo: 'REG-2024-003',
      data_autorizacao: new Date(Date.now() - 20 * 60 * 1000).toISOString(), // 20 min atrás
      especialidade: 'ORTOPEDIA',
      unidade_origem: 'HOSPITAL MUNICIPAL DE APARECIDA',
      unidade_destino: 'HOSPITAL ESTADUAL DE ANÁPOLIS DR HENRIQUE SANTILLO',
      tipo_transporte: 'USB',
      status_ambulancia: 'SOLICITADA',
      regulador_responsavel: 'Dr. Carlos Oliveira',
      classificacao_risco: 'AMARELO'
    },
    {
      protocolo: 'REG-2024-004',
      data_autorizacao: new Date(Date.now() - 10 * 60 * 1000).toISOString(), // 10 min atrás
      especialidade: 'NEUROLOGIA',
      unidade_origem: 'HOSPITAL REGIONAL DE FORMOSA',
      unidade_destino: 'HOSPITAL ESTADUAL DR ALBERTO RASSI HGG',
      tipo_transporte: 'USA',
      status_ambulancia: 'NO_LOCAL',
      previsao_chegada: new Date(Date.now() + 40 * 60 * 1000).toISOString(), // 40 min
      regulador_responsavel: 'Dra. Ana Costa',
      classificacao_risco: 'VERMELHO'
    }
  ];

  const fetchPacientesTransferencia = async () => {
    try {
      // Em produção, seria uma chamada real para a API
      // const response = await fetch(`${API_BASE_URL}/pacientes-transferencia`);
      
      // Simulando delay de rede
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Usar dados simulados
      setPacientes(dadosSimulados);
      
    } catch (error) {
      console.error('Erro ao buscar pacientes em transferência:', error);
      Alert.alert('Erro', 'Não foi possível carregar os pacientes em transferência');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchPacientesTransferencia();
  };

  const atualizarStatusAmbulancia = async (protocolo: string, novoStatus: string) => {
    try {
      // Em produção, seria uma chamada para a API
      Alert.alert(
        'Status Atualizado',
        `Status da ambulância para ${protocolo} atualizado para: ${novoStatus}`
      );
      
      // Atualizar localmente
      setPacientes(prev => 
        prev.map(p => 
          p.protocolo === protocolo 
            ? { ...p, status_ambulancia: novoStatus as any }
            : p
        )
      );
    } catch (error) {
      Alert.alert('Erro', 'Não foi possível atualizar o status');
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
      case 'SOLICITADA': return '#FF9800';
      case 'A_CAMINHO': return '#2196F3';
      case 'NO_LOCAL': return '#9C27B0';
      case 'TRANSPORTANDO': return '#4CAF50';
      default: return '#666';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'SOLICITADA': return 'SOLICITADA';
      case 'A_CAMINHO': return 'A CAMINHO';
      case 'NO_LOCAL': return 'NO LOCAL';
      case 'TRANSPORTANDO': return 'TRANSPORTANDO';
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

  const renderPaciente = ({ item }: { item: PacienteTransferencia }) => (
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
        
        {item.previsao_chegada && (
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Previsão:</Text>
            <Text style={[styles.infoValue, { fontWeight: 'bold', color: '#2196F3' }]}>
              {formatTime(item.previsao_chegada)}
            </Text>
          </View>
        )}
        
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Regulador:</Text>
          <Text style={styles.infoValue}>{item.regulador_responsavel}</Text>
        </View>
      </View>

      {/* Botões de ação */}
      <View style={styles.actionButtons}>
        {item.status_ambulancia === 'SOLICITADA' && (
          <TouchableOpacity
            style={[styles.actionButton, { backgroundColor: '#2196F3' }]}
            onPress={() => atualizarStatusAmbulancia(item.protocolo, 'A_CAMINHO')}
          >
            <Text style={styles.actionButtonText}>A Caminho</Text>
          </TouchableOpacity>
        )}
        
        {item.status_ambulancia === 'A_CAMINHO' && (
          <TouchableOpacity
            style={[styles.actionButton, { backgroundColor: '#9C27B0' }]}
            onPress={() => atualizarStatusAmbulancia(item.protocolo, 'NO_LOCAL')}
          >
            <Text style={styles.actionButtonText}>No Local</Text>
          </TouchableOpacity>
        )}
        
        {item.status_ambulancia === 'NO_LOCAL' && (
          <TouchableOpacity
            style={[styles.actionButton, { backgroundColor: '#4CAF50' }]}
            onPress={() => atualizarStatusAmbulancia(item.protocolo, 'TRANSPORTANDO')}
          >
            <Text style={styles.actionButtonText}>Transportando</Text>
          </TouchableOpacity>
        )}
        
        {item.status_ambulancia === 'TRANSPORTANDO' && (
          <View style={[styles.actionButton, { backgroundColor: '#4CAF50', opacity: 0.7 }]}>
            <Text style={styles.actionButtonText}>Em Transporte</Text>
          </View>
        )}
      </View>
    </View>
  );

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