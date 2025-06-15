"""
Репозиторий для работы с микротемами
"""
from typing import List, Optional
from sqlalchemy import select, delete, func
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
                .order_by(Microtopic.subject_id, Microtopic.number)
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
                .order_by(Microtopic.number)
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_next_number_for_subject(subject_id: int) -> int:
        """Получить следующий свободный номер для микротемы в рамках предмета"""
        async with get_db_session() as session:
            # Получаем все существующие номера для данного предмета
            result = await session.execute(
                select(Microtopic.number)
                .where(Microtopic.subject_id == subject_id)
                .order_by(Microtopic.number)
            )
            existing_numbers = [row[0] for row in result.fetchall()]

            # Если нет микротем, возвращаем 1
            if not existing_numbers:
                return 1

            # Ищем первый пропущенный номер
            for i in range(1, max(existing_numbers) + 2):
                if i not in existing_numbers:
                    return i

            # Если пропусков нет, возвращаем следующий после максимального
            return max(existing_numbers) + 1

    @staticmethod
    async def get_by_number(subject_id: int, number: int) -> Optional[Microtopic]:
        """Получить микротему по номеру в рамках предмета"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Microtopic)
                .options(selectinload(Microtopic.subject))
                .where(Microtopic.subject_id == subject_id, Microtopic.number == number)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def create(name: str, subject_id: int) -> Microtopic:
        """Создать новую микротему с автоматическим присвоением номера"""
        async with get_db_session() as session:
            # Проверяем, существует ли предмет
            subject_exists = await session.execute(
                select(Subject).where(Subject.id == subject_id)
            )
            if not subject_exists.scalar_one_or_none():
                raise ValueError(f"Предмет с ID {subject_id} не найден")

            # Проверяем уникальность названия в рамках предмета
            existing_name = await session.execute(
                select(Microtopic).where(
                    Microtopic.name == name,
                    Microtopic.subject_id == subject_id
                )
            )
            if existing_name.scalar_one_or_none():
                raise ValueError(f"Микротема с названием '{name}' уже существует для данного предмета")

            # Получаем следующий свободный номер для данного предмета в той же сессии
            existing_numbers_result = await session.execute(
                select(Microtopic.number)
                .where(Microtopic.subject_id == subject_id)
                .order_by(Microtopic.number)
            )
            existing_numbers = [row[0] for row in existing_numbers_result.fetchall()]

            # Находим первый свободный номер
            if not existing_numbers:
                next_number = 1
            else:
                next_number = None
                for i in range(1, max(existing_numbers) + 2):
                    if i not in existing_numbers:
                        next_number = i
                        break
                if next_number is None:
                    next_number = max(existing_numbers) + 1

            microtopic = Microtopic(name=name, subject_id=subject_id, number=next_number)
            session.add(microtopic)
            await session.commit()
            await session.refresh(microtopic)
            return microtopic

    @staticmethod
    async def create_multiple(names: List[str], subject_id: int) -> List[Microtopic]:
        """Создать несколько микротем одновременно с автоматическим присвоением номеров"""
        async with get_db_session() as session:
            # Проверяем, существует ли предмет
            subject_exists = await session.execute(
                select(Subject).where(Subject.id == subject_id)
            )
            if not subject_exists.scalar_one_or_none():
                raise ValueError(f"Предмет с ID {subject_id} не найден")

            # Очищаем и проверяем уникальность названий
            clean_names = []
            for name in names:
                if name.strip():
                    clean_name = name.strip()

                    # Проверяем уникальность названия в рамках предмета
                    existing_name = await session.execute(
                        select(Microtopic).where(
                            Microtopic.name == clean_name,
                            Microtopic.subject_id == subject_id
                        )
                    )
                    if existing_name.scalar_one_or_none():
                        raise ValueError(f"Микротема с названием '{clean_name}' уже существует для данного предмета")

                    # Проверяем дубликаты в текущем списке
                    if clean_name in clean_names:
                        raise ValueError(f"Дублирующееся название в списке: '{clean_name}'")

                    clean_names.append(clean_name)

            if not clean_names:
                raise ValueError("Не найдено ни одного валидного названия микротемы")

            # Получаем все существующие номера для данного предмета в той же сессии
            existing_numbers_result = await session.execute(
                select(Microtopic.number)
                .where(Microtopic.subject_id == subject_id)
                .order_by(Microtopic.number)
            )
            existing_numbers = set(row[0] for row in existing_numbers_result.fetchall())

            # Создаем микротемы, находя свободные номера
            microtopics = []
            current_number = 1
            for name in clean_names:
                # Находим следующий свободный номер
                while current_number in existing_numbers:
                    current_number += 1

                microtopic = Microtopic(
                    name=name,
                    subject_id=subject_id,
                    number=current_number
                )
                session.add(microtopic)
                microtopics.append(microtopic)
                existing_numbers.add(current_number)  # Добавляем в множество занятых номеров
                current_number += 1

            await session.commit()

            # Обновляем объекты для получения ID
            for microtopic in microtopics:
                await session.refresh(microtopic)

            return microtopics

    @staticmethod
    async def update(microtopic_id: int, name: str = None) -> bool:
        """Обновить микротему"""
        async with get_db_session() as session:
            microtopic = await session.get(Microtopic, microtopic_id)
            if not microtopic:
                return False

            if name is not None:
                microtopic.name = name

            await session.commit()
            return True

    @staticmethod
    async def renumber_subject_microtopics(subject_id: int) -> int:
        """Перенумеровать микротемы предмета по порядку (1, 2, 3...)"""
        async with get_db_session() as session:
            # Получаем все микротемы предмета, отсортированные по текущему номеру
            microtopics_result = await session.execute(
                select(Microtopic)
                .where(Microtopic.subject_id == subject_id)
                .order_by(Microtopic.number)
            )
            microtopics = microtopics_result.scalars().all()

            # Перенумеровываем
            updated_count = 0
            for i, microtopic in enumerate(microtopics, 1):
                if microtopic.number != i:
                    microtopic.number = i
                    updated_count += 1

            await session.commit()
            return updated_count

    @staticmethod
    async def delete(microtopic_id: int, renumber: bool = False) -> bool:
        """Удалить микротему без автоматической перенумерации"""
        async with get_db_session() as session:
            # Сначала получаем subject_id для возможной перенумерации
            microtopic_result = await session.execute(
                select(Microtopic.subject_id).where(Microtopic.id == microtopic_id)
            )
            subject_id = microtopic_result.scalar_one_or_none()

            # Удаляем микротему
            result = await session.execute(delete(Microtopic).where(Microtopic.id == microtopic_id))
            await session.commit()

            # Перенумеровываем только если явно запрошено (для обратной совместимости)
            if renumber and result.rowcount > 0 and subject_id:
                await MicrotopicRepository.renumber_subject_microtopics(subject_id)

            return result.rowcount > 0

    @staticmethod
    async def delete_by_number(subject_id: int, number: int) -> tuple[bool, str]:
        """Удалить микротему по номеру в рамках предмета

        Returns:
            tuple[bool, str]: (успех, название_удаленной_микротемы)
        """
        async with get_db_session() as session:
            # Находим микротему по номеру и предмету
            microtopic_result = await session.execute(
                select(Microtopic).where(
                    Microtopic.subject_id == subject_id,
                    Microtopic.number == number
                )
            )
            microtopic = microtopic_result.scalar_one_or_none()

            if not microtopic:
                return False, ""

            microtopic_name = microtopic.name

            # Удаляем микротему (без перенумерации согласно требованиям)
            result = await session.execute(
                delete(Microtopic).where(
                    Microtopic.subject_id == subject_id,
                    Microtopic.number == number
                )
            )
            await session.commit()

            return result.rowcount > 0, microtopic_name

    @staticmethod
    async def delete_by_subject(subject_id: int) -> int:
        """Удалить все микротемы предмета (используется при удалении предмета)"""
        async with get_db_session() as session:
            result = await session.execute(delete(Microtopic).where(Microtopic.subject_id == subject_id))
            await session.commit()
            return result.rowcount

    @staticmethod
    async def exists_by_number(subject_id: int, number: int) -> bool:
        """Проверить, существует ли микротема с таким номером для данного предмета"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Microtopic).where(
                    Microtopic.number == number,
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

    @staticmethod
    async def get_available_numbers(subject_id: int, limit: int = 10) -> List[int]:
        """Получить список доступных номеров для микротем в предмете"""
        async with get_db_session() as session:
            # Получаем все существующие номера для данного предмета
            result = await session.execute(
                select(Microtopic.number)
                .where(Microtopic.subject_id == subject_id)
                .order_by(Microtopic.number)
            )
            existing_numbers = set(row[0] for row in result.fetchall())

            # Находим свободные номера
            available_numbers = []
            current_number = 1

            while len(available_numbers) < limit:
                if current_number not in existing_numbers:
                    available_numbers.append(current_number)
                current_number += 1

                # Защита от бесконечного цикла
                if current_number > 1000:
                    break

            return available_numbers
