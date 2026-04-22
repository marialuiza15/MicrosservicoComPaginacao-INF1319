from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from models import URL
from database import get_db

router = APIRouter(tags=["redirect"])


@router.get("/{short_code}")
def redirect_to_url(
    short_code: str,
    db: Session = Depends(get_db)
):
    """
    Redireciona para a URL original baseado no código curto
    
    Incrementa o contador de cliques
    """
    
    url = db.query(URL).filter(URL.short_code == short_code).first()
    
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL não encontrada"
        )
    
    if not url.is_active:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Esta URL foi deletada"
        )
    
    # Incrementa o contador de hits
    url.hits += 1
    db.commit()
    
    # Redireciona para a URL original
    return RedirectResponse(url=url.original_url, status_code=301)


@router.get("/stats/{short_code}")
def get_stats(
    short_code: str,
    db: Session = Depends(get_db)
):
    """
    Retorna estatísticas de uma URL encurtada
    """
    
    url = db.query(URL).filter(URL.short_code == short_code).first()
    
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL não encontrada"
        )
    
    return {
        "short_code": url.short_code,
        "original_url": url.original_url,
        "hits": url.hits,
        "is_active": url.is_active,
        "created_at": url.created_at
    }
