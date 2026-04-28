"""Tasks Celery para geração assíncrona de PDF."""

import asyncio
from app.tasks.celery_app import celery_app
from app.core.logging import get_logger

logger = get_logger(__name__)


@celery_app.task(bind=True, max_retries=3)
def generate_monthly_report(self, user_id: str, mes: str):
    """
    Gera relatório mensal em PDF de forma assíncrona.
    Salva no storage e opcionalmente envia por email.
    """
    try:
        logger.info("Gerando relatório PDF", user_id=user_id, mes=mes)
        # Importações dentro da task para evitar problemas de contexto async
        from app.services.pdf.report import gerar_relatorio_mensal
        from app.services.storage.s3 import StorageService

        # Dados mockados - em produção viriam do DB
        pdf_bytes = gerar_relatorio_mensal(
            usuario={"nome": "Usuário", "objetivo": "bulking", "nivel": "intermediario", "peso": 80},
            workouts=[],
            nutrition_summary=[],
            prs=[],
            recomendacoes=["Continue com o plano atual!", "Aumente proteínas para 160g/dia."],
        )

        storage = StorageService()
        key = f"reports/{user_id}/relatorio_{mes}.pdf"
        url = storage.upload_file(pdf_bytes, key, "application/pdf")
        logger.info("Relatório salvo", url=url, user_id=user_id)
        return {"status": "success", "url": url}

    except Exception as exc:
        logger.error("Erro ao gerar PDF", error=str(exc), user_id=user_id)
        raise self.retry(exc=exc, countdown=60)
