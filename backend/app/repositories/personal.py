"""
Repositório para operações de banco - Personal Trainer e Clientes.

Repositório = camada que fala com o banco de dados.
Nenhuma regra de negócio aqui, só queries.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import PersonalClient, ClientStatus, User


class PersonalClientRepository:
    """
    Todas as queries relacionadas ao vínculo personal ↔ aluno.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_clients_of_personal(
        self, personal_id: UUID
    ) -> list[PersonalClient]:
        """
        Retorna todos os alunos de um personal.
        Carrega os dados do aluno junto (selectinload evita N+1 queries).
        """
        result = await self.db.execute(
            select(PersonalClient)
            .where(PersonalClient.personal_id == personal_id)
            .options(selectinload(PersonalClient.client))  # carrega dados do aluno
            .order_by(PersonalClient.invited_at.desc())
        )
        return list(result.scalars().all())

    async def get_active_clients(self, personal_id: UUID) -> list[PersonalClient]:
        """Apenas alunos ativos do personal."""
        result = await self.db.execute(
            select(PersonalClient)
            .where(
                and_(
                    PersonalClient.personal_id == personal_id,
                    PersonalClient.status == ClientStatus.ativo,
                )
            )
            .options(selectinload(PersonalClient.client))
        )
        return list(result.scalars().all())

    async def get_link(
        self, personal_id: UUID, client_id: UUID
    ) -> Optional[PersonalClient]:
        """
        Busca o vínculo específico entre um personal e um aluno.
        Retorna None se não existir.
        """
        result = await self.db.execute(
            select(PersonalClient).where(
                and_(
                    PersonalClient.personal_id == personal_id,
                    PersonalClient.client_id == client_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_link_by_id(self, link_id: UUID) -> Optional[PersonalClient]:
        """Busca vínculo pelo ID do vínculo."""
        result = await self.db.execute(
            select(PersonalClient)
            .where(PersonalClient.id == link_id)
            .options(
                selectinload(PersonalClient.client),
                selectinload(PersonalClient.personal),
            )
        )
        return result.scalar_one_or_none()

    async def get_personals_of_client(self, client_id: UUID) -> list[PersonalClient]:
        """
        Retorna todos os personais de um aluno.
        Um aluno pode ter mais de um personal.
        """
        result = await self.db.execute(
            select(PersonalClient)
            .where(PersonalClient.client_id == client_id)
            .options(selectinload(PersonalClient.personal))
        )
        return list(result.scalars().all())

    async def create_invite(
        self,
        personal_id: UUID,
        client_id: UUID,
        notes: Optional[str] = None,
    ) -> PersonalClient:
        """
        Cria o convite (vínculo com status 'pendente').
        """
        link = PersonalClient(
            personal_id=personal_id,
            client_id=client_id,
            status=ClientStatus.pendente,
            notes=notes,
        )
        self.db.add(link)
        await self.db.flush()
        await self.db.refresh(link)
        return link

    async def accept_invite(self, link: PersonalClient) -> PersonalClient:
        """
        Aluno aceita o convite → status vira 'ativo'.
        """
        from datetime import datetime, timezone
        link.status = ClientStatus.ativo
        link.accepted_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(link)
        return link

    async def deactivate(self, link: PersonalClient) -> PersonalClient:
        """
        Encerra o vínculo → status vira 'inativo'.
        Pode ser feito pelo personal ou pelo aluno.
        """
        link.status = ClientStatus.inativo
        await self.db.flush()
        await self.db.refresh(link)
        return link

    async def update_notes(
        self, link: PersonalClient, notes: str
    ) -> PersonalClient:
        """Personal atualiza suas notas sobre o aluno."""
        link.notes = notes
        await self.db.flush()
        await self.db.refresh(link)
        return link

    async def count_clients(self, personal_id: UUID) -> dict:
        """
        Conta alunos por status para o dashboard do personal.
        Retorna: { total, ativo, pendente, inativo }
        """
        from sqlalchemy import func
        result = await self.db.execute(
            select(PersonalClient.status, func.count(PersonalClient.id))
            .where(PersonalClient.personal_id == personal_id)
            .group_by(PersonalClient.status)
        )
        rows = result.all()
        counts = {"total": 0, "ativo": 0, "pendente": 0, "inativo": 0}
        for status, count in rows:
            counts[status] = count
            counts["total"] += count
        return counts
