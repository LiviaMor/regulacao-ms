-- Migração: Adicionar campos LGPD à tabela pacientes_regulacao
-- Data: 2025-12-27
-- Descrição: Adiciona campos de dados pessoais (nome, CPF, telefone) conforme LGPD

-- Adicionar colunas de dados pessoais (nullable para não quebrar dados existentes)
ALTER TABLE pacientes_regulacao 
ADD COLUMN IF NOT EXISTS nome_completo VARCHAR,
ADD COLUMN IF NOT EXISTS nome_mae VARCHAR,
ADD COLUMN IF NOT EXISTS cpf VARCHAR,
ADD COLUMN IF NOT EXISTS telefone_contato VARCHAR,
ADD COLUMN IF NOT EXISTS data_nascimento TIMESTAMP;

-- Criar índice no CPF para buscas rápidas
CREATE INDEX IF NOT EXISTS idx_pacientes_cpf ON pacientes_regulacao(cpf);

-- Atualizar registros existentes com valores padrão
UPDATE pacientes_regulacao 
SET 
    nome_completo = COALESCE(nome_completo, 'Paciente ' || protocolo),
    nome_mae = COALESCE(nome_mae, 'Não informado'),
    cpf = COALESCE(cpf, '00000000000'),
    telefone_contato = COALESCE(telefone_contato, '00000000000')
WHERE nome_completo IS NULL 
   OR nome_mae IS NULL 
   OR cpf IS NULL 
   OR telefone_contato IS NULL;

-- Verificar resultado
SELECT COUNT(*) as total_registros,
       COUNT(nome_completo) as com_nome,
       COUNT(cpf) as com_cpf,
       COUNT(telefone_contato) as com_telefone
FROM pacientes_regulacao;
