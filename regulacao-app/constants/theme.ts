/**
 * TEMA INSTITUCIONAL SES-GO
 * Sistema de Regulação Autônoma
 * 
 * Paleta de cores, tipografia e estilos padronizados
 */

export const Colors = {
  // Cores Primárias Institucionais
  primary: '#004A8D',           // Azul Institucional SES-GO
  primaryDark: '#003366',       // Azul Escuro
  primaryLight: '#E3F2FD',      // Azul Claro (backgrounds)
  
  // Cores de Ação
  success: '#2E7D32',           // Verde Saúde - Ações positivas
  successLight: '#E8F5E9',      // Verde Claro
  warning: '#F57C00',           // Laranja - Alertas
  warningLight: '#FFF3E0',      // Laranja Claro
  danger: '#D32F2F',            // Vermelho - Crítico
  dangerLight: '#FFEBEE',       // Vermelho Claro
  
  // Classificação de Risco (Manchester)
  riskRed: '#D32F2F',           // Emergência
  riskOrange: '#F57C00',        // Muito Urgente
  riskYellow: '#FBC02D',        // Urgente
  riskGreen: '#388E3C',         // Pouco Urgente
  riskBlue: '#1976D2',          // Não Urgente
  
  // Tendências (MS-Ingestao)
  trendUp: '#D32F2F',           // Tendência de ALTA (vermelho)
  trendDown: '#2E7D32',         // Tendência de QUEDA (verde)
  trendStable: '#757575',       // Tendência ESTÁVEL (cinza)
  
  // Neutros
  background: '#F8F9FA',        // Fundo principal (cinza ultra-claro)
  surface: '#FFFFFF',           // Cards e superfícies
  border: '#E0E0E0',            // Bordas
  divider: '#EEEEEE',           // Divisores
  
  // Texto
  textPrimary: '#212121',       // Texto principal
  textSecondary: '#666666',     // Texto secundário
  textMuted: '#9E9E9E',         // Texto desabilitado
  textOnPrimary: '#FFFFFF',     // Texto sobre cor primária
  textOnDark: '#FFFFFF',        // Texto sobre fundo escuro
  
  // Detalhe Governamental
  gold: '#FFD700',              // Detalhe dourado (brasões)
};

export const Typography = {
  // Família de fontes
  fontFamily: {
    regular: 'Inter_400Regular',
    medium: 'Inter_500Medium',
    semiBold: 'Inter_600SemiBold',
    bold: 'Inter_700Bold',
    // Fallbacks
    fallback: 'System',
  },
  
  // Tamanhos
  fontSize: {
    xs: 10,
    sm: 12,
    md: 14,
    lg: 16,
    xl: 18,
    xxl: 20,
    xxxl: 24,
    display: 32,
  },
  
  // Pesos
  fontWeight: {
    regular: '400' as const,
    medium: '500' as const,
    semiBold: '600' as const,
    bold: '700' as const,
  },
  
  // Espaçamento de letras
  letterSpacing: {
    tight: -0.5,
    normal: 0,
    wide: 0.5,
    wider: 1,
  },
  
  // Altura de linha
  lineHeight: {
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.75,
  },
};

export const Spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  xxl: 24,
  xxxl: 32,
};

export const BorderRadius = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  full: 9999,
};

export const Shadows = {
  // Sombra sutil para cards
  card: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  
  // Sombra média
  medium: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  
  // Sombra forte (modais, toasts)
  strong: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.15,
    shadowRadius: 16,
    elevation: 8,
  },
};

// Função helper para cor de tendência
export const getTrendColor = (trend: 'ALTA' | 'QUEDA' | 'ESTAVEL' | string): string => {
  switch (trend) {
    case 'ALTA': return Colors.trendUp;
    case 'QUEDA': return Colors.trendDown;
    case 'ESTAVEL': return Colors.trendStable;
    default: return Colors.textMuted;
  }
};

// Função helper para cor de risco
export const getRiskColor = (risk: 'VERMELHO' | 'AMARELO' | 'VERDE' | string): string => {
  switch (risk) {
    case 'VERMELHO': return Colors.riskRed;
    case 'AMARELO': return Colors.riskOrange;
    case 'VERDE': return Colors.riskGreen;
    default: return Colors.textMuted;
  }
};

// Função helper para cor de status de ocupação
export const getOccupancyColor = (status: 'CRITICO' | 'ALTO' | 'MODERADO' | 'NORMAL' | string): string => {
  switch (status) {
    case 'CRITICO': return Colors.danger;
    case 'ALTO': return Colors.warning;
    case 'MODERADO': return Colors.riskYellow;
    case 'NORMAL': return Colors.success;
    default: return Colors.textMuted;
  }
};

export default {
  Colors,
  Typography,
  Spacing,
  BorderRadius,
  Shadows,
  getTrendColor,
  getRiskColor,
  getOccupancyColor,
};
