/**
 * Tela de Auditoria - PAIC-REGULA
 * 
 * Conforme DIAGRAMA_FLUXO_COMPLETO.md:
 * - Usuários logados (REGULADOR/ADMIN/AUDITOR): Área de Auditoria com gestão de altas
 * - Usuários não logados: Dashboard público de transparência
 * 
 * Fluxo: ADMITIDO → (registra alta) → ALTA
 */

import React, { useState, useEffect } from 'react';
import { View, StyleSheet, Platform } from 'react-native';
import DashboardAuditoria from '../../components/DashboardAuditoria';
import AreaAuditoria from '../../components/AreaAuditoria';
import { Colors } from '../../constants/theme';

export default function AuditoriaScreen() {
  const [userToken, setUserToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Verificar se há token salvo
        if (Platform.OS === 'web') {
          const token = localStorage.getItem('userToken');
          setUserToken(token);
        } else {
          // Para mobile, usar AsyncStorage (importar se necessário)
          // Por enquanto, usar null para mostrar dashboard público
          setUserToken(null);
        }
      } catch (error) {
        console.error('Erro ao verificar autenticação:', error);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  if (loading) {
    return <View style={styles.container} />;
  }

  return (
    <View style={styles.container}>
      {userToken ? (
        // Usuário logado: Área de Auditoria com gestão de altas
        <AreaAuditoria userToken={userToken} />
      ) : (
        // Usuário não logado: Dashboard público de transparência
        <DashboardAuditoria />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
});
