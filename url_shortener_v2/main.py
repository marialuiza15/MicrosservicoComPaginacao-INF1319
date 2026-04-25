from fastapi import FastAPI
from models import Base
from database import engine
from config import get_settings
from routers import auth, urls, redirect

Base.metadata.create_all(bind=engine)

settings = get_settings()

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
)

app.include_router(auth.router)
app.include_router(urls.router)
app.include_router(redirect.router)