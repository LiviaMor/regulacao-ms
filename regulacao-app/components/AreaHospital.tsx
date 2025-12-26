import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  Alert,
  ScrollView,
  Image,
  Platform,
  ActivityIndicator
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import CardDecisaoIA from './CardDecisaoIA';

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
  
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [resultado, setResultado] = useState<any>(null);
  const [userToken, setUserToken] = useState<string | null>(null);

  const pickImage = async () => {
    // Solicitar permissões
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permissão necessária', 'Precisamos de acesso à galeria para selecionar imagens.');
      return;
    }

    // Selecionar imagem
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.8,
    });

    if (!result.canceled) {
      setSelectedImage(result.assets[0].uri);
    }
  };

  const takePhoto = async () => {
    // Solicitar permissões da câmera
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permissão necessária', 'Precisamos de acesso à câmera para tirar fotos.');
      return;
    }

    // Tirar foto
    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.8,
    });

    if (!result.canceled) {
      setSelectedImage(result.assets[0].uri);
    }
  };

  const uploadProntuario = async () => {
    if (!selectedImage || !form.protocolo) {
      Alert.alert('Erro', 'Selecione uma imagem e informe o protocolo.');
      return;
    }

    try {
      setIsProcessing(true);
      
      const formData = new FormData();
      formData.append('protocolo', form.protocolo);
      formData.append('file', {
        uri: selectedImage,
        type: 'image/jpeg',
        name: `prontuario_${form.protocolo}.jpg`,
      } as any);

      const response = await fetch(`${API_BASE_URL}/upload-prontuario`, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const data = await response.json();
      
      if (response.ok) {
        Alert.alert('Sucesso', 'Prontuário enviado com sucesso!');
        setForm(prev => ({ ...prev, prontuario_texto: data.texto_extraido }));
      } else {
        throw new Error(data.detail || 'Erro no upload');
      }
    } catch (error) {
      console.error('Erro no upload:', error);
      Alert.alert('Erro', 'Falha no envio do prontuário. Tente novamente.');
    } finally {
      setIsProcessing(false);
    }
  };

  const processarRegulacao = async () => {
    if (!form.protocolo || !form.cid) {
      Alert.alert('Erro', 'Protocolo e CID são obrigatórios.');
      return;
    }

    try {
      setIsProcessing(true);
      
      const response = await fetch(`${API_BASE_URL}/processar-regulacao`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(form),
      });

      const data = await response.json();
      
      if (response.ok) {
        setResultado(data);
        Alert.alert('Processamento Concluído', 'Análise da IA finalizada com sucesso!');
      } else {
        throw new Error(data.detail || 'Erro no processamento');
      }
    } catch (error) {
      console.error('Erro no processamento:', error);
      Alert.alert('Erro', 'Falha no processamento. Verifique os dados e tente novamente.');
    } finally {
      setIsProcessing(false);
    }
  };

  const quickLogin = async () => {
    try {
      setIsProcessing(true);
      
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

      const data = await response.json();
      
      if (response.ok) {
        setUserToken(data.access_token);
        Alert.alert('Login Realizado', `Bem-vindo, ${data.user_info.nome}!`);
      } else {
        throw new Error(data.detail || 'Erro no login');
      }
    } catch (error) {
      console.error('Erro no login:', error);
      Alert.alert('Erro', 'Falha no login. Verifique sua conexão.');
    } finally {
      setIsProcessing(false);
    }
  };

  const renderResultado = () => {
    if (!resultado) return null;

    // Se temos uma decisão estruturada da IA, usar o CardDecisaoIA
    if (resultado.analise_decisoria) {
      return (
        <CardDecisaoIA 
          decisaoIA={resultado}
          protocolo={form.protocolo}
          userToken={userToken}
          onTransferenciaAutorizada={(res) => {
            Alert.alert('Sucesso', 'Transferência autorizada com sucesso!');
            // Limpar formulário após autorização
            setForm({
              protocolo: '',
              especialidade: '',
              cid: '',
              cid_desc: '',
              prontuario_texto: '',
              historico_paciente: '',
              prioridade_descricao: 'Normal'
            });
            setResultado(null);
          }}
        />
      );
    }

    // Fallback para resultados não estruturados
    const { analise_decisoria, logistica, protocolo_especial } = resultado;

    return (
      <View style={styles.resultadoContainer}>
        <Text style={styles.resultadoTitle}>Resultado da Análise IA</Text>
        
        <View style={styles.resultadoCard}>
          <Text style={styles.resultadoSubtitle}>Análise Decisória</Text>
          <Text style={styles.resultadoText}>
            Score de Prioridade: {analise_decisoria?.score_prioridade}/10
          </Text>
          <Text style={[styles.resultadoText, { 
            color: analise_decisoria?.classificacao_risco === 'VERMELHO' ? '#F44336' :
                   analise_decisoria?.classificacao_risco === 'AMARELO' ? '#FF9800' : '#4CAF50'
          }]}>
            Classificação: {analise_decisoria?.classificacao_risco}
          </Text>
          <Text style={styles.resultadoText}>
            Unidade Sugerida: {analise_decisoria?.unidade_destino_sugerida}
          </Text>
          <Text style={styles.resultadoText}>
            Justificativa: {analise_decisoria?.justificativa_clinica}
          </Text>
        </View>

        <View style={styles.resultadoCard}>
          <Text style={styles.resultadoSubtitle}>Logística</Text>
          <Text style={styles.resultadoText}>
            Ambulância: {logistica?.acionar_ambulancia ? 'SIM' : 'NÃO'}
          </Text>
          <Text style={styles.resultadoText}>
            Tipo de Transporte: {logistica?.tipo_transporte}
          </Text>
          <Text style={styles.resultadoText}>
            Previsão de Vaga: {logistica?.previsao_vaga_h}
          </Text>
        </View>

        {protocolo_especial && (
          <View style={styles.resultadoCard}>
            <Text style={styles.resultadoSubtitle}>Protocolo Especial</Text>
            <Text style={styles.resultadoText}>
              Tipo: {protocolo_especial.tipo}
            </Text>
            <Text style={styles.resultadoText}>
              Instruções: {protocolo_especial.instrucoes_imediatas}
            </Text>
          </View>
        )}
      </View>
    );
  };

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
          placeholder="Especialidade *"
          value={form.especialidade}
          onChangeText={(text) => setForm(prev => ({ ...prev, especialidade: text }))}
        />

        <View style={styles.row}>
          <TextInput
            style={[styles.input, styles.halfInput]}
            placeholder="CID *"
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
          placeholder="Descrição do Quadro Clínico"
          value={form.prontuario_texto}
          onChangeText={(text) => setForm(prev => ({ ...prev, prontuario_texto: text }))}
          multiline
          numberOfLines={4}
        />

        <Text style={styles.sectionTitle}>Autenticação (Opcional)</Text>
        
        <View style={styles.authSection}>
          {userToken ? (
            <View style={styles.authSuccess}>
              <Text style={styles.authSuccessText}>✅ Autenticado como Regulador</Text>
              <TouchableOpacity 
                style={styles.logoutButton}
                onPress={() => setUserToken(null)}
              >
                <Text style={styles.logoutButtonText}>Sair</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <TouchableOpacity 
              style={styles.loginButton}
              onPress={quickLogin}
            >
              <Text style={styles.loginButtonText}>🔐 Login Rápido (Demo)</Text>
            </TouchableOpacity>
          )}
        </View>

        <Text style={styles.sectionTitle}>Upload de Prontuário</Text>
        
        <View style={styles.imageSection}>
          {selectedImage && (
            <Image source={{ uri: selectedImage }} style={styles.imagePreview} />
          )}
          
          <View style={styles.buttonRow}>
            <TouchableOpacity style={styles.imageButton} onPress={takePhoto}>
              <Text style={styles.imageButtonText}>📷 Câmera</Text>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.imageButton} onPress={pickImage}>
              <Text style={styles.imageButtonText}>🖼️ Galeria</Text>
            </TouchableOpacity>
          </View>

          {selectedImage && (
            <TouchableOpacity 
              style={styles.uploadButton} 
              onPress={uploadProntuario}
              disabled={isProcessing}
            >
              {isProcessing ? (
                <ActivityIndicator color="#FFF" />
              ) : (
                <Text style={styles.uploadButtonText}>Enviar Prontuário</Text>
              )}
            </TouchableOpacity>
          )}
        </View>

        <TouchableOpacity 
          style={styles.processButton} 
          onPress={processarRegulacao}
          disabled={isProcessing}
        >
          {isProcessing ? (
            <ActivityIndicator color="#FFF" />
          ) : (
            <Text style={styles.processButtonText}>🤖 Processar com IA</Text>
          )}
        </TouchableOpacity>

        {renderResultado()}
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
  imageSection: {
    alignItems: 'center',
    marginBottom: 20,
  },
  imagePreview: {
    width: 200,
    height: 150,
    borderRadius: 8,
    marginBottom: 15,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
    marginBottom: 15,
  },
  imageButton: {
    backgroundColor: '#E3F2FD',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
    minWidth: 100,
    alignItems: 'center',
  },
  imageButtonText: {
    color: '#004A8D',
    fontWeight: '600',
  },
  uploadButton: {
    backgroundColor: '#FF9800',
    paddingHorizontal: 30,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  uploadButtonText: {
    color: '#FFF',
    fontWeight: 'bold',
    fontSize: 16,
  },
  processButton: {
    backgroundColor: '#4CAF50',
    paddingVertical: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 20,
  },
  processButtonText: {
    color: '#FFF',
    fontWeight: 'bold',
    fontSize: 18,
  },
  authSection: {
    marginBottom: 20,
  },
  authSuccess: {
    backgroundColor: '#E8F5E8',
    padding: 15,
    borderRadius: 8,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#4CAF50',
  },
  authSuccessText: {
    color: '#2E7D32',
    fontWeight: '600',
    flex: 1,
  },
  logoutButton: {
    backgroundColor: '#FF5722',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 4,
  },
  logoutButtonText: {
    color: '#FFF',
    fontSize: 12,
    fontWeight: 'bold',
  },
  loginButton: {
    backgroundColor: '#E3F2FD',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#004A8D',
  },
  loginButtonText: {
    color: '#004A8D',
    fontWeight: '600',
    fontSize: 16,
  },
  resultadoContainer: {
    marginTop: 20,
  },
  resultadoTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
    textAlign: 'center',
  },
  resultadoCard: {
    backgroundColor: '#FFF',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#4CAF50',
  },
  resultadoSubtitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  resultadoText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
});

export default AreaHospital;