from os import getenv
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
from typing import Any
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY  = getenv("SECRET_KEY")
ALGORITHM = getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict[str, Any]):
    to_encode = data.copy()
    
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    if not SECRET_KEY:
        raise RuntimeError("A variável de ambiente SECRET_KEY não foi configurada!")
    
    if not ALGORITHM:
        raise RuntimeError("A variável de ambiente ALGORITHM não foi configurada!")
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    