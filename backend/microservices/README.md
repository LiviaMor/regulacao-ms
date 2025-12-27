# ARQUITETURA DE MICROSERVIÇOS - SISTEMA DE REGULAÇÃO SES-GO

## Visão Geral

Sistema distribuído em microserviços para escalabilidade e manutenibilidade, permitindo crescimento futuro com novos serviços especializados.

## Microserviços Implementados

### 1. MS-Hospital (Porta 8001)
- **Responsabilidade**: Gestão de solicitações hospitalares
- **Funcionalidades**:
  - Cadastro de pacientes
  - Solicitação de regulação
  - Lista de pacientes aguardando
  - Interface hospitalar

### 2. MS-Regulacao (Porta 8002)
- **Responsabilidade**: Processamento de regulação médica
- **Funcionalidades**:
  - IA inteligente para análise
  - Pipeline de hospitais de Goiás
  - Fila de regulação
  - Decisões do regulador
  - Auditoria completa

### 3. MS-Transferencia (Porta 8003)
- **Responsabilidade**: Logística de transferências
- **Funcionalidades**:
  - Autorização de transferências
  - Gestão de ambulâncias
  - Acompanhamento de transporte
  - Status de transferência

## Microserviços Futuros (Planejados)

### 4. MS-Alta (Porta 8004)
- Gestão de altas hospitalares
- Contrarreferência
- Relatórios de alta

### 5. MS-Obito (Porta 8005)
- Registro de óbitos
- Estatísticas de mortalidade
- Relatórios epidemiológicos

### 6. MS-Transplante (Porta 8006)
- Fila de transplantes
- Compatibilidade de órgãos
- Logística de transplantes

### 7. MS-Medicacao (Porta 8007)
- Medicação de alta complexidade
- Controle de estoque
- Dispensação especializada

## Comunicação Entre Microserviços

- **API Gateway**: Nginx (Porta 80/443)
- **Banco Compartilhado**: PostgreSQL
- **Cache**: Redis
- **Mensageria**: Celery + Redis

## Estrutura de Pastas

```
backend/microservices/
├── ms-hospital/
├── ms-regulacao/
├── ms-transferencia/
├── ms-alta/ (futuro)
├── ms-obito/ (futuro)
├── ms-transplante/ (futuro)
├── ms-medicacao/ (futuro)
├── shared/
│   ├── database.py
│   ├── auth.py
│   └── utils.py
└── docker-compose.microservices.yml
```

## Vantagens da Arquitetura

1. **Escalabilidade**: Cada serviço pode ser escalado independentemente
2. **Manutenibilidade**: Código organizado por domínio
3. **Flexibilidade**: Novos serviços podem ser adicionados facilmente
4. **Resiliência**: Falha em um serviço não afeta os outros
5. **Especialização**: Cada equipe pode focar em um domínio específico

## Migração do Sistema Atual

O sistema atual (`main_unified.py`) será gradualmente migrado para os microserviços, mantendo compatibilidade durante a transição.