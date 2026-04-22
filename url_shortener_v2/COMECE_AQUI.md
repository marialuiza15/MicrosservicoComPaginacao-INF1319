# 🚀 GUIA RÁPIDO DE INÍCIO

## Erro Encontrado

```
ERROR: required variable SECRET_KEY is missing a value
```

✅ **Esse erro é NORMAL e ESPERADO** - é segurança funcionando!

---

## Solução (3 Passos Simples)

### Passo 1: Arquivo .env já foi criado ✅

O arquivo `.env` já vem no projeto com:
- ✅ SECRET_KEY gerado aleatoriamente
- ✅ DATABASE_URL configurada
- ✅ Todas as variáveis prontas

**Você NÃO precisa fazer nada!** O arquivo está pronto.

### Passo 2: Iniciar Docker Compose

```bash
# Dentro da pasta url_shortener_v2/
docker-compose up --build
```

Agora funcionará porque o `.env` está configurado!

### Passo 3: Testar a API

```bash
# Acessar documentação
http://localhost:5000/docs

# Ou fazer primeira requisição
curl http://localhost:5000/health
```

---

## 📁 Estrutura de Arquivos

```
url_shortener_v2/
├── .env                    ← ARQUIVO DE CONFIGURAÇÃO (já criado!)
├── .env.example            ← Exemplo (não use, use o .env)
├── docker-compose.yml
├── Dockerfile
├── main.py
└── ... (outros arquivos)
```

---

## ⚠️ IMPORTANTE

### .env é CRÍTICO para Segurança

- ✅ O arquivo `.env` já vem com configurações prontas
- ✅ Não precisa editar nada
- ✅ As credenciais estão seguras
- ❌ **NUNCA** faça git commit do `.env`
- ❌ **NUNCA** compartilhe o `.env`

### Se precisar mudar algo:

1. **Banco de dados diferente?**
   ```
   DATABASE_URL=postgresql://seu_usuario:sua_senha@seu_host:5432/seu_banco
   ```

2. **SECRET_KEY comprometida?**
   Gere uma nova:
   ```bash
   python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
   ```

---

## ✅ Próximos Passos

1. ✅ Arquivo `.env` já está configurado
2. ⏭️ Execute: `docker-compose up --build`
3. ⏭️ Aguarde o Docker inicializar
4. ⏭️ Acesse: `http://localhost:5000/docs`
5. ⏭️ Registre seu primeiro usuário
6. ⏭️ Teste os endpoints

---

## 🐳 Comando para Rodar

```bash
cd url_shortener_v2
docker-compose up --build
```

**Pronto!** Agora funcionará sem erros de SECRET_KEY! 🎉
