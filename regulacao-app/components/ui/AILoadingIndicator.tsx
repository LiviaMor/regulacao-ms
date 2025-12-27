/**
 * AI LOADING INDICATOR - Indicador de Processamento IA
 * Sistema de Regulação Autônoma SES-GO
 * 
 * Exibe animação durante processamento BioBERT/Llama
 */

import React, { useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
  Easing,
} from 'react-native';
import { Colors, Typography, BorderRadius, Shadows, Spacing } from '@/constants/theme';

interface AILoadingIndicatorProps {
  visible: boolean;
  message?: string;
  subMessage?: string;
}

const AILoadingIndicator: React.FC<AILoadingIndicatorProps> = ({
  visible,
  message = 'Processando com IA...',
  subMessage = 'BioBERT + Llama analisando dados',
}) => {
  const rotation = useRef(new Animated.Value(0)).current;
  const pulse = useRef(new Animated.Value(1)).current;
  const dots = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (visible) {
      // Animação de rotação
      const rotationAnimation = Animated.loop(
        Animated.timing(rotation, {
          toValue: 1,
          duration: 2000,
          easing: Easing.linear,
          useNativeDriver: true,
        })
      );

      // Animação de pulso
      const pulseAnimation = Animated.loop(
        Animated.sequence([
          Animated.timing(pulse, {
            toValue: 1.2,
            duration: 800,
            easing: Easing.inOut(Easing.ease),
            useNativeDriver: true,
          }),
          Animated.timing(pulse, {
            toValue: 1,
            duration: 800,
            easing: Easing.inOut(Easing.ease),
            useNativeDriver: true,
          }),
        ])
      );

      rotationAnimation.start();
      pulseAnimation.start();

      return () => {
        rotationAnimation.stop();
        pulseAnimation.stop();
      };
    }
  }, [visible]);

  if (!visible) return null;

  const spin = rotation.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  });

  return (
    <View style={styles.overlay}>
      <View style={styles.container}>
        {/* Ícone animado de IA */}
        <Animated.View
          style={[
            styles.iconContainer,
            {
              transform: [{ rotate: spin }, { scale: pulse }],
            },
          ]}
        >
          <View style={styles.iconInner}>
            <Text style={styles.iconText}>🧠</Text>
          </View>
          
          {/* Círculos orbitais */}
          <View style={[styles.orbit, styles.orbit1]} />
          <View style={[styles.orbit, styles.orbit2]} />
        </Animated.View>

        {/* Mensagens */}
        <Text style={styles.message}>{message}</Text>
        <Text style={styles.subMessage}>{subMessage}</Text>

        {/* Barra de progresso indeterminada */}
        <View style={styles.progressContainer}>
          <Animated.View
            style={[
              styles.progressBar,
              {
                transform: [
                  {
                    translateX: rotation.interpolate({
                      inputRange: [0, 1],
                      outputRange: [-100, 200],
                    }),
                  },
                ],
              },
            ]}
          />
        </View>

        {/* Indicadores de serviços */}
        <View style={styles.servicesContainer}>
          <View style={styles.serviceItem}>
            <View style={[styles.serviceDot, { backgroundColor: Colors.success }]} />
            <Text style={styles.serviceText}>BioBERT</Text>
          </View>
          <View style={styles.serviceItem}>
            <View style={[styles.serviceDot, { backgroundColor: Colors.primary }]} />
            <Text style={styles.serviceText}>Matchmaker</Text>
          </View>
          <View style={styles.serviceItem}>
            <View style={[styles.serviceDot, { backgroundColor: Colors.warning }]} />
            <Text style={styles.serviceText}>Pipeline GO</Text>
          </View>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  overlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 9999,
  },
  container: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.xxl,
    alignItems: 'center',
    marginHorizontal: Spacing.xl,
    ...Shadows.strong,
  },
  iconContainer: {
    width: 80,
    height: 80,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: Spacing.lg,
  },
  iconInner: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: Colors.primaryLight,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 3,
    borderColor: Colors.primary,
  },
  iconText: {
    fontSize: 28,
  },
  orbit: {
    position: 'absolute',
    borderWidth: 2,
    borderColor: Colors.primary,
    borderStyle: 'dashed',
    borderRadius: 100,
    opacity: 0.3,
  },
  orbit1: {
    width: 70,
    height: 70,
  },
  orbit2: {
    width: 90,
    height: 90,
  },
  message: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.textPrimary,
    marginBottom: Spacing.xs,
    textAlign: 'center',
  },
  subMessage: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textSecondary,
    marginBottom: Spacing.lg,
    textAlign: 'center',
  },
  progressContainer: {
    width: '100%',
    height: 4,
    backgroundColor: Colors.border,
    borderRadius: 2,
    overflow: 'hidden',
    marginBottom: Spacing.lg,
  },
  progressBar: {
    width: 100,
    height: '100%',
    backgroundColor: Colors.primary,
    borderRadius: 2,
  },
  servicesContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: Spacing.lg,
  },
  serviceItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  serviceDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: Spacing.xs,
  },
  serviceText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    fontWeight: Typography.fontWeight.medium,
  },
});

export default AILoadingIndicator;
