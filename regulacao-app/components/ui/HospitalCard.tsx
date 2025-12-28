/**
 * HOSPITAL CARD - Card de Hospital com Tendência
 * Sistema de Regulação Autônoma SES-GO
 * 
 * Exibe ocupação com indicador de tendência na borda esquerda
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
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

const { width } = Dimensions.get('window');

export interface HospitalData {
  hospital: string;
  sigla: string;
  cidade: string;
  tipo: string;
  leitos_totais: number;
  leitos_ocupados: number;
  leitos_disponiveis: number;
  taxa_ocupacao: number;
  status_ocupacao: 'CRITICO' | 'ALTO' | 'MODERADO' | 'NORMAL';
  especialidades: string[];
  ultima_atualizacao: string;
  // Dados de tendência (MS-Ingestao)
  tendencia?: 'ALTA' | 'QUEDA' | 'ESTAVEL';
  variacao_6h?: number;
  alerta_saturacao?: boolean;
  previsao_saturacao_min?: number;
  mensagem_ia?: string;
}

interface HospitalCardProps {
  hospital: HospitalData;
  onPress?: () => void;
  compact?: boolean;
}

const HospitalCard: React.FC<HospitalCardProps> = ({
  hospital,
  onPress,
  compact = false,
}) => {
  const trendColor = getTrendColor(hospital.tendencia || 'ESTAVEL');
  const occupancyColor = getOccupancyColor(hospital.status_ocupacao);

  const getTrendIcon = () => {
    switch (hospital.tendencia) {
      case 'ALTA': return '↑';
      case 'QUEDA': return '↓';
      case 'ESTAVEL': return '→';
      default: return '•';
    }
  };

  const getTrendLabel = () => {
    switch (hospital.tendencia) {
      case 'ALTA': return 'Subindo';
      case 'QUEDA': return 'Caindo';
      case 'ESTAVEL': return 'Estável';
      default: return '';
    }
  };

  return (
    <TouchableOpacity
      style={[
        styles.card,
        { borderLeftColor: trendColor },
        compact && styles.cardCompact,
      ]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      {/* Alerta de Saturação */}
      {hospital.alerta_saturacao && (
        <View style={styles.alertBanner}>
          <Text style={styles.alertText}>
            ALERTA: Saturacao prevista em {hospital.previsao_saturacao_min}min
          </Text>
        </View>
      )}

      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <Text style={styles.sigla}>{hospital.sigla}</Text>
          <Text style={styles.cidade}>{hospital.cidade}</Text>
        </View>
        
        <View style={[styles.statusBadge, { backgroundColor: occupancyColor }]}>
          <Text style={styles.statusText}>{hospital.status_ocupacao}</Text>
        </View>
      </View>

      {/* Nome completo */}
      {!compact && (
        <Text style={styles.nomeCompleto} numberOfLines={2}>
          {hospital.hospital}
        </Text>
      )}

      {/* Ocupação */}
      <View style={styles.ocupacaoContainer}>
        <View style={styles.ocupacaoHeader}>
          <Text style={styles.ocupacaoLabel}>Ocupação</Text>
          <Text style={[styles.ocupacaoValue, { color: occupancyColor }]}>
            {hospital.taxa_ocupacao.toFixed(1)}%
          </Text>
        </View>
        
        {/* Barra de progresso */}
        <View style={styles.progressContainer}>
          <View
            style={[
              styles.progressBar,
              {
                width: `${Math.min(hospital.taxa_ocupacao, 100)}%`,
                backgroundColor: occupancyColor,
              },
            ]}
          />
        </View>
        
        {/* Leitos */}
        <View style={styles.leitosRow}>
          <Text style={styles.leitosText}>
            {hospital.leitos_ocupados}/{hospital.leitos_totais} ocupados
          </Text>
          <Text style={[styles.leitosDisponiveis, { color: Colors.success }]}>
            {hospital.leitos_disponiveis} disponíveis
          </Text>
        </View>
      </View>

      {/* Tendência */}
      {hospital.tendencia && (
        <View style={styles.tendenciaContainer}>
          <View style={[styles.tendenciaBadge, { backgroundColor: `${trendColor}15` }]}>
            <Text style={[styles.tendenciaIcon, { color: trendColor }]}>
              {getTrendIcon()}
            </Text>
            <Text style={[styles.tendenciaText, { color: trendColor }]}>
              {getTrendLabel()}
            </Text>
            {hospital.variacao_6h !== undefined && (
              <Text style={[styles.tendenciaVariacao, { color: trendColor }]}>
                ({hospital.variacao_6h > 0 ? '+' : ''}{hospital.variacao_6h.toFixed(1)}% em 6h)
              </Text>
            )}
          </View>
        </View>
      )}

      {/* Especialidades */}
      {!compact && hospital.especialidades && (
        <View style={styles.especialidadesContainer}>
          <View style={styles.especialidadesTags}>
            {hospital.especialidades.slice(0, 3).map((esp, idx) => (
              <View key={idx} style={styles.especialidadeTag}>
                <Text style={styles.especialidadeText}>
                  {esp.replace(/_/g, ' ')}
                </Text>
              </View>
            ))}
            {hospital.especialidades.length > 3 && (
              <View style={[styles.especialidadeTag, styles.especialidadeMore]}>
                <Text style={styles.especialidadeText}>
                  +{hospital.especialidades.length - 3}
                </Text>
              </View>
            )}
          </View>
        </View>
      )}

      {/* Footer */}
      <View style={styles.footer}>
        <Text style={styles.tipoText}>{hospital.tipo}</Text>
        <Text style={styles.atualizacaoText}>
          Atualizado às {hospital.ultima_atualizacao}
        </Text>
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    marginVertical: Spacing.sm,
    marginHorizontal: Spacing.lg,
    borderLeftWidth: 6,
    ...Shadows.card,
  },
  cardCompact: {
    width: width * 0.75,
    marginHorizontal: Spacing.sm,
  },
  alertBanner: {
    backgroundColor: Colors.dangerLight,
    marginHorizontal: -Spacing.lg,
    marginTop: -Spacing.lg,
    marginBottom: Spacing.md,
    padding: Spacing.sm,
    borderTopLeftRadius: BorderRadius.lg,
    borderTopRightRadius: BorderRadius.lg,
  },
  alertText: {
    color: Colors.danger,
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.bold,
    textAlign: 'center',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: Spacing.sm,
  },
  headerLeft: {
    flex: 1,
  },
  sigla: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.primary,
  },
  cidade: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textSecondary,
    marginTop: 2,
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
  },
  nomeCompleto: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textSecondary,
    marginBottom: Spacing.md,
    lineHeight: Typography.fontSize.sm * Typography.lineHeight.normal,
  },
  ocupacaoContainer: {
    marginBottom: Spacing.md,
  },
  ocupacaoHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.xs,
  },
  ocupacaoLabel: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textSecondary,
    fontWeight: Typography.fontWeight.medium,
  },
  ocupacaoValue: {
    fontSize: Typography.fontSize.xl,
    fontWeight: Typography.fontWeight.bold,
  },
  progressContainer: {
    height: 8,
    backgroundColor: Colors.border,
    borderRadius: BorderRadius.sm,
    marginBottom: Spacing.xs,
    overflow: 'hidden',
  },
  progressBar: {
    height: '100%',
    borderRadius: BorderRadius.sm,
  },
  leitosRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  leitosText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
  },
  leitosDisponiveis: {
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.semiBold,
  },
  tendenciaContainer: {
    marginBottom: Spacing.md,
  },
  tendenciaBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    paddingHorizontal: Spacing.sm,
    paddingVertical: Spacing.xs,
    borderRadius: BorderRadius.full,
  },
  tendenciaIcon: {
    fontSize: Typography.fontSize.md,
    fontWeight: Typography.fontWeight.bold,
    marginRight: Spacing.xs,
  },
  tendenciaText: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.semiBold,
  },
  tendenciaVariacao: {
    fontSize: Typography.fontSize.xs,
    marginLeft: Spacing.xs,
  },
  especialidadesContainer: {
    marginBottom: Spacing.md,
  },
  especialidadesTags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.xs,
  },
  especialidadeTag: {
    backgroundColor: Colors.primaryLight,
    paddingHorizontal: Spacing.sm,
    paddingVertical: Spacing.xs,
    borderRadius: BorderRadius.full,
  },
  especialidadeMore: {
    backgroundColor: Colors.border,
  },
  especialidadeText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.primary,
    fontWeight: Typography.fontWeight.medium,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: Spacing.sm,
    borderTopWidth: 1,
    borderTopColor: Colors.divider,
  },
  tipoText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    fontStyle: 'italic',
  },
  atualizacaoText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
  },
});

export default HospitalCard;
