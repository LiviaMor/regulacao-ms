/**
 * OCUPACAO DE HOSPITAIS - Dashboard de Leitos
 * Sistema de Regulacao Autonoma SES-GO
 * 
 * Exibe ocupacao com indicadores de tendencia do MS-Ingestao
 * Carrossel animado para hospitais de grande complexidade
 */

import React, { useEffect, useRef, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Animated,
  Dimensions,
} from 'react-native';
import { 
  Colors, 
  Typography, 
  BorderRadius, 
  Shadows, 
  Spacing,
} from '@/constants/theme';
import HospitalCard, { HospitalData } from './ui/HospitalCard';

const { width: SCREEN_WIDTH } = Dimensions.get('window');
const CARD_WIDTH = 280;
const CARD_MARGIN = 12;
const SCROLL_SPEED = 50; // pixels por segundo

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
  const scrollX = useRef(new Animated.Value(0)).current;
  const scrollViewRef = useRef<ScrollView>(null);
  const [contentWidth, setContentWidth] = useState(0);
  
  const hospitaisTendenciaAlta = ocupacao_hospitais.filter(h => h.tendencia === 'ALTA').length;
  const hospitaisTendenciaQueda = ocupacao_hospitais.filter(h => h.tendencia === 'QUEDA').length;
  const hospitaisComAlerta = ocupacao_hospitais.filter(h => h.alerta_saturacao).length;

  // Separar hospitais de grande complexidade (HUGO, HUGOL, HGG, etc.)
  const hospitaisGrandeComplexidade = ocupacao_hospitais.filter(h => 
    h.tipo === 'Urgencia' || h.tipo === 'Geral' || 
    (h.sigla && ['HUGO', 'HUGOL', 'HGG', 'HEMU', 'HECAD'].includes(h.sigla))
  );

  const hospitaisRegionais = ocupacao_hospitais.filter(h => 
    h.tipo === 'Regional' || 
    (h.sigla && !['HUGO', 'HUGOL', 'HGG', 'HEMU', 'HECAD'].includes(h.sigla))
  );

  // Animacao do carrossel - scroll automatico da direita para esquerda
  useEffect(() => {
    if (hospitaisGrandeComplexidade.length <= 1) return;

    const totalWidth = hospitaisGrandeComplexidade.length * (CARD_WIDTH + CARD_MARGIN);
    setContentWidth(totalWidth);

    let scrollPosition = 0;
    const interval = setInterval(() => {
      scrollPosition += 1;
      if (scrollPosition >= totalWidth - SCREEN_WIDTH + 40) {
        scrollPosition = 0;
      }
      scrollViewRef.current?.scrollTo({ x: scrollPosition, animated: false });
    }, 1000 / SCROLL_SPEED);

    return () => clearInterval(interval);
  }, [hospitaisGrandeComplexidade.length]);

  return (
    <View style={styles.container}>
      <Text style={styles.sectionTitle}>Ocupacao de Leitos - Rede Estadual</Text>
      
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
            <Text style={styles.metricLabel}>Disponiveis</Text>
          </View>
          
          <View style={styles.metricItem}>
            <Text style={[styles.metricValue, { color: Colors.primary }]}>
              {resumo_ocupacao.taxa_media}%
            </Text>
            <Text style={styles.metricLabel}>Taxa Media</Text>
          </View>
        </View>

        <View style={styles.statusRow}>
          <View style={styles.statusItem}>
            <View style={[styles.statusDot, { backgroundColor: Colors.danger }]} />
            <Text style={styles.statusText}>{resumo_ocupacao.hospitais_criticos} Criticos</Text>
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

        {/* Tendencias */}
        <View style={styles.tendenciaSection}>
          <Text style={styles.tendenciaTitle}>Tendencias (ultimas 6h)</Text>
          <View style={styles.tendenciaRow}>
            <View style={styles.tendenciaItem}>
              <View style={[styles.trendIndicator, { backgroundColor: Colors.trendUp }]}>
                <Text style={styles.trendArrow}>↑</Text>
              </View>
              <Text style={styles.tendenciaValue}>{hospitaisTendenciaAlta}</Text>
              <Text style={styles.tendenciaLabel}>Subindo</Text>
            </View>
            
            <View style={styles.tendenciaItem}>
              <View style={[styles.trendIndicator, { backgroundColor: Colors.trendDown }]}>
                <Text style={styles.trendArrow}>↓</Text>
              </View>
              <Text style={styles.tendenciaValue}>{hospitaisTendenciaQueda}</Text>
              <Text style={styles.tendenciaLabel}>Caindo</Text>
            </View>
            
            {hospitaisComAlerta > 0 && (
              <View style={[styles.tendenciaItem, styles.alertaItem]}>
                <View style={[styles.trendIndicator, { backgroundColor: Colors.danger }]}>
                  <Text style={styles.trendArrow}>!</Text>
                </View>
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

      {/* Carrossel de Hospitais de Grande Complexidade */}
      {hospitaisGrandeComplexidade.length > 0 && (
        <View style={styles.carrosselSection}>
          <View style={styles.carrosselHeader}>
            <Text style={styles.carrosselTitle}>Hospitais de Grande Complexidade</Text>
            <View style={styles.autoScrollBadge}>
              <Text style={styles.autoScrollText}>AUTO</Text>
            </View>
          </View>
          <ScrollView 
            ref={scrollViewRef}
            horizontal 
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.hospitaisContainer}
            scrollEventThrottle={16}
          >
            {hospitaisGrandeComplexidade.map((hospital, index) => (
              <View key={`grande-${index}`} style={styles.cardWrapper}>
                <HospitalCard hospital={hospital} compact />
              </View>
            ))}
          </ScrollView>
        </View>
      )}

      {/* Lista de Hospitais Regionais */}
      {hospitaisRegionais.length > 0 && (
        <View style={styles.regionaisSection}>
          <Text style={styles.regionaisTitle}>Hospitais Regionais</Text>
          <ScrollView 
            horizontal 
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.hospitaisContainer}
          >
            {hospitaisRegionais.map((hospital, index) => (
              <View key={`regional-${index}`} style={styles.cardWrapper}>
                <HospitalCard hospital={hospital} compact />
              </View>
            ))}
          </ScrollView>
        </View>
      )}

      {/* Legenda */}
      <View style={styles.legendaContainer}>
        <Text style={styles.legendaTitle}>Legenda de Tendencias:</Text>
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
            <Text style={styles.legendaText}>Estavel</Text>
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
  trendIndicator: {
    width: 28,
    height: 28,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 4,
  },
  trendArrow: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  tendenciaValue: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.textPrimary,
  },
  tendenciaLabel: { fontSize: Typography.fontSize.xs, color: Colors.textMuted },
  
  // Carrossel
  carrosselSection: {
    marginTop: Spacing.md,
  },
  carrosselHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: Spacing.lg,
    marginBottom: Spacing.sm,
  },
  carrosselTitle: {
    fontSize: Typography.fontSize.md,
    fontWeight: Typography.fontWeight.semiBold,
    color: Colors.textPrimary,
  },
  autoScrollBadge: {
    backgroundColor: Colors.primary,
    paddingHorizontal: Spacing.sm,
    paddingVertical: 2,
    borderRadius: BorderRadius.sm,
  },
  autoScrollText: {
    color: '#FFF',
    fontSize: 10,
    fontWeight: 'bold',
  },
  
  // Regionais
  regionaisSection: {
    marginTop: Spacing.lg,
  },
  regionaisTitle: {
    fontSize: Typography.fontSize.md,
    fontWeight: Typography.fontWeight.semiBold,
    color: Colors.textPrimary,
    paddingHorizontal: Spacing.lg,
    marginBottom: Spacing.sm,
  },
  
  hospitaisContainer: { paddingHorizontal: Spacing.md, paddingVertical: Spacing.sm },
  cardWrapper: {
    marginRight: CARD_MARGIN,
  },
  
  legendaContainer: {
    marginHorizontal: Spacing.lg,
    marginTop: Spacing.md,
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
