# API Examples

### Autenticação

#### 1. Registrar novo usuário

```bash
curl -X POST "http://localhost:5000/api/v2/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "joao",
    "password": "senha123"
  }'
```

**Resposta (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "joao",
  "email": "joao@example.com",
  "is_admin": false,
  "created_at": "2024-01-15T10:30:00"
}
```

#### 2. Fazer login

```bash
curl -X POST "http://localhost:5000/api/v2/auth/login?username=joao&password=senha123"
```

**Resposta (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2FvIiwi...",
  "token_type": "bearer"
}
```

**Guardar o token para usar em requisições autenticadas:**
```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2FvIiwi..."
```

---

### Endpoints de URL

#### 3. Criar URL encurtada

```bash
curl -X POST "http://localhost:5000/api/v2/urls/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "original_url": "https://www.ejemplo.com/pagina-muito-longa-e-chata"
  }'
```

**Resposta (201 Created):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "original_url": "https://www.ejemplo.com/pagina-muito-longa-e-chata",
  "short_code": "x7kP2w",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-01-15T10:35:00",
  "is_active": true,
  "hits": 0
}
```

#### 4️⃣ LISTAR URLs DO USUÁRIO (Endpoint 2 - Obrigatório)

```bash
curl -X GET "http://localhost:5000/api/v2/urls/user/my-urls?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Parâmetros:**
- `page`: número da página (padrão: 1)
- `page_size`: itens por página (padrão: 10, máx: 100)

**Resposta (200 OK):**
```json
{
  "total": 25,
  "page": 1,
  "page_size": 10,
  "total_pages": 3,
  "items": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "original_url": "https://www.google.com",
      "short_code": "x7kP2w",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2024-01-15T10:35:00",
      "is_active": true,
      "hits": 5
    }
  ],
  "has_next": true,
  "has_previous": false
}
```

#### 5️⃣ LISTAR TODAS AS URLs (Endpoint 1 - Admin Only)

```bash
curl -X GET "http://localhost:5000/api/v2/urls/admin/all?page=1&page_size=50" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Nota:** Apenas usuários com `is_admin=true` podem acessar este endpoint.

**Resposta:** Mesmo formato do endpoint de usuário, mas com todas as URLs do sistema.

#### 6️⃣ DELETAR URL (Endpoint 3 - Obrigatório)

```bash
curl -X DELETE "http://localhost:5000/api/v2/urls/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url_id": "660e8400-e29b-41d4-a716-446655440001"}'
```

**Resposta (204 No Content):** Sem corpo de resposta

**Erros possíveis:**
```bash
# 404 - URL não encontrada
# 403 - Sem permissão (não é seu URL e não é admin)
```

#### 7. Obter informações de uma URL

```bash
curl -X GET "http://localhost:5000/api/v2/urls/x7kP2w"
```

**Resposta (200 OK):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "original_url": "https://www.google.com",
  "short_code": "x7kP2w",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-01-15T10:35:00",
  "is_active": true,
  "hits": 10
}
```

---

### Redirecionamento

#### 8. Redirecionar para URL original

```bash
curl -L "http://localhost:5000/x7kP2w"
```

**Resposta:** Redirecionamento (HTTP 301) para a URL original

**Nota:** O hit count é incrementado automaticamente

#### 9. Obter estatísticas

```bash
curl -X GET "http://localhost:5000/stats/x7kP2w"
```

**Resposta (200 OK):**
```json
{
  "short_code": "x7kP2w",
  "original_url": "https://www.google.com",
  "hits": 15,
  "is_active": true,
  "created_at": "2024-01-15T10:35:00"
}
```

---

## 🧪 Fluxo Completo de Teste

```bash
#!/bin/bash

# 1. Registrar usuário
echo "📝 Registrando usuário..."
REGISTER=$(curl -s -X POST "http://localhost:5000/api/v2/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "teste_'$(date +%s)'",
    "email": "teste_'$(date +%s)'@example.com",
    "password": "senha123"
  }')
echo $REGISTER | jq '.'

# 2. Fazer login
echo -e "\n🔐 Fazendo login..."
LOGIN=$(curl -s -X POST "http://localhost:5000/api/v2/auth/login?username=teste_'$(date +%s)'&password=senha123")
TOKEN=$(echo $LOGIN | jq -r '.access_token')
echo "Token: $TOKEN"

# 3. Criar URL
echo -e "\n🔗 Criando URL encurtada..."
CREATE=$(curl -s -X POST "http://localhost:5000/api/v2/urls/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "original_url": "https://www.github.com"
  }')
SHORT_CODE=$(echo $CREATE | jq -r '.short_code')
URL_ID=$(echo $CREATE | jq -r '.id')
echo $CREATE | jq '.'

# 4. Listar URLs do usuário
echo -e "\n📋 Listando suas URLs..."
curl -s -X GET "http://localhost:5000/api/v2/urls/user/my-urls" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# 5. Redirecionar
echo -e "\n↪️  Testando redirecionamento..."
curl -s -I "http://localhost:5000/$SHORT_CODE"

# 6. Deletar URL
echo -e "\n🗑️  Deletando URL..."
curl -s -X DELETE "http://localhost:5000/api/v2/urls/$URL_ID" \
  -H "Authorization: Bearer $TOKEN" -w "\nStatus: %{http_code}\n"

echo -e "\n✅ Testes concluídos!"
```

---

## 📝 Coleção Postman

Importe esta coleção no Postman para testar facilmente:

```json
{
  "info": {
    "name": "URL Shortener v2",
    "description": "API de encurtador de URLs",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Register",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.environment.set('user_id', pm.response.json().id);"
                ]
              }
            }
          ],
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"username\": \"{{$randomUserName}}\",\n  \"email\": \"{{$randomEmail}}\",\n  \"password\": \"senha123\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/api/v2/auth/register",
              "host": ["{{base_url}}"],
              "path": ["api", "v2", "auth", "register"]
            }
          }
        },
        {
          "name": "Login",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.environment.set('token', pm.response.json().access_token);"
                ]
              }
            }
          ],
          "request": {
            "method": "POST",
            "url": {
              "raw": "{{base_url}}/api/v2/auth/login?username={{username}}&password=senha123",
              "host": ["{{base_url}}"],
              "path": ["api", "v2", "auth", "login"],
              "query": [
                {
                  "key": "username",
                  "value": "{{username}}"
                },
                {
                  "key": "password",
                  "value": "senha123"
                }
              ]
            }
          }
        }
      ]
    },
    {
      "name": "URLs",
      "item": [
        {
          "name": "Create URL",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              },
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"original_url\": \"https://www.google.com\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/api/v2/urls/",
              "host": ["{{base_url}}"],
              "path": ["api", "v2", "urls", ""]
            }
          }
        },
        {
          "name": "List My URLs",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/api/v2/urls/user/my-urls?page=1&page_size=10",
              "host": ["{{base_url}}"],
              "path": ["api", "v2", "urls", "user", "my-urls"],
              "query": [
                {
                  "key": "page",
                  "value": "1"
                },
                {
                  "key": "page_size",
                  "value": "10"
                }
              ]
            }
          }
        },
        {
          "name": "List All URLs (Admin)",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{admin_token}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/api/v2/urls/admin/all?page=1&page_size=50",
              "host": ["{{base_url}}"],
              "path": ["api", "v2", "urls", "admin", "all"],
              "query": [
                {
                  "key": "page",
                  "value": "1"
                },
                {
                  "key": "page_size",
                  "value": "50"
                }
              ]
            }
          }
        },
        {
          "name": "Delete URL",
          "request": {
            "method": "DELETE",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/api/v2/urls/{{url_id}}",
              "host": ["{{base_url}}"],
              "path": ["api", "v2", "urls", "{{url_id}}"]
            }
          }
        }
      ]
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:5000"
    },
    {
      "key": "token",
      "value": ""
    },
    {
      "key": "admin_token",
      "value": ""
    }
  ]
}
```

**Para usar:**
1. Importe o JSON no Postman
2. Configure a variável `base_url` = `http://localhost:5000`
3. Execute os endpoints em ordem

---

## 🐛 Debugging

### Ver todas as queries SQL

```python
# Em main.py, antes de criar app:
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### Testar com httpie (mais legível que curl)

```bash
# Instalar
pip install httpie

# Usar
http POST http://localhost:5000/api/v2/auth/register \
  username=teste email=teste@example.com password=senha123

http GET http://localhost:5000/api/v2/urls/user/my-urls \
  "Authorization: Bearer $TOKEN"
```

### Testar com Python

```python
import requests

# Login
response = requests.post(
    "http://localhost:5000/api/v2/auth/login",
    params={"username": "teste", "password": "senha"}
)
token = response.json()["access_token"]

# Criar URL
response = requests.post(
    "http://localhost:5000/api/v2/urls/",
    headers={"Authorization": f"Bearer {token}"},
    json={"original_url": "https://example.com"}
)
print(response.json())

# Listar URLs
response = requests.get(
    "http://localhost:5000/api/v2/urls/user/my-urls",
    headers={"Authorization": f"Bearer {token}"}
)
print(response.json())
```

