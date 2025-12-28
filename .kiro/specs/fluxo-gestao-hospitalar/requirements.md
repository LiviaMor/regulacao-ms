# Requisitos: Fluxo de Gestão Hospitalar

## Visão Geral
Sistema de regulação autônoma para gestão de pacientes entre hospitais e central de regulação da SES-GO.

## Requisitos Funcionais

### RF01 - Área Hospitalar (Solicitação de Regulação)
- **RF01.1**: Hospital deve preencher formulário com dados LGPD do paciente (nome_completo, nome_mae, cpf, telefone_contato)
- **RF01.2**: Hospital deve informar dados clínicos (especialidade, CID, prontuário, histórico)
- **RF01.3**: Sistema deve processar solicitação com IA (BioBERT + Pipeline RAG)
- **RF01.4**: Paciente deve ser salvo com status `AGUARDANDO_REGULACAO`
- **RF01.5**: Hospital deve visualizar lista de pacientes aguardando ou negados

### RF02 - Fila de Regulação (Central)
- **RF02.1**: Regulador deve visualizar pacientes com status `AGUARDANDO_REGULACAO`
- **RF02.2**: Regulador pode processar paciente com IA para obter sugestão
- **RF02.3**: Sistema deve exibir CardDecisaoIA com análise completa
- **RF02.4**: Regulador pode AUTORIZAR, NEGAR ou ALTERAR decisão da IA

### RF03 - Decisão do Regulador
- **RF03.1**: AUTORIZAR: muda status para `EM_TRANSFERENCIA`, aciona ambulância
- **RF03.2**: NEGAR: muda status para `NEGADO_PENDENTE`, retorna ao hospital com justificativa
- **RF03.3**: ALTERAR: permite mudar hospital destino antes de autorizar

### RF04 - Área de Transferência
- **RF04.1**: Exibir pacientes com status `EM_TRANSFERENCIA` ou `EM_TRANSITO`
- **RF04.2**: Permitir atualização de status da ambulância
- **RF04.3**: Registrar chegada e alta do paciente

## Requisitos Não-Funcionais

### RNF01 - LGPD
- Dados pessoais devem ser anonimizados em consultas públicas
- CPF e telefone devem ser mascarados em logs

### RNF02 - Performance
- Processamento IA deve completar em < 5 segundos
- Fila deve atualizar em tempo real

### RNF03 - Auditoria
- Todas as decisões devem ser registradas com timestamp e usuário

## Status do Paciente (Fluxo)
```
AGUARDANDO_REGULACAO → EM_REGULACAO → EM_TRANSFERENCIA → EM_TRANSITO → ADMITIDO → ALTA
                    ↘ NEGADO_PENDENTE (retorna ao hospital)
```

## Endpoints Backend
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/processar-regulacao` | POST | Processa paciente com IA |
| `/salvar-paciente-hospital` | POST | Salva paciente do hospital |
| `/pacientes-hospital-aguardando` | GET | Lista fila de regulação |
| `/decisao-regulador` | POST | Registra decisão do regulador |

## Componentes Frontend
| Componente | Função |
|------------|--------|
| `AreaHospital.tsx` | Formulário de solicitação |
| `FilaRegulacao.tsx` | Lista de pacientes aguardando |
| `CardDecisaoIA.tsx` | Exibe análise IA e botões de decisão |
| `AreaTransferencia.tsx` | Gestão de transferências |
