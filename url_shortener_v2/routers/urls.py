from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from schemas import URLCreate, URLDelete, URLResponse, PaginatedResponse
from models import URL, User
from database import get_db
from auth import get_current_user
from utils import generate_unique_short_code
from config import get_settings

router = APIRouter(prefix="/api/v2/urls", tags=["urls"])
settings = get_settings()


def build_short_url(request: Request, short_code: str) -> str:
    base_url = str(request.base_url).rstrip("/")
    return f"{base_url}/{short_code}"


def serialize_url(url: URL, request: Request) -> dict:
    return {
        "id": url.id,
        "original_url": url.original_url,
        "short_code": url.short_code,
        "short_url": build_short_url(request, url.short_code),
        "user_id": url.user_id,
        "created_at": url.created_at,
        "is_active": url.is_active,
        "hits": url.hits,
    }


@router.post("/new", response_model=URLResponse, status_code=201)
def create_short_url(
    url_data: URLCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria uma nova URL encurtada. 
    Requer autenticação pois a  URL será associada ao usuário autenticado.
    """
    # Verifica se a URL já foi encurtada por este usuário
    existing_url = db.query(URL).filter(
        URL.user_id == current_user.id,
        URL.original_url == url_data.original_url
    ).first()

    if existing_url:
        return serialize_url(existing_url, request)

    # Gera um código curto único
    short_code = generate_unique_short_code(db)
     
    # Cria a URL no banco
    new_url = URL(
        original_url=url_data.original_url,
        short_code=short_code,
        user_id=current_user.id,
        is_active=True
    )
    
    db.add(new_url)
    db.commit()
    db.refresh(new_url)
    
    return serialize_url(new_url, request)


@router.get("/my-all-urls", response_model=PaginatedResponse)
def list_all_user_urls(
    request: Request,
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE, description="Itens por página"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    📌 ENDPOINT 1: Lista TODAS as URLs DO SEU USUÁRIO COM PAGINAÇÃO
    
    **Segurança**: Você só acessa suas próprias URLs
    
    Query Parameters:
    - page: número da página (padrão: 1)
    - page_size: quantidade de itens por página (padrão: 10, máx: 100)
    """
    
    # Conta o total de URLs do usuário
    total = db.query(func.count(URL.id)).filter(URL.user_id == current_user.id).scalar()
    
    # Calcula valores de paginação
    total_pages = (total + page_size - 1) // page_size
    skip = (page - 1) * page_size
    
    # Busca as URLs do usuário na página
    urls = db.query(URL).filter(
        URL.user_id == current_user.id
    ).order_by(URL.created_at.desc()).offset(skip).limit(page_size).all()
    
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=[serialize_url(url, request) for url in urls],
        has_next=page < total_pages,
        has_previous=page > 1
    )


@router.delete("/remove", status_code=204)
def delete_url(
    payload: URLDelete,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    📌 ENDPOINT 3: Deleta uma URL encurtada
    
    **Segurança**: 
    - Você só pode deletar suas próprias URLs
    - Admin não pode deletar URLs de outros usuários
    
    Body Parameters:
    - url_id: ID da URL a ser deletada
    """
    
    # Busca a URL
    url = db.query(URL).filter(URL.id == payload.url_id).first()
    
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL não encontrada"
        )
    
    # Verifica permissão: usuário só pode deletar sua própria URL
    if url.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para deletar esta URL"
        )
    
    # Deleta a URL
    db.delete(url)
    db.commit()
    
    return None

