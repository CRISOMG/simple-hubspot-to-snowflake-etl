import os
import secrets
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import EmailStr

from ..database import db
from ..schemas import TokenResponse

load_dotenv()

# --- Configuración de JWT (leído desde .env) ---
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# --- Configuración de Hashing (para el Magic Token) ---
# Usamos bcrypt para hashear el magic token en la DB
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hashea una contraseña (o token) usando bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica un hash de bcrypt."""
    return pwd_context.verify(plain_password, hashed_password)


# --- Lógica de JWT ---

# OAuth2PasswordBearer es una clase de FastAPI que "sabe"
# cómo buscar un token 'Bearer' en el header 'Authorization'.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="verify-login"
)  # Apunta a nuestro endpoint de login


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Crea un nuevo JWT (token de sesión)."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


# --- El "Middleware" de Seguridad (como una Dependencia) ---


async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """
    Esta es la dependencia de seguridad.
    Se ejecuta en cada endpoint protegido.
    Valida el JWT y devuelve el email del usuario.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

        # 'sub' (subject) es el nombre estándar para el identificador del usuario
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

        # En una app real, aquí buscarías al usuario en la DB
        # Por ahora, solo devolvemos el email
        return email

    except JWTError:
        raise credentials_exception


def create_magic_token(email: EmailStr) -> str:

    magic_token = secrets.token_urlsafe(32)
    token_hash = get_password_hash(magic_token)
    expires = datetime.now(timezone.utc) + timedelta(minutes=15)

    db["magic_tokens"][email] = {
        "token_hash": token_hash,
        "expires": expires,
        "used": False,
    }

    return magic_token


def verify_magic_token(email: EmailStr, token: str) -> TokenResponse:

    token_data = db["magic_tokens"].get(email)

    if not token_data:
        raise HTTPException(
            status_code=404, detail="Email no encontrado o token no solicitado"
        )

    if token_data["used"]:
        raise HTTPException(status_code=400, detail="Este enlace ya fue utilizado")

    if token_data["expires"] < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="El enlace ha expirado")

    if not verify_password(token, token_data["token_hash"]):
        raise HTTPException(status_code=400, detail="Token inválido")

    token_data["used"] = True

    expires_delta = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": email},  # "sub" = subject = el email del usuario
        expires_delta=expires_delta,
    )

    return TokenResponse(access_token=access_token)
