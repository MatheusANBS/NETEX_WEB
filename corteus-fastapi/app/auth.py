"""
Módulo de autenticação segura usando JWT
"""
import jwt
import secrets
from datetime import datetime, timedelta
from typing import Optional
from decouple import config
from fastapi import Request, HTTPException, status

# Chave secreta para assinar os tokens JWT
# Em produção, isso deve estar em uma variável de ambiente
JWT_SECRET_KEY = config("JWT_SECRET_KEY", default=secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24  # Token expira em 24 horas

class AuthManager:
    """Gerenciador de autenticação usando JWT"""
    
    @staticmethod
    def create_admin_token(admin_password: str, provided_password: str) -> str:
        """
        Cria um token JWT para o admin se a senha estiver correta
        
        Args:
            admin_password: Senha correta do admin
            provided_password: Senha fornecida pelo usuário
            
        Returns:
            Token JWT assinado
            
        Raises:
            HTTPException: Se a senha estiver incorreta
        """
        if provided_password != admin_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Senha de administrador incorreta"
            )
        
        # Criar payload do token
        payload = {
            "role": "admin",
            "authenticated": True,
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            "iat": datetime.utcnow(),
            "sub": "corteus_admin"
        }
        
        # Gerar e retornar o token
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token
    
    @staticmethod
    def verify_admin_token(token: str) -> bool:
        """
        Verifica se o token JWT é válido e representa um admin autenticado
        
        Args:
            token: Token JWT a ser verificado
            
        Returns:
            True se o token for válido e representar um admin, False caso contrário
        """
        try:
            # Decodificar e verificar o token
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            # Verificar se é um token de admin válido
            return (
                payload.get("role") == "admin" and
                payload.get("authenticated") is True and
                payload.get("sub") == "corteus_admin"
            )
            
        except jwt.ExpiredSignatureError:
            # Token expirado
            return False
        except jwt.InvalidTokenError:
            # Token inválido
            return False
        except Exception:
            # Qualquer outro erro
            return False
    
    @staticmethod
    def get_admin_cookie_from_request(request: Request) -> Optional[str]:
        """
        Extrai o cookie de autenticação da requisição
        
        Args:
            request: Objeto Request do FastAPI
            
        Returns:
            Token JWT do cookie ou None se não existir
        """
        return request.cookies.get('corteus_admin_token')
    
    @staticmethod
    def is_admin_authenticated(request: Request) -> bool:
        """
        Verifica se o usuário está autenticado como admin através do cookie JWT
        
        Args:
            request: Objeto Request do FastAPI
            
        Returns:
            True se autenticado como admin, False caso contrário
        """
        token = AuthManager.get_admin_cookie_from_request(request)
        if not token:
            return False
        
        return AuthManager.verify_admin_token(token)

# Instância global do gerenciador de autenticação
auth_manager = AuthManager()
