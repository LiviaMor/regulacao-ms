/**
 * HEADER GOVERNAMENTAL MODERNO
 * Sistema de Regulação Autônoma SES-GO
 * 
 * Logo à esquerda, título à direita
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  Image,
  Platform,
  StatusBar,
} from 'react-native';
import { Colors, Typography, Spacing } from '@/constants/theme';

interface HeaderProps {
  title: string;
  subtitle?: string;
  showLogo?: boolean;
  rightComponent?: React.ReactNode;
}

const Header: React.FC<HeaderProps> = ({
  title,
  subtitle,
  showLogo = true,
  rightComponent,
}) => {
  const statusBarHeight = Platform.OS === 'ios' ? 44 : StatusBar.currentHeight || 0;

  return (
    <View style={[styles.container, { paddingTop: statusBarHeight + Spacing.md }]}>
      {/* Linha dourada superior (detalhe governamental) */}
      <View style={styles.goldLine} />
      
      <View style={styles.content}>
        {/* Logo à esquerda */}
        {showLogo && (
          <View style={styles.logoContainer}>
            <Image
              source={require('@/assets/images/logo_normal.png')}
              style={styles.logo}
              resizeMode="contain"
            />
          </View>
        )}
        
        {/* Título e subtítulo à direita */}
        <View style={styles.titleContainer}>
          <Text style={styles.title} numberOfLines={1}>
            {title}
          </Text>
          {subtitle && (
            <Text style={styles.subtitle} numberOfLines={1}>
              {subtitle}
            </Text>
          )}
        </View>
        
        {/* Componente opcional à direita */}
        {rightComponent && (
          <View style={styles.rightContainer}>
            {rightComponent}
          </View>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: Colors.primary,
    paddingBottom: Spacing.lg,
  },
  goldLine: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: 3,
    backgroundColor: Colors.gold,
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: Spacing.lg,
  },
  logoContainer: {
    marginRight: Spacing.md,
  },
  logo: {
    width: 80,
    height: 80,
  },
  titleContainer: {
    flex: 1,
  },
  title: {
    color: Colors.textOnPrimary,
    fontSize: Typography.fontSize.xl,
    fontWeight: Typography.fontWeight.bold,
    letterSpacing: Typography.letterSpacing.wide,
  },
  subtitle: {
    color: Colors.primaryLight,
    fontSize: Typography.fontSize.sm,
    marginTop: 2,
    letterSpacing: Typography.letterSpacing.wide,
  },
  rightContainer: {
    marginLeft: Spacing.md,
  },
});

export default Header;
