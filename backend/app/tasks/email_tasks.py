"""Tasks de email (dev: log no console)."""

from app.tasks.celery_app import celery_app
from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


def _send_email_or_log(to: str, subject: str, body: str) -> None:
    """Em dev, loga o email. Em prod, envia via SMTP."""
    if not settings.smtp_host:
        logger.info(
            "📧 [DEV] Email simulado",
            to=to,
            subject=subject,
            body_preview=body[:100],
        )
        return

    import smtplib
    from email.mime.text import MIMEText

    msg = MIMEText(body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        if settings.smtp_user:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_pass)
        server.send_message(msg)


@celery_app.task
def send_welcome_email(user_email: str, user_name: str):
    """Envia email de boas-vindas."""
    body = f"""
    <h2>Bem-vindo ao Athletic AI, {user_name}! 🏋️</h2>
    <p>Sua conta foi criada com sucesso.</p>
    <p>Comece registrando seu primeiro treino!</p>
    """
    _send_email_or_log(user_email, "Bem-vindo ao Athletic AI!", body)


@celery_app.task
def send_weekly_reminder(user_email: str, user_name: str):
    """Lembrete semanal de treino."""
    body = f"""
    <h2>Hora de treinar, {user_name}! 💪</h2>
    <p>Não esqueça de registrar seus treinos desta semana.</p>
    """
    _send_email_or_log(user_email, "Lembrete semanal — Athletic AI", body)
