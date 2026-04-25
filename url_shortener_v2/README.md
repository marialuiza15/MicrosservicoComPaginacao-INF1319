# URL Shortener v2

## Visão Geral
[descrição do projeto]

## Como Executar
docker-compose up

## Endpoints
[listar os 3 endpoints principais]

## Melhorias Arquiteturais Potenciais

### 1. Desempenho
- Adicionar índices no banco em (user_id, created_at)
- Implementar cache Redis para URLs frequentes
- Connection pooling no banco de dados

### 2. Consistência de Dados
- Usar transações para operações críticas
- Validar URL antes de armazenar
- Implementar soft deletes para auditoria

### 3. Acoplamento
- Separar lógica de validação em módulos
- Usar dependency injection para serviços
- Desacoplar autenticação em middleware reutilizável

### 4. Resiliência
- Implementar rate limiting por usuário
- Circuit breaker para dependências externas
- Logging estruturado para debug