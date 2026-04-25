"""
Serviço de e-mail.
Em modo desenvolvimento (APP_ENV=local), faz log no console.
Em produção, envia via SMTP.
"""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EmailService:
    """Envia e-mails ou loga no console em desenvolvimento."""

    def send(self, to: str, subject: str, html_body: str) -> None:
        """Envia e-mail ou loga dependendo do ambiente."""
        if settings.is_dev or not settings.smtp_host:
            self._log_email(to, subject, html_body)
        else:
            self._send_smtp(to, subject, html_body)

    def _log_email(self, to: str, subject: str, body: str) -> None:
        """Loga e-mail no console (modo dev)."""
        logger.info(
            "📧 [EMAIL DEV] Para: %s | Assunto: %s\n%s",
            to, subject, body[:500]
        )

    def _send_smtp(self, to: str, subject: str, html_body: str) -> None:
        """Envia e-mail real via SMTP."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.smtp_from
        msg["To"] = to
        msg.attach(MIMEText(html_body, "html"))

        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_pass)
                server.sendmail(settings.smtp_from, to, msg.as_string())
            logger.info("E-mail enviado para %s — %s", to, subject)
        except Exception as e:
            logger.error("Falha ao enviar e-mail para %s: %s", to, str(e))

    def send_welcome(self, to: str, name: str) -> None:
        """E-mail de boas-vindas após registro."""
        self.send(
            to=to,
            subject="Bem-vindo ao Athletic AI! 🏋️",
            html_body=f"""
            <h1>Olá, {name}!</h1>
            <p>Sua conta no <strong>Athletic AI</strong> foi criada com sucesso.</p>
            <p>Comece registrando seus primeiros treinos e acompanhe sua evolução!</p>
            <p>Acesse: <a href="http://localhost:3000">Athletic AI</a></p>
            """,
        )

    def send_report_ready(self, to: str, name: str, report_url: str) -> None:
        """Notificação de relatório mensal disponível."""
        self.send(
            to=to,
            subject="Seu relatório mensal está pronto! 📊",
            html_body=f"""
            <h1>Olá, {name}!</h1>
            <p>Seu relatório mensal de progresso está disponível.</p>
            <p><a href="{report_url}">Clique aqui para baixar o PDF</a></p>
            """,
        )


# Instância singleton
email_service = EmailService()
