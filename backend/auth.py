from datetime import datetime, timedelta
from jose import jwt
from passlib.hash import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.core.config import settings
from backend.db import get_db
from backend.models import User

bearer = HTTPBearer()

def hash_pw(p: str) -> str: return bcrypt.hash(p)
def verify_pw(p: str, h: str) -> bool: return bcrypt.verify(p, h)

def make_token(user_id: int) -> str:
    payload = {"sub": str(user_id), "exp": datetime.utcnow() + timedelta(days=7)}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)) -> User:
    try:
        data = jwt.decode(creds.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.get(User, int(data["sub"]))
    if not user: raise HTTPException(status_code=401, detail="User not found")
    return user