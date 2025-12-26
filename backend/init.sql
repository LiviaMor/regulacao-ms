-- Script de inicialização do banco de dados PostgreSQL
-- Sistema de Regulação Autônoma SES-GO

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Configurações de performance
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Recarregar configurações
SELECT pg_reload_conf();

-- Criar usuário específico para a aplicação se não existir
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'regulacao_app') THEN
        CREATE ROLE regulacao_app WITH LOGIN PASSWORD 'regulacao_app_pass';
    END IF;
END
$$;

-- Conceder permissões
GRANT CONNECT ON DATABASE regulacao_db TO regulacao_app;
GRANT USAGE ON SCHEMA public TO regulacao_app;
GRANT CREATE ON SCHEMA public TO regulacao_app;

-- Criar índices para otimização (serão criados após as tabelas)
-- Os índices serão criados automaticamente pelo SQLAlchemy

-- Log de inicialização
INSERT INTO pg_stat_statements_reset();

-- Comentários para documentação
COMMENT ON DATABASE regulacao_db IS 'Banco de dados do Sistema de Regulação Autônoma SES-GO';

-- Configurar timezone
SET timezone = 'America/Sao_Paulo';