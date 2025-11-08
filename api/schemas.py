from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any


# --- Modelos del endpoint de Logging (de la pregunta anterior) ---
class LogDataIn(BaseModel):
    event_name: str = Field(..., example="user_signup")
    payload: Dict[str, Any] = Field(..., example={"user_id": 123, "source": "web"})


# --- Modelos para el nuevo flujo de Auth ---
class RequestLoginIn(BaseModel):
    """Body para solicitar un enlace de login."""

    email: EmailStr


class TokenResponse(BaseModel):
    """Respuesta al verificar el token con éxito (se entrega el JWT)."""

    access_token: str
    token_type: str = "bearer"


class LogInData(BaseModel):
    email: EmailStr = Field(..., example="usuario@ejemplo.com")
