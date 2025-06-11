"""
Репозиторий для работы с микротемами
"""
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models import Microtopic, Subject
from ..database import get_db_session


class MicrotopicRepository:
    """Репозиторий для работы с микротемами"""
    
    @staticmethod
    async def get_all() -> List[Microtopic]:
        """Получить все микротемы"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Microtopic)
                .options(selectinload(Microtopic.subject))
                .order_by(Microtopic.subject_id, Microtopic.name)
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_by_id(microtopic_id: int) -> Optional[Microtopic]:
        """Получить микротему по ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Microtopic)
                .options(selectinload(Microtopic.subject))
                .where(Microtopic.id == microtopic_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_subject(subject_id: int) -> List[Microtopic]:
        """Получить микротемы по предмету"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Microtopic)
                .options(selectinload(Microtopic.subject))
                .where(Microtopic.subject_id == subject_id)
                .order_by(Microtopic.name)
            )
            return list(result.scalars().all())

    @staticmethod
    async def create(name: str, subject_id: int) -> Microtopic:
        """Создать новую микротему"""
        async with get_db_session() as session:
            # Проверяем, существует ли уже такая микротема для данного предмета
            existing = await session.execute(
                select(Microtopic).where(
                    Microtopic.name == name,
                    Microtopic.subject_id == subject_id
                )
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"Микротема '{name}' уже существует для данного предмета")

            # Проверяем, существует ли предмет
            subject_exists = await session.execute(
                select(Subject).where(Subject.id == subject_id)
            )
            if not subject_exists.scalar_one_or_none():
                raise ValueError(f"Предмет с ID {subject_id} не найден")

            microtopic = Microtopic(name=name, subject_id=subject_id)
            session.add(microtopic)
            await session.commit()
            await session.refresh(microtopic)
            return microtopic

    @staticmethod
    async def update(microtopic_id: int, name: str = None) -> bool:
        """Обновить микротему"""
        async with get_db_session() as session:
            microtopic = await session.get(Microtopic, microtopic_id)
            if not microtopic:
                return False
            
            if name is not None:
                # Проверяем уникальность нового названия для данного предмета
                existing = await session.execute(
                    select(Microtopic).where(
                        Microtopic.name == name,
                        Microtopic.subject_id == microtopic.subject_id,
                        Microtopic.id != microtopic_id
                    )
                )
                if existing.scalar_one_or_none():
                    raise ValueError(f"Микротема '{name}' уже существует для данного предмета")
                
                microtopic.name = name
                
            await session.commit()
            return True

    @staticmethod
    async def delete(microtopic_id: int) -> bool:
        """Удалить микротему"""
        async with get_db_session() as session:
            result = await session.execute(delete(Microtopic).where(Microtopic.id == microtopic_id))
            await session.commit()
            return result.rowcount > 0

    @staticmethod
    async def delete_by_subject(subject_id: int) -> int:
        """Удалить все микротемы предмета (используется при удалении предмета)"""
        async with get_db_session() as session:
            result = await session.execute(delete(Microtopic).where(Microtopic.subject_id == subject_id))
            await session.commit()
            return result.rowcount

    @staticmethod
    async def exists(name: str, subject_id: int) -> bool:
        """Проверить, существует ли микротема с таким именем для данного предмета"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Microtopic).where(
                    Microtopic.name == name,
                    Microtopic.subject_id == subject_id
                )
            )
            return result.scalar_one_or_none() is not None

    @staticmethod
    async def get_count_by_subject(subject_id: int) -> int:
        """Получить количество микротем для предмета"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Microtopic).where(Microtopic.subject_id == subject_id)
            )
            return len(list(result.scalars().all()))
