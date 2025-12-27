/**
 * DASHBOARD PÚBLICO - Monitoramento em Tempo Real
 * Sistema de Regulação Autônoma SES-GO
 * 
 * Interface pública para acompanhamento da rede hospitalar
 */

import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  FlatList, 
  RefreshControl,
  Platform,
} from 'react-native';
import { 
  Colors, 
  Typography, 
  BorderRadius, 
  Shadows, 
  Spacing,
} from '@/constants/theme';
import Header from './ui/Header';
import Toast from './ui/Toast';
import TransparenciaWidget from './TransparenciaWidget';
import OcupacaoHospitais from './OcupacaoHospitais';

const API_BASE_URL = Platform.select({
  web: 'http://localhost:8000',
  default: 'http://10.0.2.2:8000'
});

interface UnidadePressao {
  unidade_executante_desc: string;
  cidade: string;
  pacientes_em_fila: number;
}

interface StatusSummary {
  status: string;
  count: number;
}

const DashboardPublico = ({ dadosLeitos: initialData }: { dadosLeitos?: UnidadePressao[] }) => {
  const [dadosLeitos, setDadosLeitos] = useState<UnidadePressao[]>(initialData || []);
  const [refreshing, setRefreshing] = useState(false);
  const [statusSummary, setStatusSummary] = useState<StatusSummary[]>([]);
  const [ocupacaoHospitais, setOcupacaoHospitais] = useState([]);
  const [resumoOcupacao, setResumoOcupacao] = useState(null);
  const [lastUpdate, setLastUpdate] = useState<string | null>(null);
  const [toastVisible, setToastVisible] = useState(false);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/dashboard/leitos`);
      const data = await response.json();
      
      setDadosLeitos(data.unidades_pressao || []);
      setStatusSummary(data.status_summary || []);
      setOcupacaoHospitais(data.ocupacao_hospitais || []);
      setResumoOcupacao(data.resumo_ocupacao || null);
      setLastUpdate(data.ultima_atualizacao);
    } catch (error) {
      console.error('Erro ao buscar dados:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchDashboardData();
    setRefreshing(false);
    setToastVisible(true);
  };

  useEffect(() => {
    if (!initialData || initialData.length === 0) {
      fetchDashboardData();
    }
    
    const interval = setInterval(fetchDashboardData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const getStatusConfig = (count: number) => {
    if (count > 15) return { color: Colors.danger, text: 'CRÍTICO' };
    if (count > 8) return { color: Colors.warning, text: 'ALTO' };
    if (count > 3) return { color: Colors.riskYellow, text: 'MODERADO' };
    return { color: Colors.success, text: 'NORMAL' };
  };

  const renderStatusSummary = () => (
    <View style={styles.summaryCard}>
      <Text style={styles.summaryTitle}>Resumo da Rede SES-GO</Text>
      <View style={styles.summaryGrid}>
        {statusSummary.map((item, index) => (
          <View key={index} style={styles.summaryItem}>
            <Text style={styles.summaryValue}>{item.count}</Text>
            <Text style={styles.summaryLabel}>
              {item.status.replace('_', ' ')}
            </Text>
          </View>
        ))}
      </View>
      {lastUpdate && (
        <Text style={styles.summaryFooter}>
          Última atualização: {new Date(lastUpdate).toLocaleString('pt-BR')}
        </Text>
      )}
    </View>
  );

  const renderUnidadeCard = ({ item }: { item: UnidadePressao }) => {
    const config = getStatusConfig(item.pacientes_em_fila);
    
    return (
      <View style={[styles.unidadeCard, { borderLeftColor: config.color }]}>
        <View style={styles.unidadeHeader}>
          <Text style={styles.unidadeNome} numberOfLines={2}>
            {item.unidade_executante_desc}
          </Text>
          <View style={[styles.statusBadge, { backgroundColor: config.color }]}>
            <Text style={styles.statusBadgeText}>{config.text}</Text>
          </View>
        </View>
        
        <View style={styles.unidadeContent}>
          <View style={styles.metricContainer}>
            <Text style={styles.metricLabel}>Pacientes em Fila</Text>
            <Text style={[styles.metricValue, { color: config.color }]}>
              {item.pacientes_em_fila}
            </Text>
          </View>
          
          {item.cidade && (
            <View style={styles.cidadeContainer}>
              <Text style={styles.cidadeIcon}>📍</Text>
              <Text style={styles.cidadeText}>{item.cidade}</Text>
            </View>
          )}
        </View>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <Header 
        title="SES-GO | Regulação" 
        subtitle="Monitoramento em Tempo Real"
      />
      
      <FlatList
        data={dadosLeitos}
        renderItem={renderUnidadeCard}
        keyExtractor={(item, index) => `${item.unidade_executante_desc}-${index}`}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl 
            refreshing={refreshing} 
            onRefresh={onRefresh}
            colors={[Colors.primary]}
            tintColor={Colors.primary}
          />
        }
        ListHeaderComponent={() => (
          <>
            {/* Banner de Fonte de Dados */}
            <View style={styles.fonteBanner}>
              <Text style={styles.fonteIcon}>🏛️</Text>
              <View style={styles.fonteTexto}>
                <Text style={styles.fonteTitulo}>Dados Oficiais SUS Goiás</Text>
                <Text style={styles.fonteSubtitulo}>
                  Fonte: Portal da Transparência SES-GO
                </Text>
              </View>
              {lastUpdate && (
                <View style={styles.fonteUpdate}>
                  <Text style={styles.fonteUpdateText}>
                    {new Date(lastUpdate).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                  </Text>
                </View>
              )}
            </View>
            
            {statusSummary.length > 0 && renderStatusSummary()}
            
            {ocupacaoHospitais.length > 0 && resumoOcupacao && (
              <OcupacaoHospitais 
                ocupacao_hospitais={ocupacaoHospitais}
                resumo_ocupacao={resumoOcupacao}
              />
            )}
            
            <TransparenciaWidget />
            
            {dadosLeitos.length > 0 && (
              <View style={styles.sectionHeader}>
                <Text style={styles.sectionTitle}>
                  Unidades com Pressão na Regulação
                </Text>
              </View>
            )}
          </>
        )}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyIcon}>✅</Text>
            <Text style={styles.emptyText}>Sistema Operando Normalmente</Text>
            <Text style={styles.emptySubtext}>
              Nenhuma unidade com pressão crítica no momento
            </Text>
          </View>
        }
        showsVerticalScrollIndicator={false}
      />

      <Toast
        visible={toastVisible}
        message="Dados atualizados com sucesso"
        type="success"
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
  listContent: {
    paddingBottom: Spacing.xxxl,
  },
  summaryCard: {
    backgroundColor: Colors.surface,
    margin: Spacing.lg,
    padding: Spacing.lg,
    borderRadius: BorderRadius.lg,
    ...Shadows.card,
  },
  summaryTitle: {
    fontSize: Typography.fontSize.md,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.textPrimary,
    marginBottom: Spacing.md,
    textAlign: 'center',
  },
  summaryGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  summaryItem: {
    alignItems: 'center',
    flex: 1,
  },
  summaryValue: {
    fontSize: Typography.fontSize.xxl,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.primary,
  },
  summaryLabel: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    textAlign: 'center',
    marginTop: Spacing.xs,
  },
  summaryFooter: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    textAlign: 'center',
    marginTop: Spacing.md,
    fontStyle: 'italic',
  },
  sectionHeader: {
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
  },
  sectionTitle: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.primary,
    letterSpacing: Typography.letterSpacing.wide,
  },
  unidadeCard: {
    backgroundColor: Colors.surface,
    marginHorizontal: Spacing.lg,
    marginBottom: Spacing.md,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    borderLeftWidth: 6,
    ...Shadows.card,
  },
  unidadeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: Spacing.md,
  },
  unidadeNome: {
    fontSize: Typography.fontSize.md,
    fontWeight: Typography.fontWeight.semiBold,
    color: Colors.textPrimary,
    flex: 1,
    marginRight: Spacing.sm,
    lineHeight: Typography.fontSize.md * Typography.lineHeight.normal,
  },
  statusBadge: {
    paddingHorizontal: Spacing.sm,
    paddingVertical: Spacing.xs,
    borderRadius: BorderRadius.full,
  },
  statusBadgeText: {
    color: Colors.textOnPrimary,
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.bold,
  },
  unidadeContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  metricContainer: {
    flex: 1,
  },
  metricLabel: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textMuted,
    marginBottom: Spacing.xs,
  },
  metricValue: {
    fontSize: Typography.fontSize.xxxl,
    fontWeight: Typography.fontWeight.bold,
  },
  cidadeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  cidadeIcon: {
    fontSize: Typography.fontSize.sm,
    marginRight: Spacing.xs,
  },
  cidadeText: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textSecondary,
  },
  emptyContainer: {
    alignItems: 'center',
    paddingVertical: Spacing.xxxl,
    marginHorizontal: Spacing.lg,
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
    color: Colors.success,
    marginBottom: Spacing.xs,
  },
  emptySubtext: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textMuted,
    textAlign: 'center',
  },
  // Banner de Fonte de Dados
  fonteBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.primaryLight,
    marginHorizontal: Spacing.lg,
    marginTop: Spacing.md,
    marginBottom: Spacing.sm,
    padding: Spacing.md,
    borderRadius: BorderRadius.md,
    borderLeftWidth: 4,
    borderLeftColor: Colors.primary,
  },
  fonteIcon: {
    fontSize: 24,
    marginRight: Spacing.md,
  },
  fonteTexto: {
    flex: 1,
  },
  fonteTitulo: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.primary,
  },
  fonteSubtitulo: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textSecondary,
    marginTop: 2,
  },
  fonteUpdate: {
    backgroundColor: Colors.primary,
    paddingHorizontal: Spacing.sm,
    paddingVertical: Spacing.xs,
    borderRadius: BorderRadius.sm,
  },
  fonteUpdateText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textOnPrimary,
    fontWeight: Typography.fontWeight.bold,
  },
});

export default DashboardPublico;
