"""
Serviço de Storage S3-compatible (MinIO em dev, R2/S3 em prod).
"""

import io
import uuid
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from PIL import Image

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class StorageService:
    """Gerencia upload, download e delete de arquivos no storage S3-compatible."""

    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client(
                "s3",
                endpoint_url=settings.S3_ENDPOINT if not settings.S3_USE_SSL else None,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name=settings.S3_REGION,
            )
        return self._client

    def upload_image(
        self,
        file_data: bytes,
        prefix: str = "photos",
        max_width: int = 1920,
        quality: int = 85,
    ) -> str:
        """
        Comprime e faz upload de imagem. Retorna a chave no storage.
        """
        # Compressão com Pillow
        compressed = self._compress_image(file_data, max_width, quality)

        # Gerar chave única
        key = f"{prefix}/{uuid.uuid4()}.jpg"

        try:
            self.client.put_object(
                Bucket=settings.S3_BUCKET,
                Key=key,
                Body=compressed,
                ContentType="image/jpeg",
            )
            logger.info("upload_image_success", key=key)
            return key
        except ClientError as e:
            logger.error("upload_image_error", error=str(e))
            raise

    def _compress_image(self, data: bytes, max_width: int, quality: int) -> bytes:
        """Comprime imagem mantendo proporção."""
        img = Image.open(io.BytesIO(data))

        # Converter para RGB (necessário para JPEG)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Redimensionar se necessário
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.LANCZOS)

        # Salvar comprimido
        output = io.BytesIO()
        img.save(output, format="JPEG", quality=quality, optimize=True)
        return output.getvalue()

    def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Gera URL pré-assinada para acesso temporário."""
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.S3_BUCKET, "Key": key},
                ExpiresIn=expires_in,
            )
            return url
        except ClientError as e:
            logger.error("presigned_url_error", error=str(e))
            raise

    def delete_object(self, key: str) -> None:
        """Remove objeto do storage."""
        try:
            self.client.delete_object(Bucket=settings.S3_BUCKET, Key=key)
            logger.info("delete_object_success", key=key)
        except ClientError as e:
            logger.error("delete_object_error", error=str(e))
            raise

    def get_public_url(self, key: str) -> str:
        """Retorna URL pública (para objetos com acesso público)."""
        return f"{settings.S3_ENDPOINT}/{settings.S3_BUCKET}/{key}"


# Instância singleton
storage_service = StorageService()
