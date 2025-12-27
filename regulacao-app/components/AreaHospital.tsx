import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  Alert,
  ScrollView,
  FlatList,
  Platform,
  ActivityIndicator
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';

// Configuração da API baseada na plataforma
const API_BASE_URL = Platform.select({
  web: 'http://localhost:8000',
  default: 'http://10.0.2.2:8000' // Android Emulator
});

interface PacienteForm {
  protocolo: string;
  especialidade: string;
  cid: string;
  cid_desc: string;
  prontuario_texto: string;
  historico_paciente: string;
  prioridade_descricao: string;
}

interface PacienteAguardando {
  protocolo: string;
  especialidade: string;
  cid: string;
  status: string;
  data_solicitacao: string;
  justificativa_tecnica?: string;
}

const AreaHospital = () => {
  const [form, setForm] = useState<PacienteForm>({
    protocolo: '',
    especialidade: '',
    cid: '',
    cid_desc: '',
    prontuario_texto: '',
    historico_paciente: '',
    prioridade_descricao: 'Normal'
  });
  
  const [isProcessing, setIsProcessing] = useState(false);
  const [pacientesAguardando, setPacientesAguardando] = useState<PacienteAguardando[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  // Auto-login para simplificar o fluxo
  useEffect(() => {
    autoLogin();
    fetchPacientesAguardando();
  }, []);

  const autoLogin = async () => {
    try {
      const loginData = {
        email: "admin@sesgo.gov.br",
        senha: "admin123"
      };

      const response = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(loginData),
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Auto-login realizado com sucesso');
      }
    } catch (error) {
      console.error('Erro no auto-login:', error);
    }
  };

  const fetchPacientesAguardando = async () => {
    try {
      setRefreshing(true);
      
      // Buscar pacientes que foram inseridos pelo hospital e aguardam regulação
      const response = await fetch(`${API_BASE_URL}/pacientes-hospital-aguardando`);
      
      if (response.ok) {
        const data = await response.json();
        setPacientesAguardando(data);
      } else {
        // Se endpoint não existir, usar dados simulados
        setPacientesAguardando([]);
      }
    } catch (error) {
      console.error('Erro ao buscar pacientes:', error);
      setPacientesAguardando([]);
    } finally {
      setRefreshing(false);
    }
  };

  const solicitarRegulacao = async () => {
    if (!form.protocolo || !form.cid || !form.especialidade) {
      Alert.alert('Erro', 'Protocolo, CID e Especialidade são obrigatórios.');
      return;
    }

    try {
      setIsProcessing(true);
      
      // 1. Processar com IA para obter sugestão
      const iaResponse = await fetch(`${API_BASE_URL}/processar-regulacao`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(form),
      });

      if (iaResponse.ok) {
        const iaData = await iaResponse.json();
        
        // 2. Salvar paciente no banco com sugestão da IA
        const salvarResponse = await fetch(`${API_BASE_URL}/salvar-paciente-hospital`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            paciente: form,
            sugestao_ia: iaData
          }),
        });

        if (salvarResponse.ok) {
          Alert.alert(
            'Regulação Solicitada', 
            `Protocolo: ${form.protocolo}\n\nSugestão da IA:\nHospital: ${iaData.analise_decisoria.unidade_destino_sugerida}\nRisco: ${iaData.analise_decisoria.classificacao_risco}\nScore: ${iaData.analise_decisoria.score_prioridade}/10\n\nPaciente adicionado à fila de regulação!`,
            [
              {
                text: 'OK',
                onPress: () => {
                  // Limpar formulário
                  setForm({
                    protocolo: '',
                    especialidade: '',
                    cid: '',
                    cid_desc: '',
                    prontuario_texto: '',
                    historico_paciente: '',
                    prioridade_descricao: 'Normal'
                  });
                  
                  // Recarregar lista
                  fetchPacientesAguardando();
                }
              }
            ]
          );
        } else {
          throw new Error('Erro ao salvar paciente');
        }
      } else {
        throw new Error('Erro no processamento IA');
      }
    } catch (error) {
      console.error('Erro na solicitação:', error);
      Alert.alert('Erro', 'Falha na solicitação de regulação. Tente novamente.');
    } finally {
      setIsProcessing(false);
    }
  };

  const renderPacienteAguardando = ({ item }: { item: PacienteAguardando }) => (
    <View style={styles.pacienteCard}>
      <View style={styles.pacienteHeader}>
        <Text style={styles.protocolo}>{item.protocolo}</Text>
        <View style={styles.statusBadge}>
          <Text style={styles.statusText}>AGUARDANDO</Text>
        </View>
      </View>
      
      <View style={styles.pacienteInfo}>
        <Text style={styles.infoLabel}>Especialidade:</Text>
        <Text style={styles.infoValue}>{item.especialidade}</Text>
        
        <Text style={styles.infoLabel}>CID:</Text>
        <Text style={styles.infoValue}>{item.cid}</Text>
        
        <Text style={styles.infoLabel}>Solicitado em:</Text>
        <Text style={styles.infoValue}>
          {new Date(item.data_solicitacao).toLocaleString('pt-BR')}
        </Text>
        
        {item.justificativa_tecnica && (
          <>
            <Text style={styles.infoLabel}>Sugestão da IA:</Text>
            <Text style={styles.justificativa} numberOfLines={3}>
              {item.justificativa_tecnica}
            </Text>
          </>
        )}
      </View>
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Área Hospitalar</Text>
        <Text style={styles.headerSubtitle}>Solicitação de Regulação</Text>
      </View>

      <View style={styles.form}>
        <Text style={styles.sectionTitle}>Dados do Paciente</Text>
        
        <TextInput
          style={styles.input}
          placeholder="Protocolo *"
          value={form.protocolo}
          onChangeText={(text) => setForm(prev => ({ ...prev, protocolo: text }))}
        />

        <TextInput
          style={styles.input}
          placeholder="Especialidade * (ex: CARDIOLOGIA, NEUROLOGIA)"
          value={form.especialidade}
          onChangeText={(text) => setForm(prev => ({ ...prev, especialidade: text }))}
        />

        <View style={styles.row}>
          <TextInput
            style={[styles.input, styles.halfInput]}
            placeholder="CID * (ex: I21.0)"
            value={form.cid}
            onChangeText={(text) => setForm(prev => ({ ...prev, cid: text }))}
          />
          <TextInput
            style={[styles.input, styles.halfInput]}
            placeholder="Descrição do CID"
            value={form.cid_desc}
            onChangeText={(text) => setForm(prev => ({ ...prev, cid_desc: text }))}
          />
        </View>

        <TextInput
          style={[styles.input, styles.textArea]}
          placeholder="Histórico do Paciente"
          value={form.historico_paciente}
          onChangeText={(text) => setForm(prev => ({ ...prev, historico_paciente: text }))}
          multiline
          numberOfLines={3}
        />

        <TextInput
          style={[styles.input, styles.textArea]}
          placeholder="Descrição do Quadro Clínico *"
          value={form.prontuario_texto}
          onChangeText={(text) => setForm(prev => ({ ...prev, prontuario_texto: text }))}
          multiline
          numberOfLines={4}
        />

        <TextInput
          style={styles.input}
          placeholder="Prioridade (ex: Emergência, Moderada, Baixa)"
          value={form.prioridade_descricao}
          onChangeText={(text) => setForm(prev => ({ ...prev, prioridade_descricao: text }))}
        />

        <TouchableOpacity 
          style={styles.solicitarButton} 
          onPress={solicitarRegulacao}
          disabled={isProcessing}
        >
          {isProcessing ? (
            <ActivityIndicator color="#FFF" />
          ) : (
            <Text style={styles.solicitarButtonText}>
              SOLICITAR REGULAÇÃO
            </Text>
          )}
        </TouchableOpacity>

        <Text style={styles.sectionTitle}>Pacientes Aguardando Regulação</Text>
        
        {pacientesAguardando.length > 0 ? (
          <FlatList
            data={pacientesAguardando}
            renderItem={renderPacienteAguardando}
            keyExtractor={(item) => item.protocolo}
            scrollEnabled={false}
            showsVerticalScrollIndicator={false}
          />
        ) : (
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>Nenhum paciente aguardando</Text>
            <Text style={styles.emptySubtext}>
              Os pacientes solicitados aparecerão aqui até serem regulados
            </Text>
          </View>
        )}
      </View>
    </ScrollView>
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
  form: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 15,
    marginTop: 10,
  },
  input: {
    backgroundColor: '#FFF',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E0E0E0',
    fontSize: 16,
  },
  textArea: {
    height: 80,
    textAlignVertical: 'top',
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  halfInput: {
    width: '48%',
  },
  solicitarButton: {
    backgroundColor: '#4CAF50',
    paddingVertical: 18,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 20,
    marginBottom: 30,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
  },
  solicitarButtonText: {
    color: '#FFF',
    fontWeight: 'bold',
    fontSize: 18,
  },
  pacienteCard: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
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
  statusBadge: {
    backgroundColor: '#FF9800',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    minWidth: 100,
    alignItems: 'center',
  },
  statusText: {
    color: '#FFF',
    fontSize: 12,
    fontWeight: 'bold',
  },
  pacienteInfo: {
    marginBottom: 8,
  },
  infoLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 6,
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
  emptyContainer: {
    alignItems: 'center',
    paddingVertical: 30,
    backgroundColor: '#FFF',
    borderRadius: 12,
    marginTop: 10,
  },
  emptyText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#666',
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    paddingHorizontal: 20,
  },
});

export default AreaHospital;