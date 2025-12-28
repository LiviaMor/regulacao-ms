import React, { useState } from 'react';
import { 
  View, 
  Text, 
  TouchableOpacity, 
  StyleSheet, 
  Alert, 
  ActivityIndicator,
  Platform,
  ScrollView,
  Dimensions,
  useWindowDimensions
} from 'react-native';
import StatusProcessamento from './StatusProcessamento';

// Obter dimensões da tela
const { width: SCREEN_WIDTH } = Dimensions.get('window');

// Helper para alerts compatíveis com web
const showAlert = (title: string, message: string, buttons?: any[]) => {
  if (Platform.OS === 'web') {
    if (buttons && buttons.length > 1) {
      // Para confirmações, usar confirm
      const confirmButton = buttons.find(b => b.style !== 'cancel');
      if (window.confirm(`${title}\n\n${message}`)) {
        confirmButton?.onPress?.();
      }
    } else {
      window.alert(`${title}\n\n${message}`);
    }
  } else {
    Alert.alert(title, message, buttons);
  }
};

// Configuração da API baseada na plataforma
const API_BASE_URL = Platform.select({
  web: 'http://localhost:8000',  // Sistema Unificado
  default: 'http://10.0.2.2:8000' // Android Emulator
});

interface DecisaoIA {
  analise_decisoria?: {
    score_prioridade: number;
    classificacao_risco: 'VERMELHO' | 'AMARELO' | 'VERDE';
    unidade_destino_sugerida: string;
    justificativa_clinica: string;
  };
  hospital_escolhido?: string;
  justificativa_tecnica?: string;
  logistica?: {
    acionar_ambulancia: boolean;
    tipo_transporte: 'USA' | 'USB' | 'AEROMÉDICO';
    previsao_vaga_h: string;
  };
  matchmaking_logistico?: {
    hospital_destino: string;
    cidade_origem: string;
    distancia_km: number;
    tempo_estimado_min: number;
    score_logistico: number;
    score_final: number;
    viabilidade: string;
  };
  ambulancia_sugerida?: {
    id: string;
    tipo: string;
    status: string;
    tempo_chegada_min: number;
    regiao: string;
  };
  rota_otimizada?: {
    origem: {
      cidade: string;
      coordenadas: [number, number];
    };
    destino: {
      hospital: string;
      coordenadas: [number, number];
    };
    via_recomendada: string;
    alertas_rota: string[];
  };
  protocolo_especial?: {
    tipo: string;
    ativo: boolean;
    instrucoes: string[];
    alertas: string[];
    instrucoes_imediatas?: string;
  };
  metadata?: {
    tempo_processamento: number;
    biobert_usado: boolean;
    biobert_disponivel?: boolean;
    matchmaker_usado: boolean;
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
  
  // Hook para responsividade
  const { width } = useWindowDimensions();
  const isSmallScreen = width < 400;
  const isMediumScreen = width >= 400 && width < 768;
  const isLargeScreen = width >= 768;

  const getRiskColor = (risco: string) => {
    switch (risco) {
      case 'VERMELHO': return '#D32F2F';
      case 'AMARELO': return '#F57C00';
      case 'VERDE': return '#388E3C';
      default: return '#666';
    }
  };

  const getRiskIcon = (risco: string) => {
    return risco;
  };

  const getTransportIcon = (tipo: string) => {
    return tipo;
  };

  const acionarTransferencia = async () => {
    if (!userToken) {
      showAlert(
        'Autenticação Necessária', 
        'Você precisa estar logado para autorizar transferências.'
      );
      return;
    }

    const hospital = decisaoIA.analise_decisoria?.unidade_destino_sugerida || 
                    decisaoIA.hospital_escolhido || 
                    decisaoIA.matchmaking_logistico?.hospital_destino || 
                    'Hospital não definido';

    const transporte = decisaoIA.logistica?.tipo_transporte || 
                      decisaoIA.ambulancia_sugerida?.tipo || 
                      'USB';

    if (Platform.OS === 'web') {
      if (window.confirm(`Confirmar Transferência\n\nAutorizar transferência do paciente ${protocolo} para:\n\n${hospital}\n\nTransporte: ${transporte}`)) {
        executarTransferencia('AUTORIZADA');
      }
    } else {
      Alert.alert(
        'Confirmar Transferência',
        `Autorizar transferência do paciente ${protocolo} para:\n\n${hospital}\n\nTransporte: ${transporte}`,
        [
          { text: 'Cancelar', style: 'cancel' },
          { 
            text: 'Autorizar', 
            style: 'default',
            onPress: () => executarTransferencia('AUTORIZADA')
          }
        ]
      );
    }
  };

  const negarTransferencia = async () => {
    if (!userToken) {
      showAlert('Erro', 'Você precisa estar logado para negar transferências.');
      return;
    }

    // Alert.prompt não funciona na web, usar window.prompt como fallback
    const justificativa = window.prompt(
      `Negar Transferência - Protocolo ${protocolo}\n\nInforme o motivo da negação:`,
      ''
    );
    if (justificativa && justificativa.trim() !== '') {
      executarTransferencia('NEGADA', justificativa.trim());
    } else if (justificativa !== null) {
      showAlert('Erro', 'Justificativa é obrigatória para negar a transferência.');
    }
  };

  const alterarDecisao = async () => {
    if (!userToken) {
      showAlert('Erro', 'Você precisa estar logado para alterar decisões.');
      return;
    }

    const hospital = decisaoIA.analise_decisoria?.unidade_destino_sugerida || 
                    decisaoIA.hospital_escolhido || 
                    decisaoIA.matchmaking_logistico?.hospital_destino || 
                    'Hospital não definido';

    // Usar window.prompt para web
    const novoHospital = window.prompt(
      `Alterar Decisão da IA\n\nHospital atual: ${hospital}\n\nInforme o novo hospital de destino:`,
      hospital
    );
    if (novoHospital && novoHospital.trim() !== '') {
      executarAlteracaoEAutorizacao(novoHospital.trim());
    } else if (novoHospital !== null) {
      showAlert('Erro', 'Nome do hospital é obrigatório.');
    }
  };

  const executarAlteracaoEAutorizacao = async (novoHospital: string) => {
    try {
      setIsProcessing(true);

      const score = decisaoIA.analise_decisoria?.score_prioridade || 
                   decisaoIA.matchmaking_logistico?.score_final || 5;

      const transporte = decisaoIA.logistica?.tipo_transporte || 
                        decisaoIA.ambulancia_sugerida?.tipo || 
                        'USB';

      const observacoes = `ALTERADA pelo regulador - Hospital original: ${decisaoIA.analise_decisoria?.unidade_destino_sugerida || 'N/A'} → Novo: ${novoHospital} - Score IA: ${score}/10 - Decisão modificada pelo regulador médico`;

      const payload = {
        protocolo: protocolo,
        decisao_regulador: 'AUTORIZADA',
        unidade_destino: novoHospital,
        tipo_transporte: transporte,
        observacoes: observacoes,
        decisao_ia_original: decisaoIA,
        justificativa_negacao: null,
        decisao_alterada: true,
        hospital_original: decisaoIA.analise_decisoria?.unidade_destino_sugerida || 'N/A'
      };

      const response = await fetch(`${API_BASE_URL}/decisao-regulador`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userToken}`
        },
        body: JSON.stringify(payload)
      });

      const resultado = await response.json();

      if (response.ok) {
        const titulo = 'Decisão Alterada e Autorizada';
        const mensagem = `Protocolo: ${protocolo}\nHospital Original: ${payload.decisao_ia_original.analise_decisoria?.unidade_destino_sugerida || 'N/A'}\nNovo Destino: ${novoHospital}\nTransporte: ${transporte}\n\nA ambulância será acionada automaticamente.\nPaciente será movido para a área de transferência.`;
        
        showAlert(titulo, mensagem);

        // Callback para atualizar a interface pai
        if (onTransferenciaAutorizada) {
          onTransferenciaAutorizada(resultado);
        }
      } else {
        throw new Error(resultado.detail || 'Erro na alteração');
      }
    } catch (error) {
      console.error('Erro na alteração:', error);
      showAlert(
        'Erro na Alteração',
        'Não foi possível alterar a decisão. Tente novamente ou contate o suporte técnico.'
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const executarTransferencia = async (decisao: 'AUTORIZADA' | 'NEGADA', justificativaNegacao?: string) => {
    try {
      setIsProcessing(true);

      const hospital = decisaoIA.analise_decisoria?.unidade_destino_sugerida || 
                      decisaoIA.hospital_escolhido || 
                      decisaoIA.matchmaking_logistico?.hospital_destino || 
                      'Hospital não definido';

      const transporte = decisaoIA.logistica?.tipo_transporte || 
                        decisaoIA.ambulancia_sugerida?.tipo || 
                        'USB';

      const score = decisaoIA.analise_decisoria?.score_prioridade || 
                   decisaoIA.matchmaking_logistico?.score_final || 5;

      const justificativa = decisaoIA.analise_decisoria?.justificativa_clinica || 
                           decisaoIA.justificativa_tecnica || 
                           'Justificativa não disponível';

      const observacoes = decisao === 'NEGADA' 
        ? `NEGADA pelo regulador - Motivo: ${justificativaNegacao} - Score IA: ${score}/10`
        : `${decisao} pelo regulador - Score IA: ${score}/10 - ${justificativa}`;

      const payload = {
        protocolo: protocolo,
        decisao_regulador: decisao,
        unidade_destino: hospital,
        tipo_transporte: transporte,
        observacoes: observacoes,
        decisao_ia_original: decisaoIA,
        justificativa_negacao: justificativaNegacao || null
      };

      const response = await fetch(`${API_BASE_URL}/decisao-regulador`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userToken}`
        },
        body: JSON.stringify(payload)
      });

      const resultado = await response.json();

      if (response.ok) {
        if (decisao === 'AUTORIZADA') {
                  const titulo = 'Transferência Autorizada';
          const mensagem = `Protocolo: ${protocolo}\nDestino: ${hospital}\nTransporte: ${transporte}\n\nA ambulância será acionada automaticamente.\nPaciente será movido para a área de transferência.`;
          
          showAlert(titulo, mensagem);
        } else {
          const titulo = 'Transferência Negada';
          const mensagem = `Protocolo: ${protocolo}\nMotivo: ${justificativaNegacao}\n\nPaciente retornará à fila de regulação.\nHospital será notificado da negação.`;
          
          showAlert(titulo, mensagem);
        }

        // Callback para atualizar a interface pai
        if (onTransferenciaAutorizada) {
          onTransferenciaAutorizada(resultado);
        }
      } else {
        throw new Error(resultado.detail || 'Erro na decisão');
      }
    } catch (error) {
      console.error('Erro na decisão:', error);
      showAlert(
        'Erro na Decisão',
        'Não foi possível registrar a decisão. Tente novamente ou contate o suporte técnico.'
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const renderProtocoloEspecial = () => {
    if (!decisaoIA.protocolo_especial?.ativo) return null;

    return (
      <View style={styles.protocoloEspecial}>
        <Text style={styles.protocoloTitle}>
          Protocolo Especial: {decisaoIA.protocolo_especial.tipo}
        </Text>
        
        {decisaoIA.protocolo_especial.alertas && decisaoIA.protocolo_especial.alertas.length > 0 && (
          <View style={styles.alertasContainer}>
            <Text style={styles.alertasTitle}>Alertas:</Text>
            {decisaoIA.protocolo_especial.alertas.map((alerta, index) => (
              <Text key={index} style={styles.alertaText}>• {alerta}</Text>
            ))}
          </View>
        )}
        
        {decisaoIA.protocolo_especial.instrucoes && decisaoIA.protocolo_especial.instrucoes.length > 0 && (
          <View style={styles.instrucoesContainer}>
            <Text style={styles.instrucoesTitle}>Instruções:</Text>
            {decisaoIA.protocolo_especial.instrucoes.map((instrucao, index) => (
              <Text key={index} style={styles.instrucaoText}>• {instrucao}</Text>
            ))}
          </View>
        )}
        
        {decisaoIA.protocolo_especial.instrucoes_imediatas && (
          <Text style={styles.protocoloInstrucoes}>
            {decisaoIA.protocolo_especial.instrucoes_imediatas}
          </Text>
        )}
      </View>
    );
  };

  const renderMatchmakingLogistico = () => {
    if (!decisaoIA.matchmaking_logistico) return null;

    const matchmaking = decisaoIA.matchmaking_logistico;
    const ambulancia = decisaoIA.ambulancia_sugerida;
    const rota = decisaoIA.rota_otimizada;

    return (
      <View style={styles.matchmakingContainer}>
        <Text style={styles.matchmakingTitle}>Matchmaker Logístico</Text>
        
        {/* Dados Logísticos */}
        <View style={styles.logisticaRow}>
          <View style={styles.logisticaItem}>
            <Text style={styles.logisticaLabel}>Distância:</Text>
            <Text style={styles.logisticaValue}>{matchmaking.distancia_km} km</Text>
          </View>
          
          <View style={styles.logisticaItem}>
            <Text style={styles.logisticaLabel}>Tempo:</Text>
            <Text style={styles.logisticaValue}>{matchmaking.tempo_estimado_min} min</Text>
          </View>
        </View>

        <View style={styles.logisticaRow}>
          <View style={styles.logisticaItem}>
            <Text style={styles.logisticaLabel}>Score Logístico:</Text>
            <Text style={styles.logisticaValue}>{matchmaking.score_logistico}/10</Text>
          </View>
          
          <View style={styles.logisticaItem}>
            <Text style={styles.logisticaLabel}>Viabilidade:</Text>
            <Text style={[
              styles.logisticaValue,
              { color: matchmaking.viabilidade === 'VIAVEL' ? '#4CAF50' : '#FF9800' }
            ]}>
              {matchmaking.viabilidade}
            </Text>
          </View>
        </View>

        {/* Ambulância Sugerida */}
        {ambulancia && (
          <View style={styles.ambulanciaContainer}>
            <Text style={styles.ambulanciaTitle}>Ambulância: {ambulancia.id}</Text>
            <View style={styles.logisticaRow}>
              <View style={styles.logisticaItem}>
                <Text style={styles.logisticaLabel}>Tipo:</Text>
                <Text style={styles.logisticaValue}>
                  {getTransportIcon(ambulancia.tipo)} {ambulancia.tipo}
                </Text>
              </View>
              
              <View style={styles.logisticaItem}>
                <Text style={styles.logisticaLabel}>Chegada:</Text>
                <Text style={styles.logisticaValue}>{ambulancia.tempo_chegada_min} min</Text>
              </View>
            </View>
          </View>
        )}

        {/* Rota Otimizada */}
        {rota && (
          <View style={styles.rotaContainer}>
            <Text style={styles.rotaTitle}>Rota: {rota.origem.cidade} → {rota.destino.hospital.split(' ').pop()}</Text>
            <Text style={styles.rotaVia}>Via: {rota.via_recomendada}</Text>
            
            {rota.alertas_rota && rota.alertas_rota.length > 0 && (
              <View style={styles.alertasRotaContainer}>
                {rota.alertas_rota.map((alerta, index) => (
                  <Text key={index} style={styles.alertaRotaText}>{alerta}</Text>
                ))}
              </View>
            )}
          </View>
        )}

        {/* Info: Ambulância será acionada ao AUTORIZAR ou ALTERAR */}
        {ambulancia && (
          <View style={styles.infoAmbulancia}>
            <Text style={styles.infoAmbulanciaText}>
              🚑 Ambulância {ambulancia.tipo} será acionada automaticamente ao AUTORIZAR ou ALTERAR
            </Text>
          </View>
        )}
      </View>
    );
  };

  // Estilos dinâmicos baseados no tamanho da tela
  const dynamicStyles = {
    card: {
      margin: isSmallScreen ? 8 : 15,
      maxWidth: isLargeScreen ? 600 : undefined,
      alignSelf: isLargeScreen ? 'center' as const : undefined,
      width: isLargeScreen ? 600 : undefined,
    },
    body: {
      padding: isSmallScreen ? 12 : 20,
    },
    botoesDecisao: {
      flexDirection: isSmallScreen ? 'column' as const : 'row' as const,
      gap: isSmallScreen ? 10 : 8,
    },
    botaoDecisao: {
      flex: isSmallScreen ? undefined : 1,
      paddingVertical: isSmallScreen ? 14 : 12,
    },
  };

  return (
    <ScrollView 
      style={styles.scrollContainer}
      contentContainerStyle={styles.scrollContent}
      showsVerticalScrollIndicator={false}
    >
      <View style={[styles.card, dynamicStyles.card]}>
        {/* Header com classificação de risco */}
        <View style={[
          styles.header, 
          { backgroundColor: getRiskColor(decisaoIA.analise_decisoria?.classificacao_risco || 'AMARELO') }
        ]}>
          <Text style={[styles.whiteText, isSmallScreen && { fontSize: 14 }]}>
            SUGESTÃO DA IA: {decisaoIA.analise_decisoria?.classificacao_risco || 'AMARELO'}
          </Text>
          <Text style={styles.scoreText}>
            Score: {decisaoIA.analise_decisoria?.score_prioridade || decisaoIA.matchmaking_logistico?.score_final || 5}/10
          </Text>
        </View>

      {/* Corpo do card */}
      <View style={[styles.body, dynamicStyles.body]}>
        {/* Destino sugerido */}
        <View style={styles.section}>
          <Text style={[styles.label, isSmallScreen && { fontSize: 11 }]}>Destino Sugerido:</Text>
          <Text style={[styles.value, isSmallScreen && { fontSize: 14 }]}>
            {decisaoIA.analise_decisoria?.unidade_destino_sugerida || 
             decisaoIA.hospital_escolhido || 
             decisaoIA.matchmaking_logistico?.hospital_destino || 
             'Hospital não definido'}
          </Text>
        </View>

        {/* Justificativa */}
        <View style={styles.section}>
          <Text style={[styles.label, isSmallScreen && { fontSize: 11 }]}>Justificativa Clínica:</Text>
          <Text style={[styles.justificativa, isSmallScreen && { fontSize: 12, padding: 8 }]}>
            {decisaoIA.analise_decisoria?.justificativa_clinica || 
             decisaoIA.justificativa_tecnica || 
             'Justificativa não disponível'}
          </Text>
        </View>

        {/* Matchmaker Logístico */}
        {renderMatchmakingLogistico()}

        {/* Logística Tradicional (fallback) */}
        {decisaoIA.logistica && !decisaoIA.matchmaking_logistico && (
          <View style={styles.logisticaContainer}>
            <Text style={styles.logisticaTitle}>Logística de Transporte</Text>
            
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
                  {decisaoIA.logistica.acionar_ambulancia ? 'SIM' : 'NÃO'}
                </Text>
              </View>
            </View>

            <View style={styles.logisticaItem}>
              <Text style={styles.logisticaLabel}>Previsão de Vaga:</Text>
              <Text style={styles.logisticaValue}>
                {decisaoIA.logistica.previsao_vaga_h}
              </Text>
            </View>
          </View>
        )}

        {/* Protocolo especial */}
        {renderProtocoloEspecial()}

        {/* Status de Processamento */}
        {decisaoIA.metadata && (
          <StatusProcessamento
            biobert_usado={decisaoIA.metadata.biobert_usado}
            biobert_disponivel={decisaoIA.metadata.biobert_disponivel}
            matchmaker_usado={decisaoIA.metadata.matchmaker_usado}
            tempo_processamento={decisaoIA.metadata.tempo_processamento}
            pipeline_rag={true}
          />
        )}

        {/* Botões de Decisão do Regulador - Conforme DIAGRAMA_FLUXO_COMPLETO.md */}
        {/* AUTORIZAR = Aceita sugestão IA + Chama Ambulância → Transferência */}
        {/* NEGAR = Discorda da IA → Volta para Hospital */}
        {/* ALTERAR = Muda hospital + Chama Ambulância → Transferência */}
        <View style={[styles.botoesDecisao, dynamicStyles.botoesDecisao]}>
          <TouchableOpacity 
            style={[styles.botaoDecisao, styles.botaoAutorizar, dynamicStyles.botaoDecisao]} 
            onPress={acionarTransferencia}
            disabled={isProcessing}
          >
            {isProcessing ? (
              <ActivityIndicator color="#fff" size="small" />
            ) : (
              <>
                <Text style={styles.botaoDecisaoIcon}>✅</Text>
                <Text style={[styles.botaoDecisaoText, isSmallScreen && { fontSize: 12 }]}>AUTORIZAR</Text>
                <Text style={styles.botaoDecisaoSubtext}>Chama Ambulância</Text>
              </>
            )}
          </TouchableOpacity>

          <TouchableOpacity 
            style={[styles.botaoDecisao, styles.botaoNegar, dynamicStyles.botaoDecisao]} 
            onPress={negarTransferencia}
            disabled={isProcessing}
          >
            {isProcessing ? (
              <ActivityIndicator color="#fff" size="small" />
            ) : (
              <>
                <Text style={styles.botaoDecisaoIcon}>❌</Text>
                <Text style={[styles.botaoDecisaoText, isSmallScreen && { fontSize: 12 }]}>NEGAR</Text>
                <Text style={styles.botaoDecisaoSubtext}>Volta p/ Hospital</Text>
              </>
            )}
          </TouchableOpacity>

          <TouchableOpacity 
            style={[styles.botaoDecisao, styles.botaoAlterar, dynamicStyles.botaoDecisao]} 
            onPress={alterarDecisao}
            disabled={isProcessing}
          >
            {isProcessing ? (
              <ActivityIndicator color="#fff" size="small" />
            ) : (
              <>
                <Text style={styles.botaoDecisaoIcon}>✏️</Text>
                <Text style={[styles.botaoDecisaoText, isSmallScreen && { fontSize: 12 }]}>ALTERAR</Text>
                <Text style={styles.botaoDecisaoSubtext}>Muda Hospital</Text>
              </>
            )}
          </TouchableOpacity>
        </View>

        {/* Legenda do fluxo */}
        <View style={styles.legendaFluxo}>
          <Text style={styles.legendaText}>
            ✅ Autorizar: Aceita sugestão e aciona ambulância
          </Text>
          <Text style={styles.legendaText}>
            ❌ Negar: Paciente retorna ao hospital de origem
          </Text>
          <Text style={styles.legendaText}>
            ✏️ Alterar: Muda hospital destino e aciona ambulância
          </Text>
        </View>

        {/* Disclaimer */}
        <Text style={[styles.disclaimer, isSmallScreen && { fontSize: 10 }]}>
          Esta é uma sugestão baseada em IA. A decisão final é sempre do regulador médico.
        </Text>
      </View>
      </View>
    </ScrollView>
  );
};

// Estilos seguindo o padrão SES-GO (Azul Institucional, Branco e Cinza Claro)
const styles = StyleSheet.create({
  scrollContainer: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingBottom: 20,
  },
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
  botoesDecisao: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 20,
    gap: 8,
  },
  botaoDecisao: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderRadius: 8,
    alignItems: 'center',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  botaoAutorizar: {
    backgroundColor: '#4CAF50',
  },
  botaoNegar: {
    backgroundColor: '#F44336',
  },
  botaoAlterar: {
    backgroundColor: '#FF9800',
  },
  botaoDecisaoIcon: {
    fontSize: 16,
    marginBottom: 2,
  },
  botaoDecisaoText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 11,
    textAlign: 'center',
  },
  botaoDecisaoSubtext: {
    color: 'rgba(255,255,255,0.8)',
    fontSize: 9,
    textAlign: 'center',
    marginTop: 2,
  },
  legendaFluxo: {
    backgroundColor: '#F5F7FA',
    padding: 10,
    borderRadius: 8,
    marginTop: 10,
  },
  legendaText: {
    fontSize: 10,
    color: '#666',
    marginBottom: 3,
  },
  infoAmbulancia: {
    backgroundColor: '#E3F2FD',
    padding: 8,
    borderRadius: 6,
    marginTop: 8,
  },
  infoAmbulanciaText: {
    fontSize: 11,
    color: '#1565C0',
    textAlign: 'center',
    fontStyle: 'italic',
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
  },
  // Novos estilos para Matchmaker Logístico
  matchmakingContainer: {
    backgroundColor: '#E8F5E8',
    padding: 15,
    borderRadius: 8,
    marginVertical: 10,
    borderWidth: 1,
    borderColor: '#4CAF50'
  },
  matchmakingTitle: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#2E7D32',
    marginBottom: 10
  },
  ambulanciaContainer: {
    backgroundColor: '#FFF3E0',
    padding: 10,
    borderRadius: 6,
    marginTop: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#FF9800'
  },
  ambulanciaTitle: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#E65100',
    marginBottom: 5
  },
  rotaContainer: {
    backgroundColor: '#F3E5F5',
    padding: 10,
    borderRadius: 6,
    marginTop: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#9C27B0'
  },
  rotaTitle: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#6A1B9A',
    marginBottom: 3
  },
  rotaVia: {
    fontSize: 12,
    color: '#7B1FA2',
    fontStyle: 'italic'
  },
  alertasContainer: {
    marginTop: 8
  },
  alertasTitle: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#D32F2F',
    marginBottom: 3
  },
  alertaText: {
    fontSize: 11,
    color: '#F44336',
    marginBottom: 2
  },
  instrucoesContainer: {
    marginTop: 8
  },
  instrucoesTitle: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#1976D2',
    marginBottom: 3
  },
  instrucaoText: {
    fontSize: 11,
    color: '#1565C0',
    marginBottom: 2
  },
  alertasRotaContainer: {
    marginTop: 5
  },
  alertaRotaText: {
    fontSize: 11,
    color: '#E65100',
    marginBottom: 2
  },
  chamarAmbulanciaButton: {
    backgroundColor: '#FF5722',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  chamarAmbulanciaText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 13
  },
  metadataContainer: {
    backgroundColor: '#F5F5F5',
    padding: 10,
    borderRadius: 6,
    marginVertical: 8
  },
  metadataTitle: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#666',
    marginBottom: 3
  },
  metadataText: {
    fontSize: 11,
    color: '#777'
  }
});

export default CardDecisaoIA;