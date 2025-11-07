import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, EmailStr, Field
from .auth import create_magic_token, verify_magic_token, get_current_user
from .services.email import send_magic_link_email
from .schemas import TokenResponse

load_dotenv()

API_NAME = os.getenv("API_NAME")
BASE_API_DOMAIN = os.getenv("BASE_API_DOMAIN")


class LogDataIn(BaseModel):
    email: EmailStr = Field(..., example="usuario@ejemplo.com")


app = FastAPI(
    title=API_NAME,
    description="Una API simple para recibir datos de Snowflake.",
)


@app.get("/")
def get_root():
    return {"status": "Servicio activo."}


@app.post(
    "/log-in",
)
async def login(
    login_data: LogDataIn,
):
    try:
        magic_token = create_magic_token(login_data.email)

        magic_link = f"{BASE_API_DOMAIN}/verify-login?token={magic_token}&email={login_data.email}"

        send_magic_link_email(email_to=login_data.email, magic_link=magic_link)

        return {
            "message": "Si tu email está registrado, recibirás un enlace de inicio de sesión."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@app.get(
    "/verify-login",
    summary="Verificar el enlace mágico y obtener JWT",
    response_model=TokenResponse,
    tags=["Autenticación"],
)
async def verify_login(token: str, email: EmailStr):
    return verify_magic_token(email, token)


@app.get("/users/me", summary="Verificar quién soy (Protegido)", tags=["Usuarios"])
async def read_users_me(current_user: str = Depends(get_current_user)):
    """Un endpoint simple para probar que el JWT funciona."""
    return {"email_autenticado": current_user}
