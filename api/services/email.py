import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
API_NAME = os.getenv("API_NAME")


def send_magic_link_email(email_to: str, magic_link: str):
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("Error: GMAIL_USER o GMAIL_APP_PASSWORD no están en .env")
        return False

    msg = EmailMessage()
    msg.set_content(
        f'Para usar la api "{API_NAME}" inicia sesión con:\n{magic_link}\n\n'
        "Este enlace expira en 15 minutos y solo puede usarse una vez."
    )
    msg["Subject"] = "Tu enlace de inicio de sesión"
    msg["From"] = GMAIL_USER
    msg["To"] = email_to

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Email enviado exitosamente a {email_to}")
        return True
    except Exception as e:
        print(f"Error al enviar email: {e}")
        return False
