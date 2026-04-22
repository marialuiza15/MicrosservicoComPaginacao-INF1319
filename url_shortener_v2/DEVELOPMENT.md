# Guia de Desenvolvimento Local

## Pré-requisitos

- Python 3.11+
- PostgreSQL 15+
- pip/poetry
- Git

## Setup Inicial

### 1. Clonar o repositório

```bash
git clone <seu-repo>
cd url_shortener_v2
```

### 2. Criar ambiente virtual

```bash
# Linux/Mac
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
pip install pytest pytest-cov  # Para testes
```

### 4. Configurar banco de dados

```bash
# Criar arquivo .env
cp .env.example .env

# Editar .env com suas credenciais
# DATABASE_URL=postgresql://seu_usuario:sua_senha@localhost:5432/encurtador
```

### 5. Criar tabelas

```bash
python
>>> from models import Base
>>> from database import engine
>>> Base.metadata.create_all(bind=engine)
>>> exit()
```

Ou use o script de seed:

```bash
python seed.py
```

### 6. Iniciar o servidor

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

A API estará em: http://localhost:5000

## Estrutura de Pastas

```
.
├── main.py              # Aplicação principal
├── config.py            # Configurações
├── models.py            # Modelos do banco
├── schemas.py           # Schemas Pydantic
├── database.py          # Conexão DB
├── auth.py              # Autenticação JWT
├── utils.py             # Utilitários
├── seed.py              # Seed database
├── test_main.py         # Testes
├── routers/
│   ├── __init__.py
│   ├── auth.py          # Endpoints auth
│   ├── urls.py          # Endpoints URLs (3 principais)
│   └── redirect.py      # Endpoints redirect
├── requirements.txt     # Dependências
├── Dockerfile           # Imagem Docker
├── docker-compose.yml   # Orquestração
├── .env.example         # Exemplo env
├── .gitignore
├── README.md
└── DEVELOPMENT.md       # Este arquivo
```

## Workflow de Desenvolvimento

### Criar novo endpoint

1. Criar função no router apropriado (`routers/*.py`)
2. Adicionar schema Pydantic se necessário (`schemas.py`)
3. Adicionar testes (`test_main.py`)
4. Documentar no README

Exemplo:

```python
# routers/urls.py
@router.post("/validate")
def validate_url(
    url: str,
    db: Session = Depends(get_db)
):
    """Valida se uma URL é válida"""
    try:
        # Validação
        return {"valid": True}
    except:
        return {"valid": False}
```

### Executar testes

```bash
# Todos os testes
pytest test_main.py -v

# Teste específico
pytest test_main.py::TestURLEndpoints::test_create_short_url -v

# Com cobertura
pytest test_main.py --cov=.
```

### Debug

```bash
# Habilitar echo SQL
# Em config.py, altere:
# engine = create_engine(..., echo=True)

# Ou use debugger
import pdb; pdb.set_trace()
```

## Commits e Versionamento

Seguir convenção Conventional Commits:

```bash
git commit -m "feat: adicionar endpoint de validação"
git commit -m "fix: corrigir paginação"
git commit -m "docs: atualizar README"
git commit -m "test: adicionar testes para URLs"
```

## Padrões de Código

### Imports

```python
# 1. Stdlib
import os
import json
from datetime import datetime

# 2. Third-party
from sqlalchemy import create_engine
from fastapi import FastAPI

# 3. Local
from models import User
from database import get_db
```

### Funções async

```python
# FastAPI geralmente usa async
@router.get("/")
async def get_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

### Type hints

```python
# Sempre usar type hints
def create_user(username: str, email: str) -> User:
    """Cria um novo usuário"""
    pass
```

### Docstrings

```python
def get_user_urls(user_id: str, skip: int, limit: int) -> List[URL]:
    """
    Obtém URLs do usuário com paginação.
    
    Args:
        user_id: ID do usuário
        skip: Número de registros a pular
        limit: Máximo de registros a retornar
    
    Returns:
        Lista de URLs do usuário
        
    Raises:
        HTTPException: Se usuário não encontrado
    """
    pass
```

## Troubleshooting

### "Conexão recusada ao banco de dados"

```bash
# Verificar se PostgreSQL está rodando
psql -U user -d encurtador

# Se usando Docker
docker-compose ps
docker-compose logs db
```

### "Módulo não encontrado"

```bash
# Reinstalar dependências
pip install -r requirements.txt --force-reinstall

# Verificar PYTHONPATH
echo $PYTHONPATH
```

### "Erro de migração"

```bash
# Resetar banco (cuidado!)
python
>>> from models import Base
>>> from database import engine
>>> Base.metadata.drop_all(bind=engine)
>>> Base.metadata.create_all(bind=engine)
```

## Performance

### Profiling

```python
from sqlalchemy import event

# Ver todas as queries SQL
@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    print(statement)
```

### Índices

Verificar índices criados:

```sql
SELECT * FROM pg_indexes WHERE tablename = 'urls';
```

## Deploy

Veja o arquivo docker-compose.yml para deploy com containers.

Para produção:

1. Usar variáveis de ambiente seguras
2. Habilitar HTTPS/TLS
3. Adicionar rate limiting
4. Configurar logging centralizado
5. Usar load balancer (nginx)

## Recursos Úteis

- [FastAPI Docs](https://fastapi.tiangolo.com)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org)
- [Pydantic Docs](https://docs.pydantic.dev)
- [PostgreSQL Docs](https://www.postgresql.org/docs)

