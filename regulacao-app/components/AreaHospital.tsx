/**
 * ÁREA HOSPITALAR - Solicitação de Regulação
 * Sistema de Regulação Autônoma SES-GO
 * 
 * Interface profissional para hospitais solicitarem regulação
 * Inclui upload de anexos com análise por IA (OCR + BioBERT + Llama)
 */

import React, { useState, useEffect, useRef } from 'react';
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
  ActivityIndicator,
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
  hospital_origem: string;
  especialidade: string;
  cid: string;
  cid_desc: string;
  prontuario_texto: string;
  historico_paciente: string;
  prioridade_descricao: string;
}

interface AnexoInfo {
  file: File | null;
  preview: string | null;
  analiseIA: any | null;
  processando: boolean;
}

interface PacienteAguardando {
  protocolo: string;
  especialidade: string;
  cid: string;
  cid_desc?: string;
  status: string;
  data_solicitacao: string;
  justificativa_tecnica?: string;
  justificativa_negacao?: string;
  classificacao_risco?: string;
  score_prioridade?: number;
  prontuario_texto?: string;
  historico_paciente?: string;
  prioridade_descricao?: string;
  nome_completo?: string;
  nome_mae?: string;
  cpf?: string;
  telefone_contato?: string;
  hospital_origem?: string;
}

const AreaHospital = () => {
  const [form, setForm] = useState<PacienteForm>({
    protocolo: '',
    nome_completo: '',
    nome_mae: '',
    cpf: '',
    telefone_contato: '',
    hospital_origem: '',
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
  const [editandoPaciente, setEditandoPaciente] = useState<PacienteAguardando | null>(null);
  
  // Estado do anexo
  const [anexo, setAnexo] = useState<AnexoInfo>({
    file: null,
    preview: null,
    analiseIA: null,
    processando: false
  });
  const fileInputRef = useRef<HTMLInputElement>(null);
  
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

  // Função para editar paciente negado
  const editarPacienteNegado = (paciente: PacienteAguardando) => {
    // Preencher formulário com dados do paciente negado
    setForm({
      protocolo: paciente.protocolo,
      nome_completo: paciente.nome_completo || '',
      nome_mae: paciente.nome_mae || '',
      cpf: paciente.cpf || '',
      telefone_contato: paciente.telefone_contato || '',
      hospital_origem: paciente.hospital_origem || '',
      especialidade: paciente.especialidade || '',
      cid: paciente.cid || '',
      cid_desc: paciente.cid_desc || '',
      prontuario_texto: paciente.prontuario_texto || '',
      historico_paciente: paciente.historico_paciente || '',
      prioridade_descricao: paciente.prioridade_descricao || 'Normal'
    });
    setEditandoPaciente(paciente);
    showToast('Edite os dados e clique em REENVIAR', 'info');
  };

  // Função para cancelar edição
  const cancelarEdicao = () => {
    setEditandoPaciente(null);
    setAnexo({ file: null, preview: null, analiseIA: null, processando: false });
    setForm({
      protocolo: '',
      nome_completo: '',
      nome_mae: '',
      cpf: '',
      telefone_contato: '',
      hospital_origem: '',
      especialidade: '',
      cid: '',
      cid_desc: '',
      prontuario_texto: '',
      historico_paciente: '',
      prioridade_descricao: 'Normal'
    });
  };

  // Função para selecionar arquivo (Web)
  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validar tipo
    const tiposPermitidos = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf'];
    if (!tiposPermitidos.includes(file.type)) {
      showToast('Tipo de arquivo nao suportado. Use JPG, PNG, WEBP ou PDF.', 'warning');
      return;
    }

    // Validar tamanho (10MB)
    if (file.size > 10 * 1024 * 1024) {
      showToast('Arquivo muito grande. Maximo: 10MB', 'warning');
      return;
    }

    // Criar preview
    const preview = file.type.startsWith('image/') 
      ? URL.createObjectURL(file) 
      : null;

    setAnexo({
      file,
      preview,
      analiseIA: null,
      processando: true
    });

    // Analisar com IA
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE_URL}/analisar-documento-ia`, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const resultado = await response.json();
        setAnexo(prev => ({
          ...prev,
          analiseIA: resultado.analise,
          processando: false
        }));

        // Se extraiu texto, sugerir adicionar ao prontuário
        const textoOCR = resultado.analise?.etapas?.ocr?.texto_extraido;
        if (textoOCR && textoOCR.length > 20) {
          showToast('Documento analisado! Texto extraido com sucesso.', 'success');
        } else {
          showToast('Documento anexado. Analise de IA concluida.', 'info');
        }
      } else {
        throw new Error('Erro na análise');
      }
    } catch (error) {
      console.error('Erro ao analisar documento:', error);
      setAnexo(prev => ({ ...prev, processando: false }));
      showToast('Documento anexado (analise IA indisponivel)', 'warning');
    }
  };

  // Função para remover anexo
  const removerAnexo = () => {
    if (anexo.preview) {
      URL.revokeObjectURL(anexo.preview);
    }
    setAnexo({ file: null, preview: null, analiseIA: null, processando: false });
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Função para adicionar texto OCR ao prontuário
  const adicionarTextoOCRAoProntuario = () => {
    const textoOCR = anexo.analiseIA?.etapas?.ocr?.texto_extraido;
    if (textoOCR) {
      setForm(prev => ({
        ...prev,
        prontuario_texto: prev.prontuario_texto 
          ? `${prev.prontuario_texto}\n\n[TEXTO DO DOCUMENTO]\n${textoOCR}`
          : `[TEXTO DO DOCUMENTO]\n${textoOCR}`
      }));
      showToast('Texto adicionado ao quadro clinico', 'success');
    }
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
    if (!form.protocolo || !form.nome_completo || !form.nome_mae || !form.cpf || !form.telefone_contato || !form.hospital_origem || !form.cid || !form.especialidade) {
      showToast('Preencha todos os campos obrigatorios (*)', 'warning');
      return;
    }

    // Validação básica de CPF (11 dígitos)
    const cpfLimpo = form.cpf.replace(/\D/g, '');
    if (cpfLimpo.length !== 11) {
      showToast('CPF invalido. Digite 11 digitos.', 'warning');
      return;
    }

    // Validação básica de telefone (10 ou 11 dígitos)
    const telLimpo = form.telefone_contato.replace(/\D/g, '');
    if (telLimpo.length < 10 || telLimpo.length > 11) {
      showToast('Telefone invalido. Digite DDD + numero.', 'warning');
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
          // 3. Upload do anexo (se houver)
          if (anexo.file) {
            try {
              const formData = new FormData();
              formData.append('file', anexo.file);

              const uploadResponse = await fetch(
                `${API_BASE_URL}/upload-documento-medico/${form.protocolo}`,
                { method: 'POST', body: formData }
              );

              if (uploadResponse.ok) {
                const uploadData = await uploadResponse.json();
                console.log('Anexo processado:', uploadData);
              }
            } catch (uploadError) {
              console.error('Erro no upload do anexo:', uploadError);
              // Não falhar a solicitação por causa do anexo
            }
          }

          const mensagem = editandoPaciente 
            ? 'PACIENTE REENVIADO A REGULACAO' 
            : 'SOLICITACAO ENVIADA A REGULACAO';
          showToast(mensagem, 'success');
          
          // Limpar formulário, estado de edição e anexo
          setForm({
            protocolo: '',
            nome_completo: '',
            nome_mae: '',
            cpf: '',
            telefone_contato: '',
            hospital_origem: '',
            especialidade: '',
            cid: '',
            cid_desc: '',
            prontuario_texto: '',
            historico_paciente: '',
            prioridade_descricao: 'Normal'
          });
          setEditandoPaciente(null);
          removerAnexo();
          
          fetchPacientesAguardando();
        } else {
          throw new Error('Erro ao salvar paciente');
        }
      } else {
        throw new Error('Erro no processamento IA');
      }
    } catch (error) {
      console.error('Erro na solicitacao:', error);
      showToast('Falha na solicitacao. Tente novamente.', 'error');
    } finally {
      setIsProcessing(false);
    }
  };

  const renderPacienteAguardando = ({ item }: { item: PacienteAguardando }) => {
    const riskColor = getRiskColor(item.classificacao_risco || 'AMARELO');
    const isNegado = item.status === 'NEGADO_PENDENTE';
    
    return (
      <View style={[styles.pacienteCard, { borderLeftColor: isNegado ? Colors.danger : riskColor }]}>
        <View style={styles.pacienteHeader}>
          <Text style={styles.protocolo}>{item.protocolo}</Text>
          <View style={[styles.statusBadge, { backgroundColor: isNegado ? Colors.danger : Colors.warning }]}>
            <Text style={styles.statusText}>{isNegado ? 'NEGADO' : 'AGUARDANDO'}</Text>
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
          
          {isNegado && item.justificativa_negacao && (
            <View style={[styles.justificativaContainer, { borderLeftColor: Colors.danger }]}>
              <Text style={[styles.justificativaLabel, { color: Colors.danger }]}>Motivo da Negacao:</Text>
              <Text style={styles.justificativa} numberOfLines={3}>
                {item.justificativa_negacao}
              </Text>
            </View>
          )}
          
          {!isNegado && item.justificativa_tecnica && (
            <View style={styles.justificativaContainer}>
              <Text style={styles.justificativaLabel}>Analise da IA:</Text>
              <Text style={styles.justificativa} numberOfLines={3}>
                {item.justificativa_tecnica}
              </Text>
            </View>
          )}
        </View>

        {/* Botão de Editar e Reenviar para pacientes NEGADOS */}
        {isNegado && (
          <TouchableOpacity
            style={styles.editButton}
            onPress={() => editarPacienteNegado(item)}
            activeOpacity={0.8}
          >
            <Text style={styles.editButtonText}>EDITAR E REENVIAR</Text>
          </TouchableOpacity>
        )}
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
            {editandoPaciente && (
              <View style={styles.editingBanner}>
                <Text style={styles.editingBannerText}>
                  EDITANDO PACIENTE NEGADO: {editandoPaciente.protocolo}
                </Text>
                <Text style={styles.editingBannerSubtext}>
                  Motivo: {editandoPaciente.justificativa_negacao || 'Nao informado'}
                </Text>
              </View>
            )}
            
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

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Hospital de Origem *</Text>
              <TextInput
                style={styles.input}
                placeholder="Ex: HOSPITAL ESTADUAL DR ALBERTO RASSI"
                placeholderTextColor={Colors.textMuted}
                value={form.hospital_origem}
                onChangeText={(text) => setForm(prev => ({ ...prev, hospital_origem: text }))}
                autoCapitalize="characters"
              />
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

            {/* Seção de Anexos - Upload de Documentos */}
            <View style={styles.divider} />
            
            <View style={styles.anexoSection}>
              <Text style={styles.sectionTitle}>Anexar Documento</Text>
              <Text style={styles.anexoSubtitle}>
                Foto de prontuario, exame, receita ou documento medico
              </Text>
              
              {Platform.OS === 'web' && (
                <input
                  ref={fileInputRef as any}
                  type="file"
                  accept="image/jpeg,image/png,image/webp,application/pdf"
                  onChange={handleFileSelect as any}
                  style={{ display: 'none' }}
                />
              )}
              
              {!anexo.file ? (
                <View style={styles.uploadArea}>
                  <TouchableOpacity
                    style={styles.uploadButton}
                    onPress={() => {
                      if (Platform.OS === 'web' && fileInputRef.current) {
                        fileInputRef.current.click();
                      } else {
                        showToast('Funcionalidade disponivel apenas na versao web', 'info');
                      }
                    }}
                    activeOpacity={0.8}
                  >
                    <View style={styles.uploadIconContainer}>
                      <Text style={styles.uploadIcon}>+</Text>
                    </View>
                    <Text style={styles.uploadButtonText}>SELECIONAR ARQUIVO</Text>
                    <Text style={styles.uploadHint}>JPG, PNG, WEBP ou PDF (max 10MB)</Text>
                  </TouchableOpacity>
                  
                  <TouchableOpacity
                    style={styles.cameraButton}
                    onPress={() => {
                      if (Platform.OS === 'web' && fileInputRef.current) {
                        fileInputRef.current.setAttribute('capture', 'environment');
                        fileInputRef.current.click();
                        fileInputRef.current.removeAttribute('capture');
                      } else {
                        showToast('Use a camera do dispositivo', 'info');
                      }
                    }}
                    activeOpacity={0.8}
                  >
                    <Text style={styles.cameraButtonText}>TIRAR FOTO</Text>
                  </TouchableOpacity>
                </View>
              ) : (
                <View style={styles.anexoPreview}>
                  <View style={styles.anexoHeader}>
                    <View style={styles.anexoInfo}>
                      <Text style={styles.anexoFilename} numberOfLines={1}>
                        {anexo.file.name}
                      </Text>
                      <Text style={styles.anexoSize}>
                        {(anexo.file.size / 1024).toFixed(1)} KB
                      </Text>
                    </View>
                    <TouchableOpacity
                      style={styles.removerAnexoButton}
                      onPress={removerAnexo}
                    >
                      <Text style={styles.removerAnexoText}>X</Text>
                    </TouchableOpacity>
                  </View>
                  
                  {anexo.preview && (
                    <View style={styles.imagePreviewContainer}>
                      <img 
                        src={anexo.preview} 
                        alt="Preview" 
                        style={{ 
                          maxWidth: '100%', 
                          maxHeight: 200, 
                          borderRadius: 8,
                          objectFit: 'contain'
                        }} 
                      />
                    </View>
                  )}
                  
                  {anexo.processando && (
                    <View style={styles.analiseIAContainer}>
                      <ActivityIndicator size="small" color={Colors.primary} />
                      <Text style={styles.analiseIAText}>Analisando com IA...</Text>
                    </View>
                  )}
                  
                  {anexo.analiseIA && !anexo.processando && (
                    <View style={styles.analiseIAResultado}>
                      <View style={styles.analiseIAHeader}>
                        <Text style={styles.analiseIATitle}>Analise de IA</Text>
                        <View style={[
                          styles.confiancaBadge,
                          { backgroundColor: (anexo.analiseIA.confianca_geral || 0) > 0.6 ? Colors.success : Colors.warning }
                        ]}>
                          <Text style={styles.confiancaText}>
                            {Math.round((anexo.analiseIA.confianca_geral || 0) * 100)}%
                          </Text>
                        </View>
                      </View>
                      
                      {anexo.analiseIA.etapas?.ocr?.texto_extraido && (
                        <View style={styles.ocrResultado}>
                          <Text style={styles.ocrLabel}>Texto extraido (OCR):</Text>
                          <Text style={styles.ocrTexto} numberOfLines={4}>
                            {anexo.analiseIA.etapas.ocr.texto_extraido.substring(0, 300)}
                            {anexo.analiseIA.etapas.ocr.texto_extraido.length > 300 ? '...' : ''}
                          </Text>
                          <TouchableOpacity
                            style={styles.adicionarTextoButton}
                            onPress={adicionarTextoOCRAoProntuario}
                          >
                            <Text style={styles.adicionarTextoButtonText}>
                              ADICIONAR AO QUADRO CLINICO
                            </Text>
                          </TouchableOpacity>
                        </View>
                      )}
                      
                      {anexo.analiseIA.alertas && anexo.analiseIA.alertas.length > 0 && (
                        <View style={styles.alertasContainer}>
                          <Text style={styles.alertasTitle}>Alertas detectados:</Text>
                          {anexo.analiseIA.alertas.map((alerta: any, index: number) => (
                            <View key={index} style={styles.alertaItem}>
                              <Text style={styles.alertaTexto}>
                                {alerta.tipo}: {alerta.mensagem}
                              </Text>
                            </View>
                          ))}
                        </View>
                      )}
                      
                      {anexo.analiseIA.resumo_ia && (
                        <View style={styles.resumoLlama}>
                          <Text style={styles.resumoLabel}>Interpretacao Llama:</Text>
                          <Text style={styles.resumoTexto} numberOfLines={6}>
                            {anexo.analiseIA.resumo_ia.substring(0, 500)}
                          </Text>
                        </View>
                      )}
                    </View>
                  )}
                </View>
              )}
            </View>

            <View style={styles.lgpdNotice}>
              <Text style={styles.lgpdText}>
                Dados protegidos pela LGPD. Informacoes pessoais serao anonimizadas em consultas publicas.
              </Text>
            </View>

            <TouchableOpacity 
              style={[styles.submitButton, editandoPaciente && styles.reenviarButton]} 
              onPress={solicitarRegulacao}
              disabled={isProcessing}
              activeOpacity={0.8}
            >
              <Text style={styles.submitButtonText}>
                {editandoPaciente ? 'REENVIAR PARA REGULACAO' : 'SOLICITAR REGULACAO'}
              </Text>
            </TouchableOpacity>

            {editandoPaciente && (
              <TouchableOpacity 
                style={styles.cancelButton} 
                onPress={cancelarEdicao}
                activeOpacity={0.8}
              >
                <Text style={styles.cancelButtonText}>CANCELAR EDICAO</Text>
              </TouchableOpacity>
            )}
          </View>

          {/* Lista de Pacientes Aguardando */}
          <View style={styles.listSection}>
            <Text style={styles.sectionTitle}>
              Pacientes Aguardando / Negados
            </Text>
            <Text style={styles.listSubtitle}>
              Pacientes negados podem ser editados e reenviados
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
                <View style={styles.emptyIconContainer}>
                  <Text style={styles.emptyIconText}>0</Text>
                </View>
                <Text style={styles.emptyText}>Nenhum paciente aguardando</Text>
                <Text style={styles.emptySubtext}>
                  Os pacientes solicitados aparecerao aqui ate serem regulados
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
  editingBanner: {
    backgroundColor: Colors.warningLight || '#FFF3E0',
    padding: Spacing.md,
    borderRadius: BorderRadius.md,
    marginBottom: Spacing.lg,
    borderLeftWidth: 4,
    borderLeftColor: Colors.warning,
  },
  editingBannerText: {
    fontSize: Typography.fontSize.md,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.warning,
  },
  editingBannerSubtext: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textSecondary,
    marginTop: Spacing.xs,
  },
  listSection: {
    padding: Spacing.lg,
    paddingTop: 0,
  },
  sectionTitle: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.textPrimary,
    marginBottom: Spacing.xs,
    letterSpacing: Typography.letterSpacing.wide,
  },
  listSubtitle: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textMuted,
    marginBottom: Spacing.lg,
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
  reenviarButton: {
    backgroundColor: Colors.warning,
  },
  submitButtonText: {
    color: Colors.textOnPrimary,
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.bold,
    letterSpacing: Typography.letterSpacing.wider,
  },
  cancelButton: {
    backgroundColor: Colors.danger,
    paddingVertical: Spacing.md,
    borderRadius: BorderRadius.md,
    alignItems: 'center',
    marginTop: Spacing.sm,
  },
  cancelButtonText: {
    color: Colors.textOnPrimary,
    fontSize: Typography.fontSize.md,
    fontWeight: Typography.fontWeight.semiBold,
  },
  editButton: {
    backgroundColor: Colors.warning,
    paddingVertical: Spacing.md,
    borderRadius: BorderRadius.md,
    alignItems: 'center',
    marginTop: Spacing.md,
  },
  editButtonText: {
    color: Colors.textOnPrimary,
    fontSize: Typography.fontSize.md,
    fontWeight: Typography.fontWeight.bold,
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
  emptyIconContainer: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: Colors.textMuted,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: Spacing.md,
  },
  emptyIconText: {
    color: '#FFF',
    fontSize: 24,
    fontWeight: 'bold',
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
  // Estilos para seção de anexos
  anexoSection: {
    marginTop: Spacing.md,
  },
  anexoSubtitle: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textMuted,
    marginBottom: Spacing.md,
  },
  uploadArea: {
    flexDirection: 'row',
    gap: Spacing.md,
  },
  uploadButton: {
    flex: 1,
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: Colors.border,
    borderStyle: 'dashed',
  },
  uploadIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: Colors.primaryLight,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: Spacing.sm,
  },
  uploadIcon: {
    fontSize: 24,
    color: Colors.primary,
    fontWeight: 'bold',
  },
  uploadButtonText: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.primary,
    marginBottom: Spacing.xs,
  },
  uploadHint: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    textAlign: 'center',
  },
  cameraButton: {
    backgroundColor: Colors.primaryDark,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    justifyContent: 'center',
    alignItems: 'center',
    minWidth: 100,
  },
  cameraButtonText: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.textOnPrimary,
  },
  anexoPreview: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  anexoHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.sm,
  },
  anexoInfo: {
    flex: 1,
  },
  anexoFilename: {
    fontSize: Typography.fontSize.md,
    fontWeight: Typography.fontWeight.semiBold,
    color: Colors.textPrimary,
  },
  anexoSize: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
  },
  removerAnexoButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: Colors.danger,
    justifyContent: 'center',
    alignItems: 'center',
  },
  removerAnexoText: {
    color: Colors.textOnPrimary,
    fontWeight: 'bold',
    fontSize: 14,
  },
  imagePreviewContainer: {
    alignItems: 'center',
    marginVertical: Spacing.sm,
    backgroundColor: Colors.background,
    borderRadius: BorderRadius.md,
    padding: Spacing.sm,
  },
  analiseIAContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: Spacing.md,
    backgroundColor: Colors.primaryLight,
    borderRadius: BorderRadius.md,
    marginTop: Spacing.sm,
  },
  analiseIAText: {
    marginLeft: Spacing.sm,
    color: Colors.primary,
    fontWeight: Typography.fontWeight.medium,
  },
  analiseIAResultado: {
    marginTop: Spacing.md,
    padding: Spacing.md,
    backgroundColor: Colors.background,
    borderRadius: BorderRadius.md,
    borderLeftWidth: 4,
    borderLeftColor: Colors.success,
  },
  analiseIAHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.sm,
  },
  analiseIATitle: {
    fontSize: Typography.fontSize.md,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.textPrimary,
  },
  confiancaBadge: {
    paddingHorizontal: Spacing.sm,
    paddingVertical: Spacing.xs,
    borderRadius: BorderRadius.full,
  },
  confiancaText: {
    color: Colors.textOnPrimary,
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.bold,
  },
  ocrResultado: {
    marginTop: Spacing.sm,
  },
  ocrLabel: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.semiBold,
    color: Colors.textSecondary,
    marginBottom: Spacing.xs,
  },
  ocrTexto: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textPrimary,
    backgroundColor: Colors.surface,
    padding: Spacing.sm,
    borderRadius: BorderRadius.sm,
    fontStyle: 'italic',
  },
  adicionarTextoButton: {
    backgroundColor: Colors.primary,
    paddingVertical: Spacing.sm,
    paddingHorizontal: Spacing.md,
    borderRadius: BorderRadius.md,
    alignItems: 'center',
    marginTop: Spacing.sm,
  },
  adicionarTextoButtonText: {
    color: Colors.textOnPrimary,
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.bold,
  },
  alertasContainer: {
    marginTop: Spacing.md,
    padding: Spacing.sm,
    backgroundColor: '#FFF3E0',
    borderRadius: BorderRadius.md,
    borderLeftWidth: 3,
    borderLeftColor: Colors.warning,
  },
  alertasTitle: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.warning,
    marginBottom: Spacing.xs,
  },
  alertaItem: {
    marginTop: Spacing.xs,
  },
  alertaTexto: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textSecondary,
  },
  resumoLlama: {
    marginTop: Spacing.md,
  },
  resumoLabel: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.semiBold,
    color: Colors.textSecondary,
    marginBottom: Spacing.xs,
  },
  resumoTexto: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textPrimary,
    lineHeight: Typography.fontSize.sm * Typography.lineHeight.relaxed,
  },
});

export default AreaHospital;
