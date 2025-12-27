# 🏥 PIPELINE INTELIGENTE DE HOSPITAIS DE GOIÁS - IMPLEMENTADO

## 🎯 PROBLEMA RESOLVIDO

**ANTES**: A IA encaminhava pacientes com dor lombar para o HUGO (Hospital de Urgências), que é especializado em trauma e urgência.

**AGORA**: Pipeline inteligente seleciona o hospital correto baseado na especialidade, tipo de caso e complexidade.

---

## 🏥 HOSPITAIS MAPEADOS NO PIPELINE

### 🔴 **HOSPITAIS DE REFERÊNCIA ESTADUAL**

#### **HOSPITAL ESTADUAL DR ALBERTO RASSI HGG** (Goiânia)
- **Especialidades**: Cardiologia, Neurologia, Neurocirurgia, Nefrologia, Transplantes
- **Indicado para**: Infarto, AVC, casos cardiológicos complexos, neurologia
- **Capacidade**: ALTA
- **Observação**: Principal hospital de referência estadual

#### **HOSPITAL DE URGÊNCIAS DE GOIÁS DR VALDEMIRO CRUZ HUGO** (Goiânia)
- **Especialidades**: TRAUMA, Ortopedia Trauma, Neurocirurgia Trauma, Queimados
- **Indicado para**: APENAS trauma e urgência
- **Capacidade**: ALTA
- **⚠️ EXCLUSÕES**: NÃO atende casos eletivos, dor crônica, baixa complexidade

#### **HOSPITAL ESTADUAL DE ANÁPOLIS DR HENRIQUE SANTILLO** (Anápolis)
- **Especialidades**: Cardiologia, Neurologia, Ortopedia, Oncologia, Transplantes
- **Indicado para**: Casos eletivos, ortopedia não traumática, oncologia
- **Capacidade**: ALTA
- **Observação**: Referência regional, atende casos eletivos

### 🟡 **HOSPITAIS ESPECIALIZADOS**

#### **HOSPITAL ESTADUAL MATERNO INFANTIL** (Goiânia)
- **Especialidades**: Obstetrícia, Pediatria, Neonatologia
- **Indicado para**: APENAS mulheres grávidas e crianças
- **⚠️ EXCLUSÕES**: NÃO atende homens adultos

#### **HOSPITAL DE DOENÇAS TROPICAIS HDT** (Goiânia)
- **Especialidades**: Infectologia, HIV, Hepatites, Tuberculose
- **Indicado para**: APENAS doenças infecciosas
- **⚠️ EXCLUSÕES**: NÃO atende casos não infecciosos

### 🟢 **HOSPITAIS REGIONAIS**

- **HOSPITAL ESTADUAL DE FORMOSA** → Região nordeste de Goiás
- **HOSPITAL ESTADUAL DE JATAÍ** → Região sudoeste de Goiás
- **HOSPITAL ESTADUAL DO CENTRO NORTE** (Uruaçu) → Região centro-norte
- **HOSPITAL ESTADUAL DE LUZIÂNIA** → Região sul e entorno do DF

---

## 🧠 LÓGICA DO PIPELINE

### 1. **ANÁLISE DE CID**
```python
# Mapeia CIDs para especialidades necessárias
"I21": ["CARDIOLOGIA", "HEMODINÂMICA", "UTI_CARDIOLÓGICA"]  # Infarto
"S06": ["NEUROCIRURGIA", "TRAUMA", "UTI_TRAUMA"]            # TCE
"M54": ["ORTOPEDIA", "CLÍNICA_MÉDICA"]                      # Dor lombar
```

### 2. **CLASSIFICAÇÃO DE CASOS**
- **TRAUMA** → Casos com CID S* ou T* + sintomas de trauma
- **EMERGÊNCIA** → Infarto, AVC, parada cardíaca
- **ORTOPEDIA_ELETIVA** → Dor lombar, artrose (sem trauma)
- **CLÍNICO_GERAL** → Casos clínicos gerais

### 3. **CRITÉRIOS DE EXCLUSÃO**
```python
HUGO_EXCLUSÕES = [
    "CASOS_ELETIVOS",        # Não atende casos eletivos
    "BAIXA_COMPLEXIDADE",    # Não atende baixa complexidade
    "DOR_CRÔNICA"           # Não atende dor crônica
]
```

### 4. **RANQUEAMENTO POR ADEQUAÇÃO**
- **Score por tipo**: Especializado (+15), Referência (+10), Regional (+5)
- **Score por capacidade**: Alta (+10), Média (+5)
- **Score por especialidades**: +5 por especialidade compatível
- **Bonus específicos**: Trauma no HUGO (+20), Cardiologia no Rassi (+15)
- **Penalidades**: Caso eletivo no HUGO (-50)

---

## ✅ RESULTADOS DOS TESTES

### **CASOS ELETIVOS (NÃO devem ir para HUGO)**
- ✅ **Dor Lombar Crônica** → Hospital de Anápolis
- ✅ **Artrose de Joelho** → Hospital de Anápolis
- ✅ **Consultas Ortopédicas** → Hospitais regionais adequados

### **CASOS DE TRAUMA (DEVEM ir para HUGO)**
- ✅ **Traumatismo Craniano** → HUGO
- ✅ **Fratura Exposta** → HUGO
- ✅ **Politraumatismo** → HUGO

### **CASOS CARDIOLÓGICOS (DEVEM ir para RASSI)**
- ✅ **Infarto Agudo** → Hospital Rassi
- ✅ **AVC** → Hospital Rassi
- ✅ **Emergências Cardiológicas** → Hospital Rassi

---

## 🔧 IMPLEMENTAÇÃO TÉCNICA

### **Arquivo Principal**: `backend/pipeline_hospitais_goias.py`
- Classe `HospitalGoias`: Representa cada hospital com especialidades
- Classe `PipelineHospitaisGoias`: Lógica de seleção inteligente
- Função `selecionar_hospital_goias()`: Interface principal

### **Integração**: `backend/main_unified.py`
- Função `analisar_com_ia_inteligente()` usa o pipeline
- Import automático: `from pipeline_hospitais_goias import selecionar_hospital_goias`
- Fallback em caso de erro no pipeline

### **Logs de Funcionamento**:
```
INFO:pipeline_hospitais_goias:🏥 Selecionando hospital para CID: M54.5, Especialidade: ORTOPEDIA
INFO:pipeline_hospitais_goias:🏥 Selecionando hospital para CID: S06.9, Especialidade: NEUROCIRURGIA
```

---

## 📊 JUSTIFICATIVAS GERADAS

### **Exemplo - Dor Lombar**:
```
Hospital de referência estadual | 
Possui especialidades: ORTOPEDIA, TRAUMATOLOGIA, CLINICA_MEDICA | 
Referência regional. Oncologia e transplantes. Atende região metropolitana. | 
Adequado para casos ortopédicos eletivos
```

### **Exemplo - Trauma Craniano**:
```
Hospital de referência estadual | 
Possui especialidades: UTI_TRAUMA, ORTOPEDIA_TRAUMA, NEUROCIRURGIA_TRAUMA | 
ESPECIALIZADO EM TRAUMA E URGÊNCIA. NÃO para casos eletivos ou baixa complexidade. | 
Especializado em trauma e urgência
```

---

## 🎯 BENEFÍCIOS DO PIPELINE

1. **✅ Encaminhamento Correto**: Cada paciente vai para o hospital mais adequado
2. **✅ Otimização de Recursos**: HUGO fica livre para traumas reais
3. **✅ Melhor Atendimento**: Pacientes chegam no hospital com a especialidade certa
4. **✅ Transparência**: Justificativa clara do motivo da escolha
5. **✅ Escalabilidade**: Fácil adicionar novos hospitais e especialidades
6. **✅ Auditoria**: Todas as decisões são registradas e justificadas

---

## 🚀 PRÓXIMOS PASSOS

1. **Integração com APIs Reais**: Conectar com sistemas dos hospitais para disponibilidade de leitos
2. **Machine Learning**: Usar dados históricos para melhorar as sugestões
3. **Geolocalização**: Considerar distância e tempo de transporte
4. **Especialidades Detalhadas**: Mapear subespecialidades médicas
5. **Feedback dos Reguladores**: Aprender com as decisões dos profissionais

---

## 🎉 CONCLUSÃO

**O PIPELINE DE HOSPITAIS DE GOIÁS ESTÁ FUNCIONANDO PERFEITAMENTE!**

- ❌ **Problema resolvido**: Dor lombar não vai mais para o HUGO
- ✅ **Trauma vai para HUGO**: Casos de urgência no hospital certo
- ✅ **Cardiologia vai para RASSI**: Especialização adequada
- ✅ **Sistema inteligente**: Considera tipo de caso, especialidade e capacidade
- ✅ **Totalmente auditável**: Justificativas claras para cada decisão

**O sistema está pronto para apresentação no ABERTO de IA de Goiás!** 🏆