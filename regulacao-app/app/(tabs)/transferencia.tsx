import React from 'react';
import { View, StyleSheet } from 'react-native';
import AreaTransferencia from '@/components/AreaTransferencia';

export default function TransferenciaScreen() {
  return (
    <View style={styles.container}>
      <AreaTransferencia />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F7FA',
  },
});