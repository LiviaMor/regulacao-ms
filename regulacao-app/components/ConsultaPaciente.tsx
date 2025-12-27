import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
  Platform
} from 'react-native';

// Configuração da API baseada na plataforma
const API_BASE_URL = Platform.select({
  web: 'http://localhost:8000',
  default: 'http://10.0.2.2:8000' // Android Emulator
});

interface PacienteInfo {
  protocolo: string;
  nome_anonimizado?: string;
  cpf_anonimizado?: string;
  telefone_anonimizado?: string;
  data_solicitacao: string;
  status: string;
  especialidade: string;
  unidade_solicitante: string;
  cidade_origem: string;
  unidade_destino?: string;
  classificacao_risco?: string;
  data_atualizacao?: string;
  posicao_fila?: number;
  total_fila?: number;
  score_prioridade?: number;
  previsao_atendimento?: string;
  historico_movimentacoes?: Array<{
    data: string;
    status_anterior: string;
    status_novo: string;
    responsavel?: string;
    observacoes?: string;
  }>;
  // Informações de transferência e ambulância
  status_ambulancia?: string;
  tipo_transporte?: string;
  data_solicitacao_ambulancia?: string;
}

const ConsultaPaciente = () => {
  const [busca, setBusca] = useState('');
  const [paciente, setPaciente] = useState<PacienteInfo | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  const buscarPaciente = async () => {
    if (!busca.trim()) {
      if (Platform.OS === 'web') {
        window.alert('Informe o protocolo para buscar');
      } else {
        Alert.alert('Erro', 'Informe o protocolo para buscar');
      }
      return;
    }

    try {
      setIsLoading(true);
      setErro(null);
      setPaciente(null);

      // Usar endpoint público com anonimização
      const response = await fetch(`${API_BASE_URL}/consulta-publica/paciente/${busca.trim()}`);

      if (response.ok) {
        const data = await response.json();
        setPaciente(data);
      } else if (response.status === 404) {
        setErro('Paciente não encontrado');
      } else {
        throw new Error('Erro na consulta');
      }
    } catch (error) {
      console.error('Erro na busca:', error);
      setErro('Erro ao consultar. Verifique sua conexão e tente novamente.');
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'EM_REGULACAO': return '#FF9800';
      case 'INTERNACAO_AUTORIZADA': return '#2196F3';
      case 'INTERNADA': return '#4CAF50';
      case 'COM_ALTA': return '#9C27B0';
      default: return '#666';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'EM_REGULACAO': return 'Em Regulação';
      case 'INTERNACAO_AUTORIZADA': return 'Internação Autorizada';
      case 'INTERNADA': return 'Internado(a)';
      case 'COM_ALTA': return 'Com Alta';
      default: return status;
    }
  };

  const getRiscoColor = (risco?: string) => {
    switch (risco) {
      case 'VERMELHO': return '#F44336';
      case 'AMARELO': return '#FF9800';
      case 'VERDE': return '#4CAF50';
      default: return '#666';
    }
  };

  const formatarData = (dataStr: string) => {
    try {
      const data = new Date(dataStr);
      return data.toLocaleString('pt-BR');
    } catch {
      return dataStr;
    }
  };

  const renderPacienteInfo = () => {
    if (!paciente) return null;

    return (
      <ScrollView style={styles.resultadoContainer}>
        {/* Header com Status */}
        <View style={[styles.statusHeader, { backgroundColor: getStatusColor(paciente.status) }]}>
          <Text style={styles.statusHeaderText}>
            {getStatusText(paciente.status)}
          </Text>
          {paciente.posicao_fila && (
            <Text style={styles.posicaoText}>
              Posição na Fila: {paciente.posicao_fila} de {paciente.total_fila}
            </Text>
          )}
        </View>

        {/* Informações Básicas */}
        <View style={styles.infoCard}>
          <Text style={styles.cardTitle}>Informações da Solicitação</Text>
          
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Protocolo:</Text>
            <Text style={styles.infoValue}>{paciente.protocolo}</Text>
          </View>

          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Data da Solicitação:</Text>
            <Text style={styles.infoValue}>{formatarData(paciente.data_solicitacao)}</Text>
          </View>

          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Especialidade:</Text>
            <Text style={styles.infoValue}>{paciente.especialidade}</Text>
          </View>

          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Hospital Solicitante:</Text>
            <Text style={styles.infoValue}>{paciente.unidade_solicitante}</Text>
          </View>

          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Cidade:</Text>
            <Text style={styles.infoValue}>{paciente.cidade_origem}</Text>
          </View>

          {paciente.unidade_destino && (
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Destino:</Text>
              <Text style={styles.infoValue}>{paciente.unidade_destino}</Text>
            </View>
          )}
          
          {/* Status de Ambulância */}
          {paciente.status_ambulancia && (
            <>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Status Ambulância:</Text>
                <Text style={[styles.infoValue, { color: '#FF9800', fontWeight: 'bold' }]}>
                  {paciente.status_ambulancia.replace(/_/g, ' ')}
                </Text>
              </View>
              
              {paciente.tipo_transporte && (
                <View style={styles.infoRow}>
                  <Text style={styles.infoLabel}>Tipo de Transporte:</Text>
                  <Text style={styles.infoValue}>{paciente.tipo_transporte}</Text>
                </View>
              )}
              
              {paciente.data_solicitacao_ambulancia && (
                <View style={styles.infoRow}>
                  <Text style={styles.infoLabel}>Ambulância Solicitada:</Text>
                  <Text style={styles.infoValue}>{formatarData(paciente.data_solicitacao_ambulancia)}</Text>
                </View>
              )}
            </>
          )}
        </View>

        {/* Análise de Prioridade */}
        {(paciente.score_prioridade || paciente.classificacao_risco) && (
          <View style={styles.infoCard}>
            <Text style={styles.cardTitle}>Análise de Prioridade</Text>
            
            {paciente.score_prioridade && (
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Score de Prioridade:</Text>
                <Text style={[styles.infoValue, styles.scoreText]}>
                  {paciente.score_prioridade}/10
                </Text>
              </View>
            )}

            {paciente.classificacao_risco && (
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Classificação de Risco:</Text>
                <Text style={[
                  styles.infoValue, 
                  { color: getRiscoColor(paciente.classificacao_risco) }
                ]}>
                  {paciente.classificacao_risco}
                </Text>
              </View>
            )}

            {paciente.previsao_atendimento && (
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Previsão de Atendimento:</Text>
                <Text style={styles.infoValue}>{paciente.previsao_atendimento}</Text>
              </View>
            )}
          </View>
        )}

        {/* Histórico de Movimentações */}
        <View style={styles.infoCard}>
          <Text style={styles.cardTitle}>Histórico de Movimentações</Text>
          
          {paciente.historico_movimentacoes && paciente.historico_movimentacoes.length > 0 ? (
            paciente.historico_movimentacoes.map((mov, index) => (
              <View key={index} style={styles.historicoItem}>
                <View style={styles.historicoHeader}>
                  <Text style={styles.historicoData}>
                    {formatarData(mov.data)}
                  </Text>
                  {mov.responsavel && (
                    <Text style={styles.historicoResponsavel}>
                      {mov.responsavel}
                    </Text>
                  )}
                </View>
                
                <View style={styles.historicoStatus}>
                  <Text style={styles.statusAnterior}>
                    {getStatusText(mov.status_anterior)}
                  </Text>
                  <Text style={styles.seta}> → </Text>
                  <Text style={[
                    styles.statusNovo,
                    { color: getStatusColor(mov.status_novo) }
                  ]}>
                    {getStatusText(mov.status_novo)}
                  </Text>
                </View>

                {mov.observacoes && (
                  <Text style={styles.historicoObs}>
                    {mov.observacoes}
                  </Text>
                )}
              </View>
            ))
          ) : (
            <Text style={styles.semHistorico}>
              Nenhuma movimentação registrada ainda.
            </Text>
          )}
        </View>

        {/* Informações de Transparência */}
        <View style={styles.transparenciaCard}>
          <Text style={styles.transparenciaTitle}>Transparência e Auditoria</Text>
          <Text style={styles.transparenciaText}>
            • Todos os dados são auditáveis e rastreáveis
          </Text>
          <Text style={styles.transparenciaText}>
            • Histórico completo de movimentações preservado
          </Text>
          <Text style={styles.transparenciaText}>
            • Decisões da IA registradas com justificativas
          </Text>
          <Text style={styles.transparenciaText}>
            • Dados atualizados em tempo real
          </Text>
          <Text style={styles.transparenciaFooter}>
            Sistema SES-GO - Regulação Transparente
          </Text>
        </View>
      </ScrollView>
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Consulta de Paciente</Text>
        <Text style={styles.headerSubtitle}>Transparência Total na Regulação</Text>
      </View>

      <View style={styles.buscaContainer}>
        {/* Campo de Busca Unificado */}
        <TextInput
          style={styles.inputBusca}
          placeholder="Digite o protocolo (ex: REG-2025-001) ou CPF"
          value={busca}
          onChangeText={setBusca}
          autoCapitalize="characters"
        />

        {/* Botão de Busca */}
        <TouchableOpacity
          style={styles.botaoBusca}
          onPress={buscarPaciente}
          disabled={isLoading}
        >
          {isLoading ? (
            <ActivityIndicator color="#FFF" />
          ) : (
            <Text style={styles.botaoBuscaText}>Consultar</Text>
          )}
        </TouchableOpacity>

        {/* Erro */}
        {erro && (
          <View style={styles.erroContainer}>
            <Text style={styles.erroText}>{erro}</Text>
          </View>
        )}
      </View>

      {/* Resultado */}
      {renderPacienteInfo()}
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
  buscaContainer: {
    padding: 20,
  },
  inputBusca: {
    backgroundColor: '#FFF',
    borderRadius: 8,
    padding: 15,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#E0E0E0',
    marginBottom: 15,
  },
  botaoBusca: {
    backgroundColor: '#4CAF50',
    paddingVertical: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  botaoBuscaText: {
    color: '#FFF',
    fontWeight: 'bold',
    fontSize: 16,
  },
  erroContainer: {
    backgroundColor: '#FFEBEE',
    padding: 12,
    borderRadius: 8,
    marginTop: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#F44336',
  },
  erroText: {
    color: '#C62828',
    fontSize: 14,
  },
  resultadoContainer: {
    flex: 1,
    padding: 20,
    paddingTop: 0,
  },
  statusHeader: {
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 15,
  },
  statusHeaderText: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
  posicaoText: {
    color: '#FFF',
    fontSize: 14,
    marginTop: 5,
    opacity: 0.9,
  },
  infoCard: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 15,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  infoLabel: {
    fontSize: 14,
    color: '#666',
    flex: 1,
  },
  infoValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    flex: 2,
    textAlign: 'right',
  },
  scoreText: {
    color: '#FF9800',
    fontWeight: 'bold',
  },
  historicoItem: {
    backgroundColor: '#F8F9FA',
    padding: 12,
    borderRadius: 8,
    marginBottom: 10,
    borderLeftWidth: 3,
    borderLeftColor: '#004A8D',
  },
  historicoHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 5,
  },
  historicoData: {
    fontSize: 12,
    color: '#666',
    fontWeight: '600',
  },
  historicoResponsavel: {
    fontSize: 12,
    color: '#004A8D',
    fontStyle: 'italic',
  },
  historicoStatus: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 5,
  },
  statusAnterior: {
    fontSize: 13,
    color: '#666',
  },
  seta: {
    fontSize: 13,
    color: '#999',
    marginHorizontal: 5,
  },
  statusNovo: {
    fontSize: 13,
    fontWeight: '600',
  },
  historicoObs: {
    fontSize: 12,
    color: '#555',
    fontStyle: 'italic',
    marginTop: 5,
  },
  semHistorico: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    fontStyle: 'italic',
  },
  transparenciaCard: {
    backgroundColor: '#E8F5E8',
    borderRadius: 12,
    padding: 16,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#4CAF50',
  },
  transparenciaTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2E7D32',
    marginBottom: 10,
  },
  transparenciaText: {
    fontSize: 13,
    color: '#388E3C',
    marginBottom: 5,
  },
  transparenciaFooter: {
    fontSize: 12,
    color: '#4CAF50',
    textAlign: 'center',
    marginTop: 10,
    fontWeight: '600',
  },
});

export default ConsultaPaciente;