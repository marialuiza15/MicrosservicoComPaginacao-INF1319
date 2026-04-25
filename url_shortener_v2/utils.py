import random
import string
from sqlalchemy.orm import Session
from models import URL

def generate_short_code(length: int = 6) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_unique_short_code(db: Session, length: int = 6, max_attempts: int = 10) -> str:
    for _ in range(max_attempts):
        code = generate_short_code(length)
        if not db.query(URL).filter(URL.short_code == code).first():
            return code
    
    return generate_unique_short_code(db, length + 1, max_attempts)