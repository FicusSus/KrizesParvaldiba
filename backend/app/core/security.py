"""
Security Utilities

This module provides security-related functionalities including:
- Password hashing
- JWT token management
- Authentication utilities
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple

import structlog
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

logger = structlog.get_logger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Security:
    """
    Security utilities class.
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password.
            
        Returns:
            str: Hashed password.
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password to verify.
            hashed_password: Hashed password to verify against.
            
        Returns:
            bool: True if password matches, False otherwise.
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Dictionary containing token claims.
            expires_delta: Optional timedelta for expiration.
            
        Returns:
            str: Encoded JWT token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT refresh token.
        
        Args:
            data: Dictionary containing token claims.
            expires_delta: Optional timedelta for expiration.
            
        Returns:
            str: Encoded JWT token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """
        Decode and validate a JWT token.
        
        Args:
            token: JWT token string.
            
        Returns:
            Optional[dict]: Decoded token claims or None if invalid.
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            return payload
        except JWTError as e:
            logger.error("JWT decode error", error=str(e))
            return None
    
    @staticmethod
    def generate_api_key() -> Tuple[str, str]:
        """
        Generate a new API key pair (key and hash).
        
        Returns:
            Tuple[str, str]: (api_key, api_key_hash)
        """
        api_key = secrets.token_urlsafe(32)
        api_key_hash = Security.hash_password(api_key)
        return api_key, api_key_hash
    
    @staticmethod
    def verify_api_key(api_key: str, api_key_hash: str) -> bool:
        """
        Verify an API key against its hash.
        
        Args:
            api_key: API key to verify.
            api_key_hash: Stored hash of the API key.
            
        Returns:
            bool: True if API key is valid, False otherwise.
        """
        return Security.verify_password(api_key, api_key_hash)
    
    @staticmethod
    def generate_reset_token() -> str:
        """
        Generate a password reset token.
        
        Returns:
            str: Reset token.
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_reset_token(token: str) -> str:
        """
        Hash a reset token for storage.
        
        Args:
            token: Reset token to hash.
            
        Returns:
            str: Hashed token.
        """
        return hashlib.sha256(token.encode()).hexdigest()


# Singleton instance
security = Security()