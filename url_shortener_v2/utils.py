import random
import string
from sqlalchemy.orm import Session
from models import URL


def generate_short_code(length: int = 6) -> str:
    """Gera um código curto aleatório"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def generate_unique_short_code(db: Session, length: int = 6, max_attempts: int = 10) -> str:
    """Gera um código curto único que não existe no banco"""
    for _ in range(max_attempts):
        code = generate_short_code(length)
        # Verifica se o código já existe
        if not db.query(URL).filter(URL.short_code == code).first():
            return code
    
    # Se todos os códigos colidirem, tenta com tamanho maior
    return generate_unique_short_code(db, length + 1, max_attempts)
