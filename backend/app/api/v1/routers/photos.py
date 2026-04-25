"""Router de Fotos: upload, galeria e remoção."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models.photo import Photo
from app.models.user import User
from app.schemas.photo import PhotoResponse
from app.services.storage.s3 import storage_service

router = APIRouter(prefix="/photos", tags=["photos"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE_MB = 10


@router.post("", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    file: UploadFile = File(...),
    weight_kg: float = Form(default=None),
    notes: str = Form(default=None),
    taken_at: datetime = Form(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload de foto corporal com compressão automática."""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de arquivo não permitido. Use: {', '.join(ALLOWED_TYPES)}",
        )

    data = await file.read()
    if len(data) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Arquivo muito grande. Máximo: {MAX_SIZE_MB}MB",
        )

    # Upload com compressão
    key = storage_service.upload_image(data, prefix=f"photos/{current_user.id}")

    # Salvar metadados
    photo = Photo(
        user_id=current_user.id,
        storage_key=key,
        weight_kg=weight_kg,
        notes=notes,
        taken_at=taken_at or datetime.now(timezone.utc),
    )
    db.add(photo)
    await db.flush()
    await db.refresh(photo)

    # Gerar URL
    response = PhotoResponse.model_validate(photo)
    response.url = storage_service.get_public_url(key)
    return response


@router.get("", response_model=list[PhotoResponse])
async def list_photos(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista todas as fotos do usuário em ordem cronológica."""
    result = await db.execute(
        select(Photo)
        .where(Photo.user_id == current_user.id)
        .order_by(Photo.taken_at.desc())
    )
    photos = list(result.scalars().all())

    response_list = []
    for p in photos:
        r = PhotoResponse.model_validate(p)
        r.url = storage_service.get_public_url(p.storage_key)
        response_list.append(r)
    return response_list


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(
    photo_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove foto e arquivo do storage."""
    result = await db.execute(
        select(Photo).where(Photo.id == photo_id, Photo.user_id == current_user.id)
    )
    photo = result.scalar_one_or_none()

    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foto não encontrada")

    # Remove do storage
    try:
        storage_service.delete_object(photo.storage_key)
    except Exception:
        pass  # Continua mesmo se falhar no storage

    await db.delete(photo)
