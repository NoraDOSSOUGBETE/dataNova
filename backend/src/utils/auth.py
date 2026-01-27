"""
Utilitaires d'authentification JWT
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from src.config import settings

# Configuration JWT
SECRET_KEY = getattr(settings, 'jwt_secret_key', "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 jours


def hash_password(password: str) -> str:
    """
    Hash un mot de passe avec bcrypt
    
    Args:
        password: Mot de passe en clair
        
    Returns:
        Hash bcrypt du mot de passe
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie qu'un mot de passe correspond à son hash
    
    Args:
        plain_password: Mot de passe en clair
        hashed_password: Hash bcrypt
        
    Returns:
        True si le mot de passe est correct
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un token JWT
    
    Args:
        data: Données à encoder dans le token (user_id, email, role, etc.)
        expires_delta: Durée de validité personnalisée (optionnel)
        
    Returns:
        Token JWT signé
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Vérifie et décode un token JWT
    
    Args:
        token: Token JWT à vérifier
        
    Returns:
        Données décodées du token ou None si invalide
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
