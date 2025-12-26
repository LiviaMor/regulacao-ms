import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  TouchableOpacity, 
  Alert, 
  Platform,
  ActivityIndicator 
} from 'react-native';
import FilaRegulacao from '@/components/FilaRegulacao';

// Configuração da API baseada na plataforma
const API_BASE_URL = Platform.select({
  web: 'http://localhost:8000',
  default: 'http://10.0.2.2:8000' // Android Emulator
});

export default function RegulacaoScreen() {
  const [userToken, setUserToken] = useState<string | null>(null);
  const [userInfo, setUserInfo] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  const quickLogin = async () => {
    try {
      setIsLoading(true);
      
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
        setUserInfo(data.user_info);
        Alert.alert('Login Realizado', `Bem-vindo, ${data.user_info.nome}!`);
      } else {
        throw new Error(data.detail || 'Erro no login');
      }
    } catch (error) {
      console.error('Erro no login:', error);
      Alert.alert('Erro', 'Falha no login. Verifique sua conexão.');
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    Alert.alert(
      'Confirmar Logout',
      'Deseja realmente sair do sistema?',
      [
        { text: 'Cancelar', style: 'cancel' },
        { 
          text: 'Sair', 
          style: 'destructive',
          onPress: () => {
            setUserToken(null);
            setUserInfo(null);
          }
        }
      ]
    );
  };

  // Se não estiver logado, mostrar tela de login
  if (!userToken) {
    return (
      <View style={styles.container}>
        <View style={styles.loginContainer}>
          <View style={styles.loginHeader}>
            <Text style={styles.loginTitle}>🏥 Área do Regulador</Text>
            <Text style={styles.loginSubtitle}>
              Sistema de Regulação Autônoma SES-GO
            </Text>
          </View>

          <View style={styles.loginCard}>
            <Text style={styles.loginCardTitle}>Acesso Restrito</Text>
            <Text style={styles.loginCardText}>
              Esta área é destinada exclusivamente para reguladores médicos 
              autorizados pela SES-GO.
            </Text>

            <View style={styles.credentialsInfo}>
              <Text style={styles.credentialsTitle}>Credenciais de Demonstração:</Text>
              <Text style={styles.credentialsText}>📧 admin@sesgo.gov.br</Text>
              <Text style={styles.credentialsText}>🔐 admin123</Text>
            </View>

            <TouchableOpacity 
              style={styles.loginButton}
              onPress={quickLogin}
              disabled={isLoading}
            >
              {isLoading ? (
                <ActivityIndicator color="#FFF" />
              ) : (
                <Text style={styles.loginButtonText}>
                  🔐 Entrar como Regulador
                </Text>
              )}
            </TouchableOpacity>

            <Text style={styles.disclaimer}>
              ⚠️ Em produção, utilize suas credenciais oficiais da SES-GO
            </Text>
          </View>
        </View>
      </View>
    );
  }

  // Se estiver logado, mostrar a fila de regulação
  return (
    <View style={styles.container}>
      {/* Header com informações do usuário */}
      <View style={styles.userHeader}>
        <View style={styles.userInfo}>
          <Text style={styles.userName}>👨‍⚕️ {userInfo?.nome}</Text>
          <Text style={styles.userRole}>{userInfo?.tipo_usuario}</Text>
        </View>
        <TouchableOpacity style={styles.logoutButton} onPress={logout}>
          <Text style={styles.logoutButtonText}>Sair</Text>
        </TouchableOpacity>
      </View>

      {/* Fila de regulação */}
      <FilaRegulacao userToken={userToken} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F7FA',
  },
  loginContainer: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
  },
  loginHeader: {
    alignItems: 'center',
    marginBottom: 40,
  },
  loginTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#004A8D',
    textAlign: 'center',
    marginBottom: 8,
  },
  loginSubtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  loginCard: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 24,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  loginCardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 12,
  },
  loginCardText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    lineHeight: 20,
    marginBottom: 20,
  },
  credentialsInfo: {
    backgroundColor: '#F8F9FA',
    padding: 16,
    borderRadius: 8,
    marginBottom: 20,
    borderLeftWidth: 3,
    borderLeftColor: '#004A8D',
  },
  credentialsTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  credentialsText: {
    fontSize: 13,
    color: '#555',
    fontFamily: 'monospace',
    marginBottom: 4,
  },
  loginButton: {
    backgroundColor: '#004A8D',
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 16,
  },
  loginButtonText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  disclaimer: {
    fontSize: 11,
    color: '#999',
    textAlign: 'center',
    fontStyle: 'italic',
  },
  userHeader: {
    backgroundColor: '#004A8D',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    paddingTop: 50, // Para status bar
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  userRole: {
    color: '#E3F2FD',
    fontSize: 12,
    marginTop: 2,
  },
  logoutButton: {
    backgroundColor: '#FF5722',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
  },
  logoutButtonText: {
    color: '#FFF',
    fontSize: 12,
    fontWeight: 'bold',
  },
});