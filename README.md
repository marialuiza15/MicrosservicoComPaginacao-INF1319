# URL Shortener v2 - Encurtador de URLs - INF1319

## Visão Geral

URL Shortener v2 é um microsserviço em Python/FastAPI para criação, listagem e gerenciamento de URLs encurtadas. Ele foi desenvolvido para suportar usuários autenticados, oferecer paginação nas listagens e permitir controle de acesso às URLs de cada usuário.

### Principais funcionalidades
- Autenticação JWT com tokens expiráveis
- Geração automática de códigos curtos alfanuméricos
- Paginação configurável de resultados
- Isolamento de URLs por usuário
- Contador de acessos (hits)
- Validação básica de URLs
- Permissões de usuário vs administrador
- Redirecionamento público via `/{short_code}`

## Pré-requisitos
- Docker instalado
- Docker Compose instalado
- Variáveis de ambiente configuradas (via .env ou no ambiente)

## Como executar

```bash
cd url_shortener_v2

docker-compose up --build
```

A API ficará disponível em:

- `http://localhost:5000`
- Swagger UI: `http://localhost:5000/docs`
- Redoc: `http://localhost:5000/redoc`

### Parar o projeto

```bash
docker-compose down
```

## Variáveis de ambiente

As configurações principais são carregadas pela aplicação via `.env` e também expostas no Docker Compose.

### Obrigatórias
- `DATABASE_URL` — string de conexão com o PostgreSQL
- `SECRET_KEY` — chave secreta para assinatura de tokens JWT

### Opcionais e padrões do Docker
- `DB_USER` (default: `user`)
- `DB_PASSWORD` (default: `password`)
- `DB_NAME` (default: `encurtador`)
- `DB_PORT` (default: `5432`)
- `APP_PORT` (default: `5000`)

### Configurações internas
- `ALGORITHM` (default: `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (default: `30`)
- `DEFAULT_PAGE_SIZE` (default: `10`)
- `MAX_PAGE_SIZE` (default: `100`)

## Endpoints principais

### 1. Autenticação (`/api/v2/auth`)

#### POST `/register`
Registra um novo usuário.

**Request:**
```json
{
  "username": "seu_usuario",
  "password": "sua_senha"
}
```

**Response (201 Created):**
```json
{
  "username": "seu_usuario",
  "id": "abc123...",
  "is_admin": false,
  "created_at": "2026-04-25T10:30:00"
}
```

#### POST `/login`
Faz login e retorna token JWT.

**Request:**
```json
{
  "username": "seu_usuario",
  "password": "sua_senha"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 2. Gerenciamento de URLs (`/api/v2/urls`)

#### POST `/new`
Cria uma nova URL encurtada. Requer autenticação.

**Request:**
```json
{
  "original_url": "https://github.com/settings/copilot/features"
}
```

**Response (201 Created):**
```json
{
  "id": "a34dfu89",
  "original_url": "https://github.com/settings/copilot/features",
  "short_code": "1cbm9s",
  "short_url": "http://localhost:5000/1cbm9s",
  "user_id": "cba00876c48",
  "is_active": true,
  "created_at": "2026-04-25T10:30:00",
  "hits": 0
}
```

#### GET `/my-all-urls`
Lista as URLs do usuário autenticado com paginação.

**Query Parameters:**
- `page` (opcional): número da página (default: `1`)
- `page_size` (opcional): itens por página (default: `10`, máximo `100`)

**Example Request:**
```
GET /api/v2/urls/my-all-urls?page=1&page_size=10
Authorization: Bearer {seu_token}
```

**Response (200 OK):**
```json
{
  "total": 5,
  "page": 1,
  "page_size": 10,
  "total_pages": 1,
  "items": [
    {
      "id": "a34dfu89",
      "original_url": "https://github.com/settings/copilot/features",
      "short_code": "1cbm9s",
      "short_url": "http://localhost:5000/1cbm9s",
      "user_id": "cba00876c48",
      "is_active": true,
      "created_at": "2026-04-25T10:30:00",
      "hits": 3
    }
  ],
  "has_next": false,
  "has_previous": false
}
```

#### DELETE `/remove`
Deleta uma URL encurtada. Apenas o proprietário pode deletar.

**Request:**
```json
{
  "url_id": "a34dfu89"
}
```

**Response (204 No Content)**n

### 3. Redirecionamento público

#### GET `/{short_code}`
Redireciona para a URL original e incrementa contador de acessos.

**Example:**
```
GET /1cbm9s
→ 302 Redirect para https://github.com/settings/copilot/features
```

## Estrutura do projeto

```text
url_shortener_v2/
├── API_EXAMPLES.md
├── ARCHITECTURE.md
├── auth.py
├── config.py
├── database.py
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
├── main.py
├── models.py
├── requirements.txt
├── schemas.py
├── seed.py
├── utils.py
└── routers/
    ├── auth.py
    ├── redirect.py
    └── urls.py
```

## Melhorias recomendadas

### Performance
- Usar cache (Redis ou similar) para consultas de `short_code`
- Processar o incremento de `hits` de forma assíncrona ou em lote
- Evitar `OFFSET` em paginação para grandes volumes (usar cursor/keyset pagination)
- Garantir índices no banco para `short_code`, `user_id` e `created_at`

### Consistência de dados
- Usar soft delete para permitir auditoria e recuperação
- Garantir transações confiáveis em operações de criação e exclusão

### Arquitetura e acoplamento
- Separar camadas de rotas, serviços, repositórios e modelos
- Centralizar validações e regras de negócio fora dos handlers de rota

### Resiliência
- Adicionar rate limiting para evitar abuso
- Monitorar latência, erros e contagem de conexões
- Preparar o app para rodar em múltiplas instâncias

## Observações finais

Esse projeto já oferece a base de um serviço de encurtamento de URLs. Para torná-lo mais robusto em produção, priorize cache de redirecionamento, escrita assíncrona de métricas e paginação eficiente.
