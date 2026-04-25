"""
Serviço de armazenamento de arquivos (S3-compatible: MinIO/R2).
Suporta upload, download URL pré-assinada e deleção.
"""
import io
import logging
import uuid
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from PIL import Image

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class StorageService:
    """Interface unificada para operações de storage S3-compatible."""

    def __init__(self) -> None:
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
            use_ssl=settings.s3_use_ssl,
        )
        self.bucket = settings.s3_bucket

    def _ensure_bucket(self) -> None:
        """Cria o bucket se não existir."""
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except ClientError:
            self.client.create_bucket(Bucket=self.bucket)
            logger.info("Bucket '%s' criado.", self.bucket)

    def upload_image(
        self,
        file_bytes: bytes,
        content_type: str,
        user_id: uuid.UUID,
        prefix: str = "photos",
    ) -> str:
        """
        Comprime e faz upload de imagem.
        Retorna a storage_key (caminho no bucket).
        """
        # Comprime a imagem com Pillow
        compressed = self._compress_image(file_bytes)

        # Gera key única
        file_id = str(uuid.uuid4())
        key = f"{prefix}/{user_id}/{file_id}.jpg"

        self._ensure_bucket()
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=compressed,
            ContentType="image/jpeg",
        )
        logger.info("Upload concluído: %s", key)
        return key

    def _compress_image(self, file_bytes: bytes) -> bytes:
        """Redimensiona e comprime imagem para JPEG."""
        try:
            img = Image.open(io.BytesIO(file_bytes))

            # Converte para RGB (remove canal alpha se houver)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Redimensiona mantendo proporção
            max_w, max_h = settings.image_max_width, settings.image_max_height
            img.thumbnail((max_w, max_h), Image.LANCZOS)

            # Salva como JPEG comprimido
            output = io.BytesIO()
            img.save(output, format="JPEG", quality=settings.image_quality, optimize=True)
            return output.getvalue()
        except Exception as e:
            logger.warning("Falha na compressão de imagem, usando original: %s", e)
            return file_bytes

    def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Gera URL pré-assinada para acesso temporário ao arquivo."""
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expires_in,
            )
            return url
        except ClientError as e:
            logger.error("Erro ao gerar URL pré-assinada para %s: %s", key, e)
            return ""

    def delete(self, key: str) -> None:
        """Remove arquivo do storage."""
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            logger.info("Arquivo removido: %s", key)
        except ClientError as e:
            logger.error("Erro ao remover arquivo %s: %s", key, e)

    def upload_pdf(self, pdf_bytes: bytes, user_id: uuid.UUID, filename: str) -> str:
        """Upload de arquivo PDF para storage."""
        key = f"reports/{user_id}/{filename}"
        self._ensure_bucket()
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=pdf_bytes,
            ContentType="application/pdf",
        )
        return key


# Instância singleton
storage_service = StorageService()
