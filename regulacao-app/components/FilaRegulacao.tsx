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

// Helper para alerts compatíveis com web
const showAlert = (title: string, message: string) => {
  if (Platform.OS === 'web') {
    window.alert(`${title}\n\n${message}`);
  } else {
    Alert.alert(title, message);
  }
};

// Configuração da API baseada na plataforma
const API_BASE_URL = Platform.select({
  web: 'http://localhost:8000',  // Sistema Unificado
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
      // Buscar pacientes que foram inseridos pelo hospital e aguardam regulação
      // APENAS status AGUARDANDO_REGULACAO (não inclui NEGADO_PENDENTE)
      const response = await fetch(`${API_BASE_URL}/pacientes-hospital-aguardando`, {
        headers: {
          'Authorization': `Bearer ${userToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        // Filtrar apenas pacientes AGUARDANDO_REGULACAO
        // Pacientes NEGADO_PENDENTE devem aparecer na Área do Hospital para edição
        const pacientesAguardando = data.filter((p: any) => p.status === 'AGUARDANDO_REGULACAO');
        
        // Converter para o formato esperado pela interface
        const filaFormatada = pacientesAguardando.map((p: any) => ({
          protocolo: p.protocolo,
          data_solicitacao: p.data_solicitacao,
          especialidade: p.especialidade,
          cidade_origem: p.cidade_origem || 'N/A',
          unidade_solicitante: p.unidade_solicitante || 'Hospital Solicitante',
          score_prioridade: p.score_prioridade,
          classificacao_risco: p.classificacao_risco,
          justificativa_tecnica: p.justificativa_tecnica,
          cid: p.cid,
          cid_desc: p.cid_desc,
          unidade_destino_sugerida: p.unidade_destino
        }));
        setFila(filaFormatada);
      } else {
        throw new Error('Erro ao buscar fila');
      }
    } catch (error) {
      console.error('Erro ao buscar fila:', error);
      showAlert('Erro', 'Não foi possível carregar a fila de regulação');
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
      
      console.log('Processando paciente com IA:', paciente.protocolo);
      
      // Preparar dados do paciente para a IA
      const dadosPaciente = {
        protocolo: paciente.protocolo,
        especialidade: paciente.especialidade,
        cid: (paciente as any).cid || 'M79.9', // CID padrão se não tiver
        cid_desc: (paciente as any).cid_desc || 'Condição médica',
        prontuario_texto: (paciente as any).prontuario_texto || `Paciente com ${paciente.especialidade.toLowerCase()}, aguardando regulação`,
        historico_paciente: (paciente as any).historico_paciente || 'Histórico não informado',
        prioridade_descricao: paciente.classificacao_risco === 'VERMELHO' ? 'Urgente' : 'Normal',
        cidade_origem: paciente.cidade_origem || 'GOIANIA'
      };

      console.log('📤 Enviando dados para IA:', dadosPaciente);

      // Chamar a IA real do MS-Regulacao
      const response = await fetch(`${API_BASE_URL}/processar-regulacao`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${userToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dadosPaciente)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const decisaoIA = await response.json();
      console.log('Resposta da IA recebida:', decisaoIA);

      // Adicionar protocolo à decisão para o CardDecisaoIA
      decisaoIA.protocolo = paciente.protocolo;
      
      setDecisaoIA(decisaoIA);
      
    } catch (error) {
      console.error('Erro no processamento IA:', error);
      showAlert(
        'Erro na IA', 
        `Falha no processamento: ${error instanceof Error ? error.message : 'Erro desconhecido'}\n\nVerifique se o MS-Regulacao está rodando.`
      );
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
      case 'VERMELHO': return 'CRITICO';
      case 'AMARELO': return 'MODERADO';
      case 'VERDE': return 'BAIXO';
      default: return 'N/A';
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
        <Text style={styles.protocolo}>{item.protocolo}</Text>
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
        <Text style={styles.infoLabel}>Especialidade:</Text>
        <Text style={styles.infoValue}>{item.especialidade}</Text>
        
        <Text style={styles.infoLabel}>Origem:</Text>
        <Text style={styles.infoValue}>{item.cidade_origem}</Text>
        
        <Text style={styles.infoLabel}>Unidade Solicitante:</Text>
        <Text style={styles.infoValue} numberOfLines={2}>
          {item.unidade_solicitante}
        </Text>
        
        <Text style={styles.infoLabel}>Solicitação:</Text>
        <Text style={styles.infoValue}>{formatDate(item.data_solicitacao)}</Text>
        
        {item.score_prioridade && (
          <>
            <Text style={styles.infoLabel}>Score de Prioridade:</Text>
            <Text style={[styles.infoValue, { fontWeight: 'bold' }]}>
              {item.score_prioridade}/10
            </Text>
          </>
        )}
        
        {item.justificativa_tecnica && (
          <>
            <Text style={styles.infoLabel}>Justificativa:</Text>
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
            Processar com IA
          </Text>
        )}
      </TouchableOpacity>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#004A8D" />
        <Text style={styles.loadingText}>Carregando fila de regulacao...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Fila de Regulacao</Text>
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
            <View style={styles.emptyIcon}>
              <Text style={styles.emptyIconText}>OK</Text>
            </View>
            <Text style={styles.emptyText}>Nenhum paciente na fila</Text>
            <Text style={styles.emptySubtext}>
              Todos os pacientes foram regulados com sucesso
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
              <Text style={styles.closeButtonText}>Fechar</Text>
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
  emptyIcon: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#4CAF50',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  emptyIconText: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: 'bold',
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
    padding: 10,
  },
  modalContent: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    width: '100%',
    maxWidth: 600,
    maxHeight: '90%',
    overflow: 'hidden',
  },
  closeButton: {
    backgroundColor: '#FF5722',
    padding: 14,
    alignItems: 'center',
  },
  closeButtonText: {
    color: '#FFF',
    fontWeight: 'bold',
    fontSize: 14,
  },
});

export default FilaRegulacao;