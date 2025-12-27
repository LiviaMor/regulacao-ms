/**
 * Tela de Auditoria Pública - PAIC-REGULA
 * 
 * Exibe o dashboard de auditoria com métricas de transparência
 * Atende ao critério de IA Aberta do edital FAPEG
 */

import React from 'react';
import { View, StyleSheet } from 'react-native';
import DashboardAuditoria from '../../components/DashboardAuditoria';
import { Colors } from '../../constants/theme';

export default function AuditoriaScreen() {
  return (
    <View style={styles.container}>
      <DashboardAuditoria />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
});
