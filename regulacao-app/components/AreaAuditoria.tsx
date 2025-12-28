/**
 * ÁREA DE AUDITORIA - PAIC-REGULA
 * 
 * Componente para gestão de pacientes ADMITIDOS aguardando alta.
 * Conforme DIAGRAMA_FLUXO_COMPLETO.md:
 * 
 * Fluxo: ADMITIDO → (registra alta) → ALTA
 * 
 * Funcionalidades:
 * - Lista pacientes ADMITIDOS (chegaram ao destino)
 * - Permite registrar alta hospitalar
 * - Exibe tempo de internação
 */

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
import { Colors } from '../constants/theme';

// Helper para alerts compatíveis com web
const showAlert = (title: string, message: string) => {
  if (Platform.OS === 'web') {
    window.alert(`${title}\n\n${message}`);
  } else {
    Alert.alert(title, message);
  }
};

// Configuração da API
const API_BASE_URL = Platform.select({
  web: 'http://localhost:8000',
  default: 'http://10.0.2.2:8000'
});

interface PacienteAuditoria {
  protocolo: string;
  especialidade: string;
  unidade_origem: string;
  unidade_destino: string;
  classificacao_risco: 'VERMELHO' | 'AMARELO' | 'VERDE';
  data_solicitacao: string;
  data_internacao: string;
  tempo_total_horas: number;
  status: string;
  data_alta: string | null;
}

interface AreaAuditoriaProps {
  userToken: string;
}

const AreaAuditoria: React.FC<AreaAuditoriaProps> = ({ userToken }) => {
  const [pacientes, setPacientes] = useState<PacienteAuditoria[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [processando, setProcessando] = useState<string | null>(null);

  const fetchPacientesAuditoria = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/pacientes-auditoria`, {
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
      console.error('Erro ao buscar pacientes em auditoria:', error);
      showAlert('Erro', 'Não foi possível carregar os pacientes em auditoria');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchPacientesAuditoria();
  };

  const registrarAlta = async (protocolo: string) => {
    try {
      setProcessando(protocolo);
      
      // Solicitar data/hora da alta
      const dataAltaStr = Platform.OS === 'web' 
        ? window.prompt(
            `Registrar Alta Hospitalar\n\nProtocolo: ${protocolo}\n\nInforme a data/hora da alta (formato: AAAA-MM-DD HH:MM):`,
            new Date().toISOString().slice(0, 16).replace('T', ' ')
          )
        : new Date().toISOString();
      
      if (!dataAltaStr) {
        setProcessando(null);
        return;
      }
      
      // Converter para ISO format
      const dataAlta = dataAltaStr.replace(' ', 'T') + ':00';
      
      const response = await fetch(`${API_BASE_URL}/registrar-alta`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${userToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          protocolo,
          data_alta: dataAlta,
          observacoes_alta: 'Alta registrada via sistema'
        })
      });

      if (response.ok) {
        const data = await response.json();
        showAlert('Sucesso', `Alta registrada!\n\nProtocolo: ${protocolo}\nTempo total: ${data.tempo_total_horas}h`);
        fetchPacientesAuditoria(); // Recarregar lista
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Erro ao registrar alta');
      }
    } catch (error) {
      console.error('Erro ao registrar alta:', error);
      showAlert('Erro', error instanceof Error ? error.message : 'Não foi possível registrar alta');
    } finally {
      setProcessando(null);
    }
  };

  useEffect(() => {
    fetchPacientesAuditoria();
  }, []);

  const getRiskColor = (risco: string) => {
    switch (risco) {
      case 'VERMELHO': return '#D32F2F';
      case 'AMARELO': return '#F57C00';
      case 'VERDE': return '#388E3C';
      default: return '#666';
    }
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString('pt-BR');
    } catch {
      return dateString || 'N/A';
    }
  };

  const renderPaciente = ({ item }: { item: PacienteAuditoria }) => {
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

        {/* Status ADMITIDO */}
        <View style={styles.statusContainer}>
          <Text style={styles.statusText}>🏥 ADMITIDO - Aguardando Alta</Text>
          <Text style={styles.tempoInternacao}>
            {item.tempo_total_horas ? `${item.tempo_total_horas}h internado` : 'N/A'}
          </Text>
        </View>

        {/* Informações do paciente */}
        <View style={styles.pacienteInfo}>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Especialidade:</Text>
            <Text style={styles.infoValue}>{item.especialidade}</Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Hospital Origem:</Text>
            <Text style={styles.infoValue} numberOfLines={2}>
              {item.unidade_origem}
            </Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Hospital Destino:</Text>
            <Text style={styles.infoValue} numberOfLines={2}>
              {item.unidade_destino}
            </Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Data Solicitação:</Text>
            <Text style={styles.infoValue}>{formatDate(item.data_solicitacao)}</Text>
          </View>
          
          {item.data_internacao && (
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Data Internação:</Text>
              <Text style={styles.infoValue}>{formatDate(item.data_internacao)}</Text>
            </View>
          )}
        </View>

        {/* Botão de registrar alta */}
        <TouchableOpacity
          style={styles.altaButton}
          onPress={() => registrarAlta(item.protocolo)}
          disabled={isProcessando}
        >
          {isProcessando ? (
            <ActivityIndicator color="#FFF" size="small" />
          ) : (
            <Text style={styles.altaButtonText}>📋 Registrar Alta Hospitalar</Text>
          )}
        </TouchableOpacity>
      </View>
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={Colors.primary} />
        <Text style={styles.loadingText}>Carregando pacientes em auditoria...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Área de Auditoria</Text>
        <Text style={styles.headerSubtitle}>
          {pacientes.length} paciente{pacientes.length !== 1 ? 's' : ''} ADMITIDO{pacientes.length !== 1 ? 'S' : ''} aguardando alta
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
            <Text style={styles.emptyText}>Nenhum paciente aguardando alta</Text>
            <Text style={styles.emptySubtext}>
              Todos os pacientes receberam alta hospitalar!
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
    backgroundColor: Colors.primary,
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
    backgroundColor: '#4CAF50',
  },
  statusText: {
    color: '#FFF',
    fontSize: 14,
    fontWeight: 'bold',
  },
  tempoInternacao: {
    color: '#FFF',
    fontSize: 12,
    opacity: 0.9,
  },
  pacienteInfo: {
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
    width: 110,
    marginRight: 8,
  },
  infoValue: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
    flex: 1,
  },
  altaButton: {
    backgroundColor: '#9C27B0',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  altaButtonText: {
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

export default AreaAuditoria;
