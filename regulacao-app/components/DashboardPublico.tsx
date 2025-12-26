import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, FlatList, Dimensions, TouchableOpacity, RefreshControl, Alert } from 'react-native';
import { Platform } from 'react-native';

const { width } = Dimensions.get('window');

// Configuração da API baseada na plataforma
const API_BASE_URL = Platform.select({
  web: 'http://localhost:8000',
  default: 'http://10.0.2.2:8000' // Android Emulator
});

const DashboardPublico = ({ dadosLeitos: initialData }) => {
  const [dadosLeitos, setDadosLeitos] = useState(initialData || []);
  const [refreshing, setRefreshing] = useState(false);
  const [statusSummary, setStatusSummary] = useState([]);
  const [lastUpdate, setLastUpdate] = useState(null);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/dashboard/leitos`);
      const data = await response.json();
      
      setDadosLeitos(data.unidades_pressao || []);
      setStatusSummary(data.status_summary || []);
      setLastUpdate(data.ultima_atualizacao);
    } catch (error) {
      console.error('Erro ao buscar dados:', error);
      Alert.alert('Erro', 'Não foi possível atualizar os dados');
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchDashboardData();
    setRefreshing(false);
  };

  useEffect(() => {
    // Buscar dados na inicialização se não tiver dados iniciais
    if (!initialData || initialData.length === 0) {
      fetchDashboardData();
    }
    
    // Atualizar a cada 5 minutos
    const interval = setInterval(fetchDashboardData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (count) => {
    if (count > 15) return '#F44336'; // Vermelho - Crítico
    if (count > 8) return '#FF9800';  // Laranja - Alto
    if (count > 3) return '#FFC107';  // Amarelo - Moderado
    return '#4CAF50'; // Verde - Normal
  };

  const getStatusText = (count) => {
    if (count > 15) return 'CRÍTICO';
    if (count > 8) return 'ALTO';
    if (count > 3) return 'MODERADO';
    return 'NORMAL';
  };

  const renderStatusSummary = () => (
    <View style={styles.summaryContainer}>
      <Text style={styles.summaryTitle}>Resumo da Rede SES-GO</Text>
      <View style={styles.summaryRow}>
        {statusSummary.map((item, index) => (
          <View key={index} style={styles.summaryCard}>
            <Text style={styles.summaryLabel}>{item.status.replace('_', ' ')}</Text>
            <Text style={styles.summaryValue}>{item.count}</Text>
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

  const renderCard = ({ item }) => {
    const statusColor = getStatusColor(item.pacientes_em_fila);
    const statusText = getStatusText(item.pacientes_em_fila);
    
    return (
      <TouchableOpacity style={styles.card} activeOpacity={0.7}>
        <View style={styles.cardHeader}>
          <Text style={styles.hospitalTitle} numberOfLines={2}>
            {item.unidade_executante_desc}
          </Text>
          <View style={[styles.statusBadge, { backgroundColor: statusColor }]}>
            <Text style={styles.statusBadgeText}>{statusText}</Text>
          </View>
        </View>
        
        <View style={styles.cardContent}>
          <View style={styles.metric}>
            <Text style={styles.label}>Pacientes em Fila</Text>
            <Text style={[styles.value, { color: statusColor }]}>
              {item.pacientes_em_fila}
            </Text>
          </View>
          
          {item.cidade && (
            <View style={styles.locationContainer}>
              <Text style={styles.locationText}>📍 {item.cidade}</Text>
            </View>
          )}
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>SES-GO | Regulação Autônoma</Text>
        <Text style={styles.headerSubtitle}>Monitoramento em Tempo Real</Text>
        {lastUpdate && (
          <Text style={styles.lastUpdate}>
            Atualizado: {new Date(lastUpdate).toLocaleTimeString('pt-BR')}
          </Text>
        )}
      </View>
      
      <FlatList
        data={dadosLeitos}
        renderItem={renderCard}
        keyExtractor={(item, index) => `${item.unidade_executante_desc}-${index}`}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListHeaderComponent={statusSummary.length > 0 ? renderStatusSummary : null}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F5F7FA' },
  header: { 
    padding: 20, 
    backgroundColor: '#004A8D',
    borderBottomLeftRadius: 15, 
    borderBottomRightRadius: 15,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
  },
  headerTitle: { 
    color: '#FFF', 
    fontSize: 20, 
    fontWeight: 'bold',
    textAlign: 'center'
  },
  headerSubtitle: {
    color: '#E3F2FD',
    fontSize: 14,
    textAlign: 'center',
    marginTop: 4
  },
  lastUpdate: {
    color: '#E3F2FD',
    fontSize: 12,
    textAlign: 'center',
    marginTop: 8
  },
  summaryContainer: {
    backgroundColor: '#FFF',
    margin: 15,
    padding: 16,
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
  },
  summaryTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-around'
  },
  summaryCard: {
    alignItems: 'center',
    flex: 1
  },
  summaryLabel: {
    fontSize: 11,
    color: '#666',
    textAlign: 'center'
  },
  summaryValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#004A8D',
    marginTop: 4
  },
  summaryFooter: {
    fontSize: 10,
    color: '#999',
    textAlign: 'center',
    marginTop: 8,
    fontStyle: 'italic'
  },
  list: { 
    padding: 15,
    paddingTop: 0
  },
  card: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12
  },
  hospitalTitle: { 
    fontSize: 14, 
    fontWeight: '600', 
    color: '#333',
    flex: 1,
    marginRight: 8
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    minWidth: 60,
    alignItems: 'center'
  },
  statusBadgeText: {
    color: '#FFF',
    fontSize: 10,
    fontWeight: 'bold'
  },
  cardContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  metric: {
    flex: 1
  },
  label: { 
    fontSize: 12, 
    color: '#666',
    marginBottom: 4
  },
  value: { 
    fontSize: 24, 
    fontWeight: 'bold'
  },
  locationContainer: {
    flex: 1,
    alignItems: 'flex-end'
  },
  locationText: {
    fontSize: 12,
    color: '#666'
  }
});

export default DashboardPublico;
