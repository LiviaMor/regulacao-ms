"""
Sistema de autenticação compartilhado entre microserviços
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import List, Optional
import os
import logging

from .database import get_db, Usuario

logger = logging.getLogger(__name__)

# Configurações
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "regulacao_jwt_secret_key_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

# Configurações de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar senha - versão simplificada para desenvolvimento"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.warning(f"Erro na verificação de senha com hash, tentando comparação direta: {e}")
        # Fallback para desenvolvimento - comparação direta
        return plain_password == hashed_password

def get_password_hash(password: str) -> str:
    """Hash de senha - versão simplificada para desenvolvimento"""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.warning(f"Erro no hash de senha, usando senha direta: {e}")
        # Fallback para desenvolvimento
        return password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user

def require_role(allowed_roles: List[str]):
    def role_checker(current_user: Usuario = Depends(get_current_user)):
        if current_user.tipo_usuario not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker