/**
 * OCUPAÇÃO DE HOSPITAIS - Dashboard de Leitos
 * Sistema de Regulação Autônoma SES-GO
 * 
 * Exibe ocupação com indicadores de tendência do MS-Ingestao
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Dimensions,
} from 'react-native';
import { 
  Colors, 
  Typography, 
  BorderRadius, 
  Shadows, 
  Spacing,
  getTrendColor,
  getOccupancyColor,
} from '@/constants/theme';
import HospitalCard, { HospitalData } from './ui/HospitalCard';

const { width } = Dimensions.get('window');

interface ResumoOcupacao {
  total_leitos: number;
  total_ocupados: number;
  total_disponiveis: number;
  taxa_media: number;
  hospitais_criticos: number;
  hospitais_alto: number;
  hospitais_normal: number;
}

interface OcupacaoHospitaisProps {
  ocupacao_hospitais: HospitalData[];
  resumo_ocupacao: ResumoOcupacao;
}

const OcupacaoHospitais: React.FC<OcupacaoHospitaisProps> = ({ 
  ocupacao_hospitais, 
  resumo_ocupacao 
}) => {
  const hospitaisTendenciaAlta = ocupacao_hospitais.filter(h => h.tendencia === 'ALTA').length;
  const hospitaisTendenciaQueda = ocupacao_hospitais.filter(h => h.tendencia === 'QUEDA').length;
  const hospitaisComAlerta = ocupacao_hospitais.filter(h => h.alerta_saturacao).length;

  return (
    <View style={styles.container}>
      <Text style={styles.sectionTitle}>Ocupação de Leitos - Rede Estadual</Text>
      
      {/* Resumo Card */}
      <View style={styles.resumoCard}>
        <Text style={styles.resumoTitle}>Resumo da Rede Estadual</Text>
        
        <View style={styles.metricsGrid}>
          <View style={styles.metricItem}>
            <Text style={styles.metricValue}>{resumo_ocupacao.total_leitos}</Text>
            <Text style={styles.metricLabel}>Total de Leitos</Text>
          </View>
          
          <View style={styles.metricItem}>
            <Text style={[styles.metricValue, { color: Colors.warning }]}>
              {resumo_ocupacao.total_ocupados}
            </Text>
            <Text style={styles.metricLabel}>Ocupados</Text>
          </View>
          
          <View style={styles.metricItem}>
            <Text style={[styles.metricValue, { color: Colors.success }]}>
              {resumo_ocupacao.total_disponiveis}
            </Text>
            <Text style={styles.metricLabel}>Disponíveis</Text>
          </View>
          
          <View style={styles.metricItem}>
            <Text style={[styles.metricValue, { color: Colors.primary }]}>
              {resumo_ocupacao.taxa_media}%
            </Text>
            <Text style={styles.metricLabel}>Taxa Média</Text>
          </View>
        </View>

        <View style={styles.statusRow}>
          <View style={styles.statusItem}>
            <View style={[styles.statusDot, { backgroundColor: Colors.danger }]} />
            <Text style={styles.statusText}>{resumo_ocupacao.hospitais_criticos} Críticos</Text>
          </View>
          
          <View style={styles.statusItem}>
            <View style={[styles.statusDot, { backgroundColor: Colors.warning }]} />
            <Text style={styles.statusText}>{resumo_ocupacao.hospitais_alto} Alto</Text>
          </View>
          
          <View style={styles.statusItem}>
            <View style={[styles.statusDot, { backgroundColor: Colors.success }]} />
            <Text style={styles.statusText}>{resumo_ocupacao.hospitais_normal} Normal</Text>
          </View>
        </View>

        {/* Tendências */}
        <View style={styles.tendenciaSection}>
          <Text style={styles.tendenciaTitle}>Tendências (últimas 6h)</Text>
          <View style={styles.tendenciaRow}>
            <View style={styles.tendenciaItem}>
              <Text style={[styles.tendenciaIcon, { color: Colors.trendUp }]}>↑</Text>
              <Text style={styles.tendenciaValue}>{hospitaisTendenciaAlta}</Text>
              <Text style={styles.tendenciaLabel}>Subindo</Text>
            </View>
            
            <View style={styles.tendenciaItem}>
              <Text style={[styles.tendenciaIcon, { color: Colors.trendDown }]}>↓</Text>
              <Text style={styles.tendenciaValue}>{hospitaisTendenciaQueda}</Text>
              <Text style={styles.tendenciaLabel}>Caindo</Text>
            </View>
            
            {hospitaisComAlerta > 0 && (
              <View style={[styles.tendenciaItem, styles.alertaItem]}>
                <Text style={styles.tendenciaIcon}>⚠️</Text>
                <Text style={[styles.tendenciaValue, { color: Colors.danger }]}>
                  {hospitaisComAlerta}
                </Text>
                <Text style={[styles.tendenciaLabel, { color: Colors.danger }]}>
                  Alertas
                </Text>
              </View>
            )}
          </View>
        </View>
      </View>
      
      {/* Lista de Hospitais */}
      <ScrollView 
        horizontal 
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.hospitaisContainer}
      >
        {ocupacao_hospitais.map((hospital, index) => (
          <HospitalCard key={index} hospital={hospital} compact />
        ))}
      </ScrollView>

      {/* Legenda */}
      <View style={styles.legendaContainer}>
        <Text style={styles.legendaTitle}>Legenda de Tendências:</Text>
        <View style={styles.legendaRow}>
          <View style={styles.legendaItem}>
            <View style={[styles.legendaBorda, { backgroundColor: Colors.trendUp }]} />
            <Text style={styles.legendaText}>Alta</Text>
          </View>
          <View style={styles.legendaItem}>
            <View style={[styles.legendaBorda, { backgroundColor: Colors.trendDown }]} />
            <Text style={styles.legendaText}>Queda</Text>
          </View>
          <View style={styles.legendaItem}>
            <View style={[styles.legendaBorda, { backgroundColor: Colors.trendStable }]} />
            <Text style={styles.legendaText}>Estável</Text>
          </View>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { marginVertical: Spacing.lg },
  sectionTitle: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.primary,
    marginBottom: Spacing.md,
    paddingHorizontal: Spacing.lg,
  },
  resumoCard: {
    backgroundColor: Colors.surface,
    marginHorizontal: Spacing.lg,
    marginBottom: Spacing.md,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    ...Shadows.card,
  },
  resumoTitle: {
    fontSize: Typography.fontSize.md,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.textPrimary,
    marginBottom: Spacing.md,
    textAlign: 'center',
  },
  metricsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: Spacing.md,
  },
  metricItem: { alignItems: 'center', flex: 1 },
  metricValue: {
    fontSize: Typography.fontSize.xxl,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.primary,
  },
  metricLabel: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    textAlign: 'center',
    marginTop: Spacing.xs,
  },
  statusRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingTop: Spacing.md,
    borderTopWidth: 1,
    borderTopColor: Colors.divider,
  },
  statusItem: { flexDirection: 'row', alignItems: 'center' },
  statusDot: { width: 12, height: 12, borderRadius: 6, marginRight: Spacing.xs },
  statusText: { fontSize: Typography.fontSize.sm, color: Colors.textSecondary },
  tendenciaSection: {
    marginTop: Spacing.md,
    paddingTop: Spacing.md,
    borderTopWidth: 1,
    borderTopColor: Colors.divider,
  },
  tendenciaTitle: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.semiBold,
    color: Colors.textSecondary,
    marginBottom: Spacing.sm,
    textAlign: 'center',
  },
  tendenciaRow: { flexDirection: 'row', justifyContent: 'center', gap: Spacing.xl },
  tendenciaItem: { alignItems: 'center' },
  alertaItem: {
    backgroundColor: Colors.dangerLight,
    paddingHorizontal: Spacing.sm,
    paddingVertical: Spacing.xs,
    borderRadius: BorderRadius.md,
  },
  tendenciaIcon: { fontSize: Typography.fontSize.xl, fontWeight: Typography.fontWeight.bold },
  tendenciaValue: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.textPrimary,
  },
  tendenciaLabel: { fontSize: Typography.fontSize.xs, color: Colors.textMuted },
  hospitaisContainer: { paddingHorizontal: Spacing.md, paddingVertical: Spacing.sm },
  legendaContainer: {
    marginHorizontal: Spacing.lg,
    marginTop: Spacing.sm,
    padding: Spacing.md,
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.md,
    ...Shadows.card,
  },
  legendaTitle: {
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.semiBold,
    color: Colors.textSecondary,
    marginBottom: Spacing.sm,
  },
  legendaRow: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.md },
  legendaItem: { flexDirection: 'row', alignItems: 'center' },
  legendaBorda: { width: 16, height: 4, borderRadius: 2, marginRight: Spacing.xs },
  legendaText: { fontSize: Typography.fontSize.xs, color: Colors.textMuted },
});

export default OcupacaoHospitais;
