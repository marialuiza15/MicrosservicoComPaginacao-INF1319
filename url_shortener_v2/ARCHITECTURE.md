# Arquitetura do Projeto URL Shortener v2

## 📊 Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                        Cliente / Navegador                       │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Application                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      main.py                              │   │
│  │  (FastAPI app, CORS, middleware, routers)                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  routers/    │  │              │  │                      │  │
│  │  ├─ auth.py  │  │  schemas.py  │  │    config.py         │  │
│  │  ├─ urls.py  │  │              │  │                      │  │
│  │  └─ redirect │  │ (Pydantic    │  │ (Settings, env       │  │
│  │                 │  validation)  │  │  vars)               │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            auth.py - JWT & Segurança                      │   │
│  │  ├─ verify_password()                                     │   │
│  │  ├─ get_password_hash()                                   │   │
│  │  ├─ create_access_token()                                 │   │
│  │  ├─ get_current_user()                                    │   │
│  │  └─ get_current_admin_user()                              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            utils.py - Funções Auxiliares                  │   │
│  │  ├─ generate_short_code()                                 │   │
│  │  └─ generate_unique_short_code()                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────┬────────────────────────────────────────┘
                         │ SQLAlchemy ORM
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SQLAlchemy Models                             │
│  ┌──────────────┐        ┌──────────────┐                       │
│  │    User      │        │     URL      │                       │
│  ├──────────────┤        ├──────────────┤                       │
│  │ id (PK)      │────────▶│ id (PK)      │                       │
│  │ username     │ 1    n  │ short_code   │                       │
│  │ email        │         │ original_url │                       │
│  │ password     │         │ user_id (FK) │                       │
│  │ is_admin     │         │ hits         │                       │
│  │ created_at   │         │ created_at   │                       │
│  └──────────────┘         │ is_active    │                       │
│                           └──────────────┘                       │
└─────────────────────────┬────────────────────────────────────────┘
                         │ psycopg2
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                           │
│  ┌──────────────────┐        ┌──────────────────┐               │
│  │   users table    │        │    urls table    │               │
│  ├──────────────────┤        ├──────────────────┤               │
│  │ id (uuid)        │────────▶│ id (uuid)        │               │
│  │ username         │ 1    n  │ short_code       │               │
│  │ email            │         │ original_url     │               │
│  │ hashed_password  │         │ user_id (FK)     │               │
│  │ is_admin         │         │ hits             │               │
│  │ created_at       │         │ created_at       │               │
│  └──────────────────┘         │ is_active        │               │
│                               └──────────────────┘               │
│  Índices:                                                         │
│  ├─ PK: id                    ├─ PK: id                          │
│  ├─ UNIQUE: username          ├─ UNIQUE: short_code              │
│  └─ UNIQUE: email             └─ FK: user_id                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Fluxo de Requisições

### 1. Autenticação (Login/Register)

```
POST /api/v2/auth/register
├─ Valida credenciais (Pydantic)
├─ Hash da senha (bcrypt)
├─ Insere usuário no DB
└─ Retorna user_id

POST /api/v2/auth/login
├─ Procura usuário no DB
├─ Verifica senha
├─ Cria JWT token
└─ Retorna token
```

### 2. Criar URL Encurtada

```
POST /api/v2/urls/
├─ Extrai user do JWT (get_current_user)
├─ Valida URL original (Pydantic)
├─ Gera short_code único
├─ Insere no DB
└─ Retorna URLResponse
```

### 3. Listar URLs do Usuário (Endpoint 2 - OBRIGATÓRIO)

```
GET /api/v2/urls/user/my-urls?page=1&page_size=10
├─ Extrai user do JWT
├─ Conta total de URLs do usuário
├─ Calcula paginação (offset, limit)
├─ Busca URLs da página
├─ Calcula has_next/has_previous
└─ Retorna PaginatedResponse
```

### 4. Listar TODAS as URLs (Endpoint 1 - Admin Only)

```
GET /api/v2/urls/admin/all?page=1&page_size=50
├─ Extrai user do JWT
├─ Verifica is_admin (get_current_admin_user)
├─ Conta total de TODAS as URLs
├─ Calcula paginação
├─ Busca URLs de TODOS os usuários
└─ Retorna PaginatedResponse
```

### 5. Deletar URL (Endpoint 3 - OBRIGATÓRIO)

```
DELETE /api/v2/urls/{url_id}
├─ Extrai user do JWT
├─ Busca URL no DB
├─ Verifica permissão:
│  ├─ IF owner ou admin:
│  │  └─ DELETE from DB
│  └─ ELSE:
│     └─ HTTPException 403
└─ Retorna 204 No Content
```

### 6. Redirecionar (GET /{short_code})

```
GET /{short_code}
├─ Busca URL no DB
├─ Incrementa hits
├─ Valida is_active
├─ Commit no DB
└─ Redireciona HTTP 301
```

---

## 🗂️ Estrutura de Pastas Detalhada

```
url_shortener_v2/
│
├── main.py                  # ⭐ Aplicação FastAPI principal
│   ├─ Cria app FastAPI
│   ├─ Configura CORS
│   ├─ Cria tabelas (Base.metadata.create_all)
│   ├─ Inclui routers
│   ├─ Endpoints: /, /health
│   └─ Executa: uvicorn main:app
│
├── config.py                # ⚙️ Configurações
│   └─ Settings class com variáveis de ambiente
│
├── models.py                # 🗄️ Modelos SQLAlchemy
│   ├─ User
│   │  ├─ id, username, email, password, is_admin
│   │  └─ relationship: urls
│   └─ URL
│      ├─ id, original_url, short_code, user_id, hits
│      └─ relationship: owner
│
├── schemas.py               # ✅ Schemas Pydantic (validação)
│   ├─ UserBase, UserCreate, UserResponse
│   ├─ URLBase, URLCreate, URLResponse, URLUpdate
│   ├─ PaginatedResponse (para os 2 endpoints de listagem)
│   ├─ Token, TokenData
│   └─ Validators para URLs (http:// ou https://)
│
├── database.py              # 🔌 Conexão com DB
│   ├─ engine (create_engine)
│   ├─ SessionLocal (sessionmaker)
│   └─ get_db() dependency
│
├── auth.py                  # 🔐 Autenticação JWT
│   ├─ pwd_context (bcrypt)
│   ├─ security (HTTPBearer)
│   ├─ verify_password()
│   ├─ get_password_hash()
│   ├─ create_access_token()
│   ├─ get_current_user() dependency
│   └─ get_current_admin_user() dependency
│
├── utils.py                 # 🛠️ Funções auxiliares
│   ├─ generate_short_code()
│   └─ generate_unique_short_code()
│
├── routers/                 # 📡 Endpoints (Routes)
│   ├─ __init__.py
│   ├─ auth.py               # Auth routes
│   │  ├─ POST /api/v2/auth/register
│   │  └─ POST /api/v2/auth/login
│   ├─ urls.py               # ⭐ URLs routes (3 ENDPOINTS OBRIGATÓRIOS)
│   │  ├─ POST /api/v2/urls/           (criar)
│   │  ├─ GET  /api/v2/urls/admin/all  (ENDPOINT 1: Admin - todas URLs)
│   │  ├─ GET  /api/v2/urls/user/my-urls (ENDPOINT 2: Usuário - suas URLs)
│   │  ├─ DELETE /api/v2/urls/{url_id} (ENDPOINT 3: Deletar URL)
│   │  └─ GET /api/v2/urls/{short_code} (get info)
│   └─ redirect.py           # Redirect routes
│      ├─ GET /{short_code}  (redireciona)
│      └─ GET /stats/{short_code} (stats)
│
├── seed.py                  # 🌱 Popular DB com dados teste
│   └─ Cria admin + usuário teste + URLs exemplo
│
├── test_main.py             # 🧪 Testes unitários
│   ├─ TestAuth
│   ├─ TestURLEndpoints
│   └─ TestRedirect
│
├── requirements.txt         # 📦 Dependências Python
├── Dockerfile               # 🐳 Imagem Docker
├── docker-compose.yml       # 🐳 Orquestração containers
├── entrypoint.sh            # 🚀 Script de inicialização
│
├── .env.example             # 📝 Exemplo de variáveis
├── .gitignore               # 🚫 Arquivos ignorados
│
├── README.md                # 📖 Documentação principal
├── DEVELOPMENT.md           # 💻 Guia de desenvolvimento
├── API_EXAMPLES.md          # 📚 Exemplos de requisições
│
└── ARCHITECTURE.md          # 🏗️ Este arquivo
```

---

## 💾 Modelo de Dados

### Tabela `users`

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_username ON users(username);
CREATE INDEX idx_email ON users(email);
```

### Tabela `urls`

```sql
CREATE TABLE urls (
    id UUID PRIMARY KEY,
    original_url VARCHAR(2048) NOT NULL,
    short_code VARCHAR(10) UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    hits INTEGER DEFAULT 0
);

CREATE INDEX idx_short_code ON urls(short_code);
CREATE INDEX idx_user_id ON urls(user_id);
CREATE INDEX idx_user_created ON urls(user_id, created_at);
CREATE INDEX idx_is_active ON urls(is_active);
```

---

## 🔀 Fluxo de Paginação (Endpoints 1 e 2)

```
Cliente envia: GET /api/v2/urls/user/my-urls?page=2&page_size=10

┌─────────────────────────────────────────┐
│  Validar parâmetros                     │
│  page=2, page_size=10                   │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│  Contar total                           │
│  total = db.query(count()).scalar()     │
│  total = 45                             │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│  Calcular total_pages                   │
│  total_pages = (45 + 10 - 1) // 10      │
│  total_pages = 5                        │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│  Calcular skip (offset)                 │
│  skip = (page - 1) * page_size          │
│  skip = (2 - 1) * 10 = 10               │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│  Executar query                         │
│  .offset(10).limit(10)                  │
│  Retorna: items 10-19                   │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│  Calcular has_next / has_previous       │
│  has_next = page < total_pages          │
│  has_next = 2 < 5 = True                │
│  has_previous = page > 1                │
│  has_previous = 2 > 1 = True            │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│  Retornar PaginatedResponse             │
│  {                                      │
│    "total": 45,                         │
│    "page": 2,                           │
│    "page_size": 10,                     │
│    "total_pages": 5,                    │
│    "items": [...],                      │
│    "has_next": true,                    │
│    "has_previous": true                 │
│  }                                      │
└─────────────────────────────────────────┘
```

---

## 🔒 Segurança

```
POST /api/v2/urls/ com Authorization header
│
├─ Extrai credenciais do header
│  Authorization: Bearer eyJhbGciOiJIUzI1NiI...
│
├─ Valida JWT
│  ├─ Verifica assinatura
│  ├─ Verifica expiração
│  └─ Extrai username
│
├─ Busca usuário no DB
│  └─ Se não existe: 401 Unauthorized
│
├─ Retorna User object
│  └─ Passa como dependency injection
│
└─ Usa user_id para criar URL
   └─ Garante que URL pertence ao usuário certo
```

---

## 📈 Escalabilidade

### Melhorias Propostas:

```
ATUAL:
┌──────────┐
│ FastAPI  │
└────┬─────┘
     │ 1 instância
     ▼
┌──────────────┐
│ PostgreSQL   │
└──────────────┘


FUTURO (Load Balancing):
     ┌──────────────────┐
     │   Nginx/HAProxy  │
     └────┬─────┬──────┬┘
          │     │      │
    ┌─────▼─┐ ┌─▼──┐ ┌─▼──┐
    │ App 1 │ │App2│ │App3│ (3+ instâncias)
    └─┬────┘ └──┬──┘ └─┬──┘
      │         │      │
      └─────┬───┴──┬───┘
            │      │
       ┌────▼──────▼────┐
       │ PostgreSQL     │ (com replicação)
       └───────┬────────┘
               │
       ┌──────▼────────┐
       │ Redis Cache   │ (para URLs populares)
       └───────────────┘
```

---

## 📊 Endpoints Resumo

| # | Método | Path | Auth | Descrição |
|---|--------|------|------|-----------|
| **1️⃣** | GET | `/api/v2/urls/admin/all` | Admin | **OBRIGATÓRIO**: Lista TODAS as URLs |
| **2️⃣** | GET | `/api/v2/urls/user/my-urls` | User | **OBRIGATÓRIO**: Lista suas URLs |
| **3️⃣** | DELETE | `/api/v2/urls/{url_id}` | User | **OBRIGATÓRIO**: Deleta URL |
| - | POST | `/api/v2/urls/` | User | Cria URL |
| - | GET | `/api/v2/urls/{short_code}` | - | Info sobre URL |
| - | POST | `/api/v2/auth/register` | - | Registra usuário |
| - | POST | `/api/v2/auth/login` | - | Login (retorna token) |
| - | GET | `/{short_code}` | - | Redireciona para URL original |
| - | GET | `/stats/{short_code}` | - | Estatísticas |

---

## 🚀 Deploy Checklist

- [ ] Usar variáveis de ambiente seguras
- [ ] Habilitar HTTPS/TLS
- [ ] Configurar rate limiting
- [ ] Adicionar logging centralizado
- [ ] Monitorar performance
- [ ] Fazer backup do banco
- [ ] Planejar disaster recovery
- [ ] Testar failover

