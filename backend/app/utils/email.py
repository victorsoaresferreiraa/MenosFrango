"""
Utilitário de envio de e-mail.
Em dev (EMAIL_DEV_LOG=True), apenas loga no console.
Em prod, usa SMTP configurado.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def send_email(
    to: str,
    subject: str,
    body_html: str,
    body_text: Optional[str] = None,
) -> bool:
    """
    Envia e-mail. Em dev, apenas loga.
    Retorna True se enviado/logado com sucesso.
    """
    if settings.EMAIL_DEV_LOG or not settings.SMTP_HOST:
        logger.info(
            "email_dev_log",
            to=to,
            subject=subject,
            body_preview=body_text[:100] if body_text else body_html[:100],
        )
        print(f"\n{'='*60}")
        print(f"📧 EMAIL (DEV MODE)")
        print(f"Para: {to}")
        print(f"Assunto: {subject}")
        print(f"Conteúdo: {body_text or body_html[:200]}")
        print(f"{'='*60}\n")
        return True

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to
        msg["Subject"] = subject

        if body_text:
            msg.attach(MIMEText(body_text, "plain"))
        msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.sendmail(settings.SMTP_FROM, to, msg.as_string())

        logger.info("email_sent", to=to, subject=subject)
        return True

    except Exception as e:
        logger.error("email_error", error=str(e), to=to)
        return False


def send_welcome_email(user_name: str, user_email: str) -> bool:
    """E-mail de boas-vindas."""
    subject = f"Bem-vindo ao Athletic AI, {user_name}! 🏋️"
    body_html = f"""
    <h2>Olá, {user_name}! 🏋️</h2>
    <p>Seu cadastro no <strong>Athletic AI</strong> foi realizado com sucesso.</p>
    <p>Comece registrando seu primeiro treino e deixe a IA criar seu plano personalizado!</p>
    <br>
    <p>Acesse: <a href="http://localhost:3000">Athletic AI</a></p>
    <p>Equipe Athletic AI</p>
    """
    body_text = f"Olá, {user_name}! Bem-vindo ao Athletic AI. Acesse: http://localhost:3000"
    return send_email(user_email, subject, body_html, body_text)
