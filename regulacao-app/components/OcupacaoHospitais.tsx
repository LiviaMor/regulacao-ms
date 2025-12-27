import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Dimensions
} from 'react-native';

const { width } = Dimensions.get('window');

interface Hospital {
  hospital: string;
  sigla: string;
  cidade: string;
  tipo: string;
  leitos_totais: number;
  leitos_ocupados: number;
  leitos_disponiveis: number;
  taxa_ocupacao: number;
  status_ocupacao: 'CRITICO' | 'ALTO' | 'MODERADO' | 'NORMAL';
  cor_status: string;
  especialidades: string[];
  ultima_atualizacao: string;
}

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
  ocupacao_hospitais: Hospital[];
  resumo_ocupacao: ResumoOcupacao;
}

const OcupacaoHospitais: React.FC<OcupacaoHospitaisProps> = ({ 
  ocupacao_hospitais, 
  resumo_ocupacao 
}) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'CRITICO': return 'CRÍTICO';
      case 'ALTO': return 'ALTO';
      case 'MODERADO': return 'MODERADO';
      case 'NORMAL': return 'NORMAL';
      default: return 'N/A';
    }
  };

  const getTipoIcon = (tipo: string) => {
    switch (tipo) {
      case 'Urgência': return 'URG';
      case 'Geral': return 'GER';
      case 'Materno-Infantil': return 'MAT';
      case 'Pediátrico': return 'PED';
      case 'Regional': return 'REG';
      default: return 'HOS';
    }
  };

  const renderResumoCard = () => (
    <View style={styles.resumoCard}>
      <Text style={styles.resumoTitle}>Resumo da Rede Estadual</Text>
      
      <View style={styles.resumoGrid}>
        <View style={styles.resumoItem}>
          <Text style={styles.resumoNumber}>{resumo_ocupacao.total_leitos}</Text>
          <Text style={styles.resumoLabel}>Total de Leitos</Text>
        </View>
        
        <View style={styles.resumoItem}>
          <Text style={[styles.resumoNumber, { color: '#F57C00' }]}>
            {resumo_ocupacao.total_ocupados}
          </Text>
          <Text style={styles.resumoLabel}>Ocupados</Text>
        </View>
        
        <View style={styles.resumoItem}>
          <Text style={[styles.resumoNumber, { color: '#4CAF50' }]}>
            {resumo_ocupacao.total_disponiveis}
          </Text>
          <Text style={styles.resumoLabel}>Disponíveis</Text>
        </View>
        
        <View style={styles.resumoItem}>
          <Text style={[styles.resumoNumber, { color: '#2196F3' }]}>
            {resumo_ocupacao.taxa_media}%
          </Text>
          <Text style={styles.resumoLabel}>Taxa Média</Text>
        </View>
      </View>

      <View style={styles.statusResumo}>
        <View style={styles.statusItem}>
          <View style={[styles.statusIndicator, { backgroundColor: '#D32F2F' }]} />
          <Text style={styles.statusText}>{resumo_ocupacao.hospitais_criticos} Críticos</Text>
        </View>
        
        <View style={styles.statusItem}>
          <View style={[styles.statusIndicator, { backgroundColor: '#F57C00' }]} />
          <Text style={styles.statusText}>{resumo_ocupacao.hospitais_alto} Alto</Text>
        </View>
        
        <View style={styles.statusItem}>
          <View style={[styles.statusIndicator, { backgroundColor: '#4CAF50' }]} />
          <Text style={styles.statusText}>{resumo_ocupacao.hospitais_normal} Normal</Text>
        </View>
      </View>
    </View>
  );

  const renderHospitalCard = (hospital: Hospital, index: number) => (
    <View key={index} style={styles.hospitalCard}>
      {/* Header do Hospital */}
      <View style={styles.hospitalHeader}>
        <View style={styles.hospitalInfo}>
          <Text style={styles.hospitalNome} numberOfLines={2}>
            {hospital.sigla}
          </Text>
          <Text style={styles.hospitalCidade}>{hospital.cidade}</Text>
          <Text style={styles.hospitalTipo}>{hospital.tipo}</Text>
        </View>
        
        <View style={styles.statusContainer}>
          <View style={[styles.statusBadge, { backgroundColor: hospital.cor_status }]}>
            <Text style={styles.statusBadgeText}>
              {getStatusIcon(hospital.status_ocupacao)}
            </Text>
          </View>
        </View>
      </View>

      {/* Barra de Ocupação */}
      <View style={styles.ocupacaoContainer}>
        <View style={styles.ocupacaoHeader}>
          <Text style={styles.ocupacaoLabel}>Taxa de Ocupação</Text>
          <Text style={[styles.ocupacaoPercentual, { color: hospital.cor_status }]}>
            {hospital.taxa_ocupacao}%
          </Text>
        </View>
        
        <View style={styles.progressBarContainer}>
          <View 
            style={[
              styles.progressBar, 
              { 
                width: `${hospital.taxa_ocupacao}%`,
                backgroundColor: hospital.cor_status 
              }
            ]} 
          />
        </View>
        
        <View style={styles.leitosInfo}>
          <Text style={styles.leitosText}>
            {hospital.leitos_ocupados}/{hospital.leitos_totais} ocupados
          </Text>
          <Text style={styles.leitosDisponiveis}>
            {hospital.leitos_disponiveis} disponíveis
          </Text>
        </View>
      </View>

      {/* Especialidades */}
      <View style={styles.especialidadesContainer}>
        <Text style={styles.especialidadesLabel}>Especialidades:</Text>
        <View style={styles.especialidadesTags}>
          {hospital.especialidades.slice(0, 3).map((esp, idx) => (
            <View key={idx} style={styles.especialidadeTag}>
              <Text style={styles.especialidadeText}>
                {esp.replace('_', ' ')}
              </Text>
            </View>
          ))}
          {hospital.especialidades.length > 3 && (
            <View style={styles.especialidadeTag}>
              <Text style={styles.especialidadeText}>
                +{hospital.especialidades.length - 3}
              </Text>
            </View>
          )}
        </View>
      </View>

      {/* Footer */}
      <View style={styles.hospitalFooter}>
        <Text style={styles.ultimaAtualizacao}>
          Atualizado às {hospital.ultima_atualizacao}
        </Text>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.sectionTitle}>Ocupação de Leitos - Rede Estadual</Text>
      
      {/* Resumo Geral */}
      {renderResumoCard()}
      
      {/* Lista de Hospitais */}
      <ScrollView 
        horizontal 
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.hospitaisContainer}
      >
        {ocupacao_hospitais.map((hospital, index) => renderHospitalCard(hospital, index))}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#004A8D',
    marginBottom: 15,
    paddingHorizontal: 20,
  },
  
  // Resumo Card
  resumoCard: {
    backgroundColor: '#FFF',
    marginHorizontal: 20,
    marginBottom: 15,
    borderRadius: 12,
    padding: 16,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  resumoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
    textAlign: 'center',
  },
  resumoGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  resumoItem: {
    alignItems: 'center',
    flex: 1,
  },
  resumoNumber: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#004A8D',
  },
  resumoLabel: {
    fontSize: 11,
    color: '#666',
    textAlign: 'center',
    marginTop: 2,
  },
  statusResumo: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  statusItem: {
    alignItems: 'center',
    flexDirection: 'row',
  },
  statusIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 6,
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  statusBadgeText: {
    color: '#FFF',
    fontSize: 10,
    fontWeight: 'bold',
  },
  statusIcon: {
    fontSize: 16,
    marginBottom: 2,
  },
  statusText: {
    fontSize: 11,
    color: '#666',
  },
  
  // Hospitais Container
  hospitaisContainer: {
    paddingHorizontal: 15,
  },
  
  // Hospital Card
  hospitalCard: {
    backgroundColor: '#FFF',
    width: width * 0.8,
    marginHorizontal: 5,
    borderRadius: 12,
    padding: 16,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  hospitalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 15,
  },
  hospitalInfo: {
    flex: 1,
  },
  hospitalNome: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#004A8D',
    marginBottom: 4,
  },
  hospitalCidade: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  hospitalTipo: {
    fontSize: 11,
    color: '#888',
    fontStyle: 'italic',
  },
  statusContainer: {
    alignItems: 'center',
    marginLeft: 10,
  },
  
  // Ocupação
  ocupacaoContainer: {
    marginBottom: 15,
  },
  ocupacaoHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  ocupacaoLabel: {
    fontSize: 13,
    color: '#666',
    fontWeight: '600',
  },
  ocupacaoPercentual: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  progressBarContainer: {
    height: 8,
    backgroundColor: '#E0E0E0',
    borderRadius: 4,
    marginBottom: 8,
  },
  progressBar: {
    height: '100%',
    borderRadius: 4,
  },
  leitosInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  leitosText: {
    fontSize: 12,
    color: '#666',
  },
  leitosDisponiveis: {
    fontSize: 12,
    color: '#4CAF50',
    fontWeight: '600',
  },
  
  // Especialidades
  especialidadesContainer: {
    marginBottom: 12,
  },
  especialidadesLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 6,
  },
  especialidadesTags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  especialidadeTag: {
    backgroundColor: '#E3F2FD',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 12,
    marginRight: 6,
    marginBottom: 4,
  },
  especialidadeText: {
    fontSize: 10,
    color: '#1976D2',
    fontWeight: '500',
  },
  
  // Footer
  hospitalFooter: {
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
    paddingTop: 8,
  },
  ultimaAtualizacao: {
    fontSize: 10,
    color: '#999',
    textAlign: 'center',
    fontStyle: 'italic',
  },
});

export default OcupacaoHospitais;