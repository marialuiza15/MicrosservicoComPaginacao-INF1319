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

    existing_url = db.query(URL).filter(
        URL.user_id == current_user.id,
        URL.original_url == url_data.original_url
    ).first()

    if existing_url:
        return serialize_url(existing_url, request)

    short_code = generate_unique_short_code(db)
     
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
    
    total = db.query(func.count(URL.id)).filter(URL.user_id == current_user.id).scalar()
    
    total_pages = (total + page_size - 1) // page_size
    skip = (page - 1) * page_size
    
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
    
    url = db.query(URL).filter(URL.id == payload.url_id).first()
    
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL não encontrada"
        )
    
    if url.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para deletar esta URL"
        )

    db.delete(url)
    db.commit()
    
    return None