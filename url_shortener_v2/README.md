# URL Shortener API v2

## 📋 Descrição do Projeto

Uma API de encurtador de URLs desenvolvida em **Python + FastAPI + PostgreSQL**, com autenticação JWT e sistema de paginação. Este projeto é uma evolução da v1 (Flask), implementando melhorias significativas em arquitetura, segurança e escalabilidade.

### 🎯 Objetivos

- ✅ Criar URLs encurtadas únicas
- ✅ Listar URLs com paginação (3 endpoints diferentes)
- ✅ Deletar URLs cadastradas
- ✅ Sistema de autenticação JWT
- ✅ Controle de permissões (admin vs usuário comum)
- ✅ Redirecionamento de URLs com contagem de cliques
- ✅ Containerização com Docker

---

## 🚀 Tecnologias Utilizadas

| Tecnologia | Versão | Propósito |
|-----------|--------|----------|
| Python | 3.11+ | Linguagem principal |
| FastAPI | 0.104+ | Framework web |
| PostgreSQL | 15 | Banco de dados |
| SQLAlchemy | 2.0+ | ORM |
| JWT (python-jose) | 3.3+ | Autenticação |
| Pydantic | 2.5+ | Validação de dados |
| Docker | - | Containerização |
| Uvicorn | 0.24+ | Servidor ASGI |

---

## 📦 Instalação e Configuração

### Pré-requisitos

- Docker e Docker Compose instalados
- Python 3.11+ (se executar localmente)
- PostgreSQL 15+ (se não usar Docker)

### Com Docker Compose (Recomendado)

```bash
# Clone o repositório
git clone <seu-repo>
cd url_shortener_v2

# Inicie os containers
docker-compose up --build

# A API estará disponível em http://localhost:5000
# Docs interativa em http://localhost:5000/docs
```

### Sem Docker (Desenvolvimento Local)

```bash
# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure o banco de dados (edit config.py ou .env)
# DATABASE_URL=postgresql://seu_usuario:sua_senha@localhost:5432/encurtador

# Inicie a API
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

---

## 🔐 Autenticação

Este projeto usa **JWT (JSON Web Tokens)** para autenticação.

### 1. Registrar um novo usuário

```bash
curl -X POST "http://localhost:5000/api/v2/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "joao",
    "email": "joao@example.com",
    "password": "senha123"
  }'
```

Resposta:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "joao",
  "email": "joao@example.com",
  "is_admin": false,
  "created_at": "2024-01-15T10:30:00"
}
```

### 2. Fazer login e obter token

```bash
curl -X POST "http://localhost:5000/api/v2/auth/login?username=joao&password=senha123"
```

Resposta:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Usar o token em requisições

```bash
curl -X GET "http://localhost:5000/api/v2/urls/user/my-urls" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## 📚 Endpoints da API

### 1️⃣ **ENDPOINT 1: Listar Todas as URLs (Admin)**

**Descrição:** Retorna TODAS as URLs cadastradas no sistema com paginação. Apenas administradores podem acessar.

```bash
GET /api/v2/urls/admin/all?page=1&page_size=10
Authorization: Bearer <token_admin>
```

**Parâmetros Query:**
- `page` (int, default=1): Número da página
- `page_size` (int, default=10): Itens por página (máx: 100)

**Resposta (200 OK):**
```json
{
  "total": 45,
  "page": 1,
  "page_size": 10,
  "total_pages": 5,
  "items": [
    {
      "id": "uuid-1",
      "original_url": "https://google.com",
      "short_code": "abc123",
      "user_id": "uuid-user-1",
      "created_at": "2024-01-15T10:30:00",
      "is_active": true,
      "hits": 42
    },
    ...
  ],
  "has_next": true,
  "has_previous": false
}
```

### 2️⃣ **ENDPOINT 2: Listar URLs do Usuário**

**Descrição:** Retorna apenas as URLs criadas pelo usuário autenticado, com paginação.

```bash
GET /api/v2/urls/user/my-urls?page=1&page_size=10
Authorization: Bearer <token>
```

**Parâmetros Query:**
- `page` (int, default=1): Número da página
- `page_size` (int, default=10): Itens por página (máx: 100)

**Resposta (200 OK):** Mesmo formato do endpoint 1, mas filtrando apenas URLs do usuário.

### 3️⃣ **ENDPOINT 3: Deletar URL**

**Descrição:** Deleta uma URL encurtada. Usuários só podem deletar suas próprias URLs. Admins podem deletar qualquer URL.

```bash
DELETE /api/v2/urls/{url_id}
Authorization: Bearer <token>
```

**Path Parameters:**
- `url_id` (string): ID da URL a deletar

**Resposta (204 No Content):** Sem corpo de resposta

**Erros:**
- `404 Not Found`: URL não existe
- `403 Forbidden`: Sem permissão para deletar (não é seu ou não é admin)

---

## 🔍 Endpoints Auxiliares

### Criar URL Encurtada

```bash
POST /api/v2/urls/
Authorization: Bearer <token>
Content-Type: application/json

{
  "original_url": "https://exemplo.com/pagina-muito-longa-e-chata"
}
```

Resposta (201 Created):
```json
{
  "id": "uuid-123",
  "original_url": "https://exemplo.com/pagina-muito-longa-e-chata",
  "short_code": "x7kP2w",
  "user_id": "uuid-user",
  "created_at": "2024-01-15T10:30:00",
  "is_active": true,
  "hits": 0
}
```

### Redirecionar para URL Original

```bash
GET /{short_code}
```

Resposta: Redirecionamento (HTTP 301) para a URL original

### Obter Estatísticas

```bash
GET /stats/{short_code}
```

Resposta:
```json
{
  "short_code": "x7kP2w",
  "original_url": "https://exemplo.com/...",
  "hits": 15,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00"
}
```

---

## 📊 Documentação Interativa

A API inclui documentação automática:

- **Swagger UI:** http://localhost:5000/docs
- **ReDoc:** http://localhost:5000/redoc

---

## 🏗️ Estrutura do Projeto

```
url_shortener_v2/
├── main.py              # Aplicação FastAPI principal
├── config.py            # Configurações (DB, JWT, etc)
├── models.py            # Modelos SQLAlchemy (User, URL)
├── schemas.py           # Schemas Pydantic (validação)
├── database.py          # Conexão com banco de dados
├── auth.py              # Autenticação JWT e segurança
├── utils.py             # Funções auxiliares
├── routers/
│   ├── auth.py          # Endpoints de registro e login
│   ├── urls.py          # Endpoints de URL (os 3 principais)
│   └── redirect.py      # Endpoints de redirecionamento
├── Dockerfile           # Imagem Docker
├── docker-compose.yml   # Orquestração de containers
├── requirements.txt     # Dependências Python
├── .env.example         # Exemplo de variáveis de ambiente
├── .gitignore           # Arquivos ignorados pelo git
└── README.md            # Este arquivo
```

---

## 🔧 Variáveis de Ambiente

Configure o arquivo `.env` na raiz do projeto:

```env
DATABASE_URL=postgresql://user:password@db:5432/encurtador
SECRET_KEY=sua-chave-secreta-mude-em-producao
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEFAULT_PAGE_SIZE=10
MAX_PAGE_SIZE=100
```

---

## 📈 Melhorias Arquiteturais Propostas

Este projeto implementa boas práticas, mas aqui estão melhorias possíveis:

### 1. **DESEMPENHO** ⚡

#### Problemas Atuais:
- Sem cache de URLs frequentes
- Sem índices otimizados para queries populares
- Sem compressão de resposta
- Sem rate limiting

#### Soluções Propostas:

**A) Cache com Redis**
```python
# Cachear URLs populares
from redis import Redis
redis_client = Redis(host='redis', port=6379)

@router.get("/{short_code}")
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    # Primeiro tenta cache
    cached = redis_client.get(f"url:{short_code}")
    if cached:
        return RedirectResponse(cached)
    
    # Se não estiver em cache, busca no DB e cacheia
    url = db.query(URL).filter(URL.short_code == short_code).first()
    redis_client.setex(f"url:{short_code}", 3600, url.original_url)
    return RedirectResponse(url.original_url)
```

**B) Índices de Banco de Dados Otimizados**
```python
class URL(Base):
    __tablename__ = "urls"
    
    # Índice composto para melhorar buscas por usuário + data
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
        Index('idx_short_code', 'short_code'),  # Único já existe
        Index('idx_is_active', 'is_active'),
    )
```

**C) Paginação com Cursor (melhor que offset)**
```python
# Em vez de offset/limit, usar cursor-based pagination
# Mais eficiente para grandes datasets
@router.get("/admin/all/cursor")
def list_urls_cursor(
    cursor: Optional[str] = None,
    page_size: int = 10
):
    """Cursor-based pagination"""
    query = db.query(URL).order_by(URL.created_at.desc())
    
    if cursor:
        query = query.filter(URL.created_at < decode_cursor(cursor))
    
    urls = query.limit(page_size + 1).all()
    has_next = len(urls) > page_size
    
    return {
        "items": urls[:page_size],
        "next_cursor": encode_cursor(urls[-2].created_at) if has_next else None
    }
```

**D) Compressão GZIP**
```python
from fastapi.middleware.gzip import GZIPMiddleware

app.add_middleware(GZIPMiddleware, minimum_size=1000)
```

**E) Rate Limiting**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.get("/{short_code}")
@limiter.limit("100/minute")
def redirect_to_url(request: Request, short_code: str):
    # Máximo 100 requisições por minuto
    ...
```

---

### 2. **CONSISTÊNCIA DE DADOS** 🔄

#### Problemas Atuais:
- Sem transações explícitas
- Sem validação de integridade referencial
- Sem auditoria de mudanças
- Sem soft deletes

#### Soluções Propostas:

**A) Soft Deletes (deletar sem apagar)**
```python
class URL(Base):
    __tablename__ = "urls"
    
    deleted_at = Column(DateTime, nullable=True)  # Soft delete
    
    @property
    def is_deleted(self):
        return self.deleted_at is not None
```

**B) Auditoria de Mudanças**
```python
from datetime import datetime
from sqlalchemy import event

class URLHistory(Base):
    __tablename__ = "url_history"
    
    id = Column(String(36), primary_key=True)
    url_id = Column(String(36), ForeignKey("urls.id"))
    action = Column(String(10))  # CREATE, UPDATE, DELETE
    changed_by = Column(String(36), ForeignKey("users.id"))
    changed_at = Column(DateTime, default=datetime.utcnow)
    old_values = Column(JSON)
    new_values = Column(JSON)

@event.listens_for(URL, 'after_update')
def receive_after_update(mapper, connection, target):
    # Registrar mudanças em URLHistory
    ...
```

**C) Transações Explícitas**
```python
@router.post("/urls/batch")
def create_urls_batch(urls: List[URLCreate], current_user: User = Depends(get_current_user)):
    try:
        new_urls = []
        for url_data in urls:
            new_url = URL(
                original_url=url_data.original_url,
                short_code=generate_unique_short_code(db),
                user_id=current_user.id
            )
            new_urls.append(new_url)
        
        db.add_all(new_urls)
        db.commit()  # Tudo ou nada
        return new_urls
    except Exception as e:
        db.rollback()  # Desfaz tudo se houver erro
        raise HTTPException(status_code=400, detail=str(e))
```

**D) Constraint de Integridade**
```python
from sqlalchemy import CheckConstraint, UniqueConstraint

class URL(Base):
    __tablename__ = "urls"
    
    __table_args__ = (
        CheckConstraint('length(original_url) > 5'),
        CheckConstraint('length(short_code) > 0'),
        UniqueConstraint('user_id', 'short_code', name='uq_user_short_code'),
    )
```

---

### 3. **ACOPLAMENTO DA SOLUÇÃO** 🔗

#### Problemas Atuais:
- Lógica de negócio acoplada aos routers
- Sem camada de serviço (service layer)
- Dependências diretas no banco

#### Soluções Propostas:

**A) Camada de Serviço (Service Layer)**
```python
# services/url_service.py
class URLService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_short_url(self, original_url: str, user_id: str) -> URL:
        """Lógica de negócio isolada"""
        short_code = generate_unique_short_code(self.db)
        url = URL(
            original_url=original_url,
            short_code=short_code,
            user_id=user_id
        )
        self.db.add(url)
        self.db.commit()
        return url
    
    def get_user_urls(self, user_id: str, skip: int, limit: int):
        """Busca URLs do usuário"""
        return self.db.query(URL).filter(
            URL.user_id == user_id
        ).offset(skip).limit(limit).all()

# routers/urls.py
@router.post("/")
def create_url(
    url_data: URLCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = URLService(db)
    return service.create_short_url(url_data.original_url, current_user.id)
```

**B) Repository Pattern**
```python
# repositories/url_repository.py
class URLRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_short_code(self, short_code: str) -> Optional[URL]:
        return self.db.query(URL).filter(URL.short_code == short_code).first()
    
    def get_by_user_paginated(self, user_id: str, skip: int, limit: int):
        return self.db.query(URL).filter(
            URL.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    def save(self, url: URL):
        self.db.add(url)
        self.db.commit()
        self.db.refresh(url)
        return url
```

**C) Dependency Injection**
```python
from typing import Annotated

def get_url_service(db: Session = Depends(get_db)) -> URLService:
    return URLService(db)

@router.post("/")
def create_url(
    url_data: URLCreate,
    current_user: User = Depends(get_current_user),
    service: URLService = Depends(get_url_service)
):
    return service.create_short_url(url_data.original_url, current_user.id)
```

**D) Event-Driven Architecture**
```python
# events/url_events.py
class URLCreatedEvent:
    def __init__(self, url: URL, created_by: User):
        self.url = url
        self.created_by = created_by
        self.timestamp = datetime.utcnow()

# handlers/email_handler.py
def on_url_created(event: URLCreatedEvent):
    """Envia email quando URL é criada"""
    send_email(
        event.created_by.email,
        f"URL encurtada: {event.url.short_code}"
    )
```

---

### 4. **RESILIÊNCIA** 🛡️

#### Problemas Atuais:
- Sem tratamento robusto de erros
- Sem retry logic
- Sem circuit breaker
- Sem healthchecks adequados
- Sem logging centralizado

#### Soluções Propostas:

**A) Tratamento Robusto de Erros**
```python
from fastapi import exception_handlers
from sqlalchemy.exc import IntegrityError

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=400,
        content={"detail": "Violação de integridade de dados"}
    )

class APIException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
```

**B) Retry com Exponential Backoff**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def get_url_with_retry(db: Session, short_code: str) -> URL:
    """Tenta buscar URL 3 vezes com espera crescente"""
    return db.query(URL).filter(URL.short_code == short_code).first()
```

**C) Circuit Breaker para DB**
```python
from pybreaker import CircuitBreaker

db_breaker = CircuitBreaker(
    fail_max=5,
    reset_timeout=60,
    listeners=[LogListener()]
)

def get_db_with_breaker():
    try:
        db_breaker.call(lambda: db.execute("SELECT 1"))
        return SessionLocal()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Banco de dados indisponível"
        )
```

**D) Health Checks Avançados**
```python
from sqlalchemy import text

@app.get("/health/deep")
async def deep_health_check(db: Session = Depends(get_db)):
    """Verifica saúde de todos os componentes"""
    try:
        # Verifica DB
        db.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "components": {
                "api": "ok",
                "database": "ok",
                "cache": "ok" if redis_client.ping() else "down"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }, 503
```

**E) Logging Centralizado**
```python
import logging
from pythonjsonlogger import jsonlogger

# Configurar logging em JSON para ELK Stack
logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

@router.post("/")
def create_url(...):
    logger.info("URL creation started", extra={
        "user_id": current_user.id,
        "original_url": url_data.original_url
    })
    
    try:
        # ... logic
        logger.info("URL created successfully", extra={
            "short_code": new_url.short_code
        })
    except Exception as e:
        logger.error("URL creation failed", extra={
            "error": str(e),
            "user_id": current_user.id
        })
        raise
```

**F) Monitoring e Métricas**
```python
from prometheus_client import Counter, Histogram, start_http_server

# Métricas
url_creations = Counter('url_creations_total', 'Total URLs criadas')
redirect_latency = Histogram('redirect_latency_seconds', 'Latência de redirecionamento')

@router.get("/{short_code}")
@redirect_latency.time()
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    url = db.query(URL).filter(URL.short_code == short_code).first()
    
    if not url:
        raise HTTPException(status_code=404)
    
    url.hits += 1
    db.commit()
    
    return RedirectResponse(url.original_url)

# Expor métricas em /metrics
start_http_server(8000)
```

---

## 🗂️ Resumo de Melhorias

| Aspecto | Problema Atual | Solução | Benefício |
|---------|---|---|---|
| **Desempenho** | Sem cache | Redis + índices | 100x mais rápido em queries repetidas |
| **Desempenho** | Offset/limit ineficiente | Cursor-based pagination | O(1) em grandes datasets |
| **Consistência** | Hard deletes | Soft deletes + auditoria | Rastreabilidade completa |
| **Acoplamento** | Lógica nos routers | Service + Repository | Testável e reutilizável |
| **Resiliência** | Erros não tratados | Exception handlers + retry | Recuperação automática |
| **Resiliência** | Sem logging | JSON logging + Prometheus | Observabilidade total |

---

## 🧪 Testando a API

### Com curl (Linux/Mac):

```bash
# 1. Registrar usuário
curl -X POST "http://localhost:5000/api/v2/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"teste","email":"teste@test.com","password":"senha123"}'

# 2. Fazer login
TOKEN=$(curl -s -X POST "http://localhost:5000/api/v2/auth/login?username=teste&password=senha123" | jq -r '.access_token')

# 3. Criar URL
curl -X POST "http://localhost:5000/api/v2/urls/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"original_url":"https://google.com"}'

# 4. Listar suas URLs
curl -X GET "http://localhost:5000/api/v2/urls/user/my-urls?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN"
```

### Com Postman:

1. Importe a coleção: `postman_collection.json` (será criada)
2. Configure a variável `base_url` como `http://localhost:5000`
3. Execute os endpoints na ordem

---

## 🔒 Segurança

- ✅ Senhas hasheadas com bcrypt
- ✅ JWT para autenticação stateless
- ✅ CORS configurado
- ✅ Validação de entrada com Pydantic
- ✅ Proteção contra SQL Injection (SQLAlchemy ORM)
- ⚠️ **TODO**: Rate limiting
- ⚠️ **TODO**: HTTPS/TLS
- ⚠️ **TODO**: CSRF protection

---

## 📝 Licença

MIT License

---

## 👨‍💻 Autor

Desenvolvido como trabalho para INF1319 - Tópicos em Computação VII

---

## 📞 Suporte

Para dúvidas ou problemas:

1. Verifique o `docker-compose logs app`
2. Acesse `/docs` para documentação interativa
3. Verifique as variáveis de ambiente em `.env`
