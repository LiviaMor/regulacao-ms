import React, { useState } from 'react';
import { 
  View, 
  Text, 
  TouchableOpacity, 
  StyleSheet, 
  Alert, 
  ActivityIndicator,
  Platform 
} from 'react-native';

// Configuração da API baseada na plataforma
const API_BASE_URL = Platform.select({
  web: 'http://localhost:8000',
  default: 'http://10.0.2.2:8000' // Android Emulator
});

interface DecisaoIA {
  analise_decisoria: {
    score_prioridade: number;
    classificacao_risco: 'VERMELHO' | 'AMARELO' | 'VERDE';
    unidade_destino_sugerida: string;
    justificativa_clinica: string;
  };
  logistica: {
    acionar_ambulancia: boolean;
    tipo_transporte: 'USA' | 'USB' | 'AEROMÉDICO';
    previsao_vaga_h: string;
  };
  protocolo_especial?: {
    tipo: string;
    instrucoes_imediatas: string;
  };
}

interface CardDecisaoIAProps {
  decisaoIA: DecisaoIA;
  protocolo: string;
  onTransferenciaAutorizada?: (resultado: any) => void;
  userToken?: string;
}

const CardDecisaoIA: React.FC<CardDecisaoIAProps> = ({ 
  decisaoIA, 
  protocolo, 
  onTransferenciaAutorizada,
  userToken 
}) => {
  const [isProcessing, setIsProcessing] = useState(false);

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

  const getTransportIcon = (tipo: string) => {
    switch (tipo) {
      case 'USA': return '🚑'; // Unidade de Suporte Avançado
      case 'USB': return '🚐'; // Unidade de Suporte Básico
      case 'AEROMÉDICO': return '🚁'; // Helicóptero
      default: return '🚗';
    }
  };

  const acionarTransferencia = async () => {
    if (!userToken) {
      Alert.alert(
        'Autenticação Necessária', 
        'Você precisa estar logado para autorizar transferências.'
      );
      return;
    }

    Alert.alert(
      'Confirmar Transferência',
      `Autorizar transferência do paciente ${protocolo} para:\n\n${decisaoIA.analise_decisoria.unidade_destino_sugerida}\n\nTransporte: ${decisaoIA.logistica.tipo_transporte}`,
      [
        { text: 'Cancelar', style: 'cancel' },
        { 
          text: 'Autorizar', 
          style: 'default',
          onPress: () => executarTransferencia()
        }
      ]
    );
  };

  const executarTransferencia = async () => {
    try {
      setIsProcessing(true);

      const transferencia = {
        protocolo: protocolo,
        unidade_destino: decisaoIA.analise_decisoria.unidade_destino_sugerida,
        tipo_transporte: decisaoIA.logistica.tipo_transporte,
        observacoes: `Autorizado via IA - Score: ${decisaoIA.analise_decisoria.score_prioridade}/10 - ${decisaoIA.analise_decisoria.justificativa_clinica}`
      };

      const response = await fetch(`${API_BASE_URL}/transferencia`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userToken}`
        },
        body: JSON.stringify(transferencia)
      });

      const resultado = await response.json();

      if (response.ok) {
        Alert.alert(
          'Transferência Autorizada! ✅',
          `Protocolo: ${protocolo}\nDestino: ${transferencia.unidade_destino}\nTransporte: ${transferencia.tipo_transporte}\n\nA ambulância será acionada automaticamente.`,
          [{ text: 'OK' }]
        );

        // Callback para atualizar a interface pai
        if (onTransferenciaAutorizada) {
          onTransferenciaAutorizada(resultado);
        }
      } else {
        throw new Error(resultado.detail || 'Erro na autorização');
      }
    } catch (error) {
      console.error('Erro na transferência:', error);
      Alert.alert(
        'Erro na Transferência',
        'Não foi possível autorizar a transferência. Tente novamente ou contate o suporte técnico.'
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const renderProtocoloEspecial = () => {
    if (!decisaoIA.protocolo_especial) return null;

    return (
      <View style={styles.protocoloEspecial}>
        <Text style={styles.protocoloTitle}>
          🏥 Protocolo Especial: {decisaoIA.protocolo_especial.tipo}
        </Text>
        <Text style={styles.protocoloInstrucoes}>
          {decisaoIA.protocolo_especial.instrucoes_imediatas}
        </Text>
      </View>
    );
  };

  return (
    <View style={styles.card}>
      {/* Header com classificação de risco */}
      <View style={[
        styles.header, 
        { backgroundColor: getRiskColor(decisaoIA.analise_decisoria.classificacao_risco) }
      ]}>
        <Text style={styles.whiteText}>
          {getRiskIcon(decisaoIA.analise_decisoria.classificacao_risco)} 
          SUGESTÃO DA IA: {decisaoIA.analise_decisoria.classificacao_risco}
        </Text>
        <Text style={styles.scoreText}>
          Score de Prioridade: {decisaoIA.analise_decisoria.score_prioridade}/10
        </Text>
      </View>

      {/* Corpo do card */}
      <View style={styles.body}>
        {/* Destino sugerido */}
        <View style={styles.section}>
          <Text style={styles.label}>🏥 Destino Sugerido:</Text>
          <Text style={styles.value}>
            {decisaoIA.analise_decisoria.unidade_destino_sugerida}
          </Text>
        </View>

        {/* Justificativa */}
        <View style={styles.section}>
          <Text style={styles.label}>📋 Justificativa Clínica:</Text>
          <Text style={styles.justificativa}>
            {decisaoIA.analise_decisoria.justificativa_clinica}
          </Text>
        </View>

        {/* Logística */}
        <View style={styles.logisticaContainer}>
          <Text style={styles.logisticaTitle}>🚑 Logística de Transporte</Text>
          
          <View style={styles.logisticaRow}>
            <View style={styles.logisticaItem}>
              <Text style={styles.logisticaLabel}>Tipo:</Text>
              <Text style={styles.logisticaValue}>
                {getTransportIcon(decisaoIA.logistica.tipo_transporte)} {decisaoIA.logistica.tipo_transporte}
              </Text>
            </View>
            
            <View style={styles.logisticaItem}>
              <Text style={styles.logisticaLabel}>Ambulância:</Text>
              <Text style={[
                styles.logisticaValue,
                { color: decisaoIA.logistica.acionar_ambulancia ? '#388E3C' : '#D32F2F' }
              ]}>
                {decisaoIA.logistica.acionar_ambulancia ? '✅ SIM' : '❌ NÃO'}
              </Text>
            </View>
          </View>

          <View style={styles.logisticaItem}>
            <Text style={styles.logisticaLabel}>⏱️ Previsão de Vaga:</Text>
            <Text style={styles.logisticaValue}>
              {decisaoIA.logistica.previsao_vaga_h}
            </Text>
          </View>
        </View>

        {/* Protocolo especial */}
        {renderProtocoloEspecial()}

        {/* Botão de ação */}
        <TouchableOpacity 
          style={[
            styles.button,
            isProcessing && styles.buttonDisabled
          ]} 
          onPress={acionarTransferencia}
          disabled={isProcessing}
        >
          {isProcessing ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>
              🚑 AUTORIZAR TRANSFERÊNCIA E AMBULÂNCIA
            </Text>
          )}
        </TouchableOpacity>

        {/* Disclaimer */}
        <Text style={styles.disclaimer}>
          ⚠️ Esta é uma sugestão baseada em IA. A decisão final é sempre do regulador médico.
        </Text>
      </View>
    </View>
  );
};

// Estilos seguindo o padrão SES-GO (Azul Institucional, Branco e Cinza Claro)
const styles = StyleSheet.create({
  card: { 
    borderRadius: 12, 
    overflow: 'hidden', 
    elevation: 6, 
    backgroundColor: '#fff', 
    margin: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.15,
    shadowRadius: 6,
  },
  header: { 
    padding: 15, 
    alignItems: 'center' 
  },
  whiteText: { 
    color: '#fff', 
    fontWeight: 'bold', 
    fontSize: 16,
    textAlign: 'center'
  },
  scoreText: {
    color: '#fff',
    fontSize: 14,
    marginTop: 4,
    opacity: 0.9
  },
  body: { 
    padding: 20 
  },
  section: {
    marginBottom: 15
  },
  label: { 
    fontSize: 13, 
    color: '#666', 
    fontWeight: '600',
    marginBottom: 5
  },
  value: { 
    fontSize: 16, 
    fontWeight: 'bold', 
    color: '#004A8D',
    lineHeight: 22
  },
  justificativa: { 
    fontSize: 14, 
    fontStyle: 'italic', 
    color: '#333',
    lineHeight: 20,
    backgroundColor: '#F5F7FA',
    padding: 12,
    borderRadius: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#004A8D'
  },
  logisticaContainer: {
    backgroundColor: '#F8F9FA',
    padding: 15,
    borderRadius: 8,
    marginVertical: 10
  },
  logisticaTitle: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10
  },
  logisticaRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8
  },
  logisticaItem: {
    flex: 1,
    marginRight: 10
  },
  logisticaLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2
  },
  logisticaValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333'
  },
  protocoloEspecial: {
    backgroundColor: '#FFF3E0',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#FFB74D',
    marginVertical: 10
  },
  protocoloTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#E65100',
    marginBottom: 5
  },
  protocoloInstrucoes: {
    fontSize: 13,
    color: '#BF360C',
    fontStyle: 'italic'
  },
  button: { 
    backgroundColor: '#004A8D', 
    padding: 18, 
    borderRadius: 8, 
    marginTop: 20, 
    alignItems: 'center',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  buttonDisabled: {
    backgroundColor: '#999',
    elevation: 0
  },
  buttonText: { 
    color: '#fff', 
    fontWeight: 'bold',
    fontSize: 16
  },
  disclaimer: {
    fontSize: 11,
    color: '#999',
    textAlign: 'center',
    marginTop: 15,
    fontStyle: 'italic'
  }
});

export default CardDecisaoIA;