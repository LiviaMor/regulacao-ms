/**
 * ÁREA HOSPITALAR - Solicitação de Regulação
 * Sistema de Regulação Autônoma SES-GO
 * 
 * Interface profissional para hospitais solicitarem regulação
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  FlatList,
  Platform,
  KeyboardAvoidingView,
} from 'react-native';
import { Colors, Typography, BorderRadius, Shadows, Spacing, getRiskColor } from '@/constants/theme';
import Header from './ui/Header';
import Toast from './ui/Toast';
import AILoadingIndicator from './ui/AILoadingIndicator';

// Configuração da API baseada na plataforma
const API_BASE_URL = Platform.select({
  web: 'http://localhost:8000',
  default: 'http://10.0.2.2:8000'
});

interface PacienteForm {
  protocolo: string;
  nome_completo: string;
  nome_mae: string;
  cpf: string;
  telefone_contato: string;
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
  classificacao_risco?: string;
  score_prioridade?: number;
}

const AreaHospital = () => {
  const [form, setForm] = useState<PacienteForm>({
    protocolo: '',
    nome_completo: '',
    nome_mae: '',
    cpf: '',
    telefone_contato: '',
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
  
  // Toast state
  const [toastVisible, setToastVisible] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState<'success' | 'error' | 'warning' | 'info'>('success');

  useEffect(() => {
    autoLogin();
    fetchPacientesAguardando();
  }, []);

  const showToast = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'success') => {
    setToastMessage(message);
    setToastType(type);
    setToastVisible(true);
  };

  const autoLogin = async () => {
    try {
      const loginData = {
        email: "admin@sesgo.gov.br",
        senha: "admin123"
      };

      await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginData),
      });
    } catch (error) {
      console.error('Erro no auto-login:', error);
    }
  };

  const fetchPacientesAguardando = async () => {
    try {
      setRefreshing(true);
      const response = await fetch(`${API_BASE_URL}/pacientes-hospital-aguardando`);
      
      if (response.ok) {
        const data = await response.json();
        setPacientesAguardando(data);
      } else {
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
    // Validação dos campos obrigatórios
    if (!form.protocolo || !form.nome_completo || !form.nome_mae || !form.cpf || !form.telefone_contato || !form.cid || !form.especialidade) {
      showToast('Preencha todos os campos obrigatórios (*)', 'warning');
      return;
    }

    // Validação básica de CPF (11 dígitos)
    const cpfLimpo = form.cpf.replace(/\D/g, '');
    if (cpfLimpo.length !== 11) {
      showToast('CPF inválido. Digite 11 dígitos.', 'warning');
      return;
    }

    // Validação básica de telefone (10 ou 11 dígitos)
    const telLimpo = form.telefone_contato.replace(/\D/g, '');
    if (telLimpo.length < 10 || telLimpo.length > 11) {
      showToast('Telefone inválido. Digite DDD + número.', 'warning');
      return;
    }

    try {
      setIsProcessing(true);
      
      // 1. Processar com IA
      const iaResponse = await fetch(`${API_BASE_URL}/processar-regulacao`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });

      if (iaResponse.ok) {
        const iaData = await iaResponse.json();
        
        // 2. Salvar paciente
        const salvarResponse = await fetch(`${API_BASE_URL}/salvar-paciente-hospital`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            paciente: form,
            sugestao_ia: iaData
          }),
        });

        if (salvarResponse.ok) {
          showToast('SOLICITAÇÃO ENVIADA À REGULAÇÃO', 'success');
          
          // Limpar formulário
          setForm({
            protocolo: '',
            nome_completo: '',
            nome_mae: '',
            cpf: '',
            telefone_contato: '',
            especialidade: '',
            cid: '',
            cid_desc: '',
            prontuario_texto: '',
            historico_paciente: '',
            prioridade_descricao: 'Normal'
          });
          
          fetchPacientesAguardando();
        } else {
          throw new Error('Erro ao salvar paciente');
        }
      } else {
        throw new Error('Erro no processamento IA');
      }
    } catch (error) {
      console.error('Erro na solicitação:', error);
      showToast('Falha na solicitação. Tente novamente.', 'error');
    } finally {
      setIsProcessing(false);
    }
  };

  const renderPacienteAguardando = ({ item }: { item: PacienteAguardando }) => {
    const riskColor = getRiskColor(item.classificacao_risco || 'AMARELO');
    
    return (
      <View style={[styles.pacienteCard, { borderLeftColor: riskColor }]}>
        <View style={styles.pacienteHeader}>
          <Text style={styles.protocolo}>{item.protocolo}</Text>
          <View style={[styles.statusBadge, { backgroundColor: Colors.warning }]}>
            <Text style={styles.statusText}>AGUARDANDO</Text>
          </View>
        </View>
        
        <View style={styles.pacienteInfo}>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Especialidade</Text>
            <Text style={styles.infoValue}>{item.especialidade}</Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>CID</Text>
            <Text style={styles.infoValue}>{item.cid}</Text>
          </View>
          
          {item.score_prioridade && (
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Score IA</Text>
              <Text style={[styles.infoValue, { color: riskColor, fontWeight: '700' }]}>
                {item.score_prioridade}/10
              </Text>
            </View>
          )}
          
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Solicitado em</Text>
            <Text style={styles.infoValue}>
              {new Date(item.data_solicitacao).toLocaleString('pt-BR')}
            </Text>
          </View>
          
          {item.justificativa_tecnica && (
            <View style={styles.justificativaContainer}>
              <Text style={styles.justificativaLabel}>Análise da IA:</Text>
              <Text style={styles.justificativa} numberOfLines={3}>
                {item.justificativa_tecnica}
              </Text>
            </View>
          )}
        </View>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <Header 
        title="Área Hospitalar" 
        subtitle="Solicitação de Regulação"
      />

      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView 
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {/* Formulário */}
          <View style={styles.formSection}>
            <Text style={styles.sectionTitle}>Dados do Paciente</Text>
            
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Protocolo *</Text>
              <TextInput
                style={styles.input}
                placeholder="Ex: REG-2024-001"
                placeholderTextColor={Colors.textMuted}
                value={form.protocolo}
                onChangeText={(text) => setForm(prev => ({ ...prev, protocolo: text }))}
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Nome Completo do Paciente *</Text>
              <TextInput
                style={styles.input}
                placeholder="Nome completo"
                placeholderTextColor={Colors.textMuted}
                value={form.nome_completo}
                onChangeText={(text) => setForm(prev => ({ ...prev, nome_completo: text }))}
                autoCapitalize="words"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Nome da Mãe *</Text>
              <TextInput
                style={styles.input}
                placeholder="Nome completo da mãe"
                placeholderTextColor={Colors.textMuted}
                value={form.nome_mae}
                onChangeText={(text) => setForm(prev => ({ ...prev, nome_mae: text }))}
                autoCapitalize="words"
              />
            </View>

            <View style={styles.row}>
              <View style={[styles.inputGroup, { flex: 1, marginRight: Spacing.sm }]}>
                <Text style={styles.inputLabel}>CPF *</Text>
                <TextInput
                  style={styles.input}
                  placeholder="000.000.000-00"
                  placeholderTextColor={Colors.textMuted}
                  value={form.cpf}
                  onChangeText={(text) => setForm(prev => ({ ...prev, cpf: text }))}
                  keyboardType="numeric"
                  maxLength={14}
                />
              </View>
              <View style={[styles.inputGroup, { flex: 1 }]}>
                <Text style={styles.inputLabel}>Telefone *</Text>
                <TextInput
                  style={styles.input}
                  placeholder="(62) 98765-4321"
                  placeholderTextColor={Colors.textMuted}
                  value={form.telefone_contato}
                  onChangeText={(text) => setForm(prev => ({ ...prev, telefone_contato: text }))}
                  keyboardType="phone-pad"
                  maxLength={15}
                />
              </View>
            </View>

            <View style={styles.divider} />

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Especialidade *</Text>
              <TextInput
                style={styles.input}
                placeholder="Ex: CARDIOLOGIA, NEUROLOGIA"
                placeholderTextColor={Colors.textMuted}
                value={form.especialidade}
                onChangeText={(text) => setForm(prev => ({ ...prev, especialidade: text }))}
              />
            </View>

            <View style={styles.row}>
              <View style={[styles.inputGroup, { flex: 1, marginRight: Spacing.sm }]}>
                <Text style={styles.inputLabel}>CID *</Text>
                <TextInput
                  style={styles.input}
                  placeholder="Ex: I21.0"
                  placeholderTextColor={Colors.textMuted}
                  value={form.cid}
                  onChangeText={(text) => setForm(prev => ({ ...prev, cid: text }))}
                />
              </View>
              <View style={[styles.inputGroup, { flex: 1.5 }]}>
                <Text style={styles.inputLabel}>Descrição CID</Text>
                <TextInput
                  style={styles.input}
                  placeholder="Descrição do CID"
                  placeholderTextColor={Colors.textMuted}
                  value={form.cid_desc}
                  onChangeText={(text) => setForm(prev => ({ ...prev, cid_desc: text }))}
                />
              </View>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Histórico do Paciente</Text>
              <TextInput
                style={[styles.input, styles.textArea]}
                placeholder="Comorbidades, alergias, medicações em uso..."
                placeholderTextColor={Colors.textMuted}
                value={form.historico_paciente}
                onChangeText={(text) => setForm(prev => ({ ...prev, historico_paciente: text }))}
                multiline
                numberOfLines={3}
                textAlignVertical="top"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Quadro Clínico Atual *</Text>
              <TextInput
                style={[styles.input, styles.textArea, { minHeight: 100 }]}
                placeholder="Descreva os sintomas, sinais vitais e condição atual do paciente..."
                placeholderTextColor={Colors.textMuted}
                value={form.prontuario_texto}
                onChangeText={(text) => setForm(prev => ({ ...prev, prontuario_texto: text }))}
                multiline
                numberOfLines={4}
                textAlignVertical="top"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Prioridade</Text>
              <TextInput
                style={styles.input}
                placeholder="Ex: Emergência, Urgente, Normal"
                placeholderTextColor={Colors.textMuted}
                value={form.prioridade_descricao}
                onChangeText={(text) => setForm(prev => ({ ...prev, prioridade_descricao: text }))}
              />
            </View>

            <View style={styles.lgpdNotice}>
              <Text style={styles.lgpdText}>
                🔒 Dados protegidos pela LGPD. Informações pessoais serão anonimizadas em consultas públicas.
              </Text>
            </View>

            <TouchableOpacity 
              style={styles.submitButton} 
              onPress={solicitarRegulacao}
              disabled={isProcessing}
              activeOpacity={0.8}
            >
              <Text style={styles.submitButtonText}>
                SOLICITAR REGULAÇÃO
              </Text>
            </TouchableOpacity>
          </View>

          {/* Lista de Pacientes Aguardando */}
          <View style={styles.listSection}>
            <Text style={styles.sectionTitle}>
              Pacientes Aguardando Regulação
            </Text>
            
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
                <Text style={styles.emptyIcon}>📋</Text>
                <Text style={styles.emptyText}>Nenhum paciente aguardando</Text>
                <Text style={styles.emptySubtext}>
                  Os pacientes solicitados aparecerão aqui até serem regulados
                </Text>
              </View>
            )}
          </View>
        </ScrollView>
      </KeyboardAvoidingView>

      {/* Loading IA */}
      <AILoadingIndicator 
        visible={isProcessing}
        message="Analisando paciente..."
        subMessage="BioBERT + Pipeline de Hospitais GO"
      />

      {/* Toast */}
      <Toast
        visible={toastVisible}
        message={toastMessage}
        type={toastType}
        onHide={() => setToastVisible(false)}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  keyboardView: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: Spacing.xxxl,
  },
  formSection: {
    padding: Spacing.lg,
  },
  listSection: {
    padding: Spacing.lg,
    paddingTop: 0,
  },
  sectionTitle: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.textPrimary,
    marginBottom: Spacing.lg,
    letterSpacing: Typography.letterSpacing.wide,
  },
  inputGroup: {
    marginBottom: Spacing.md,
  },
  inputLabel: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.semiBold,
    color: Colors.textSecondary,
    marginBottom: Spacing.xs,
    letterSpacing: Typography.letterSpacing.wide,
  },
  input: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.md,
    padding: Spacing.md,
    fontSize: Typography.fontSize.md,
    color: Colors.textPrimary,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  textArea: {
    minHeight: 80,
    textAlignVertical: 'top',
  },
  row: {
    flexDirection: 'row',
  },
  divider: {
    height: 1,
    backgroundColor: Colors.divider,
    marginVertical: Spacing.lg,
  },
  lgpdNotice: {
    backgroundColor: Colors.primaryLight,
    padding: Spacing.md,
    borderRadius: BorderRadius.md,
    marginTop: Spacing.md,
    borderLeftWidth: 3,
    borderLeftColor: Colors.primary,
  },
  lgpdText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.primary,
    lineHeight: Typography.fontSize.xs * Typography.lineHeight.relaxed,
  },
  submitButton: {
    backgroundColor: Colors.success,
    paddingVertical: Spacing.lg,
    borderRadius: BorderRadius.md,
    alignItems: 'center',
    marginTop: Spacing.lg,
    ...Shadows.medium,
  },
  submitButtonText: {
    color: Colors.textOnPrimary,
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.bold,
    letterSpacing: Typography.letterSpacing.wider,
  },
  pacienteCard: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    marginBottom: Spacing.md,
    borderLeftWidth: 6,
    ...Shadows.card,
  },
  pacienteHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.md,
  },
  protocolo: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.primary,
  },
  statusBadge: {
    paddingHorizontal: Spacing.sm,
    paddingVertical: Spacing.xs,
    borderRadius: BorderRadius.full,
  },
  statusText: {
    color: Colors.textOnPrimary,
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.bold,
    letterSpacing: Typography.letterSpacing.wide,
  },
  pacienteInfo: {},
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: Spacing.xs,
  },
  infoLabel: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textMuted,
  },
  infoValue: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textPrimary,
    fontWeight: Typography.fontWeight.medium,
  },
  justificativaContainer: {
    marginTop: Spacing.sm,
    padding: Spacing.sm,
    backgroundColor: Colors.background,
    borderRadius: BorderRadius.md,
    borderLeftWidth: 3,
    borderLeftColor: Colors.primary,
  },
  justificativaLabel: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textSecondary,
    fontWeight: Typography.fontWeight.semiBold,
    marginBottom: Spacing.xs,
  },
  justificativa: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textSecondary,
    fontStyle: 'italic',
    lineHeight: Typography.fontSize.sm * Typography.lineHeight.relaxed,
  },
  emptyContainer: {
    alignItems: 'center',
    paddingVertical: Spacing.xxxl,
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    ...Shadows.card,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: Spacing.md,
  },
  emptyText: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.textSecondary,
    marginBottom: Spacing.xs,
  },
  emptySubtext: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textMuted,
    textAlign: 'center',
    paddingHorizontal: Spacing.xl,
  },
});

export default AreaHospital;
