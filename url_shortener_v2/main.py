from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import Base
from database import engine
from config import get_settings
from routers import auth, urls, redirect

# Criar tabelas no banco (se não existirem)
Base.metadata.create_all(bind=engine)

settings = get_settings()

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.API_TITLE,
    description="API de encurtador de URLs com autenticação JWT",
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)
app.include_router(urls.router)
app.include_router(redirect.router)


@app.get("/")
def read_root():
    """Endpoint raiz da API"""
    return {
        "message": "Bem-vindo à URL Shortener API v2",
        "docs": "/docs",
        "version": settings.API_VERSION
    }


@app.get("/health")
def health_check():
    """Health check da API"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
