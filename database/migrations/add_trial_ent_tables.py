"""
Миграция для добавления таблиц пробного ЕНТ
"""
import asyncio
import logging
from sqlalchemy import text
from database.database import get_db_session

logger = logging.getLogger(__name__)


async def create_trial_ent_tables():
    """Создать таблицы для пробного ЕНТ"""
    
    # SQL для создания таблицы результатов пробного ЕНТ
    create_trial_ent_results_sql = """
    CREATE TABLE IF NOT EXISTS trial_ent_results (
        id SERIAL PRIMARY KEY,
        student_id INTEGER NOT NULL,
        required_subjects TEXT NOT NULL,
        profile_subjects TEXT NOT NULL,
        total_questions INTEGER NOT NULL,
        correct_answers INTEGER NOT NULL DEFAULT 0,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
    );
    """

    # SQL для создания таблицы результатов вопросов пробного ЕНТ
    create_trial_ent_question_results_sql = """
    CREATE TABLE IF NOT EXISTS trial_ent_question_results (
        id SERIAL PRIMARY KEY,
        test_result_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        selected_answer_id INTEGER,
        is_correct BOOLEAN NOT NULL,
        subject_code VARCHAR(20) NOT NULL,
        time_spent INTEGER,
        microtopic_number INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (test_result_id) REFERENCES trial_ent_results (id) ON DELETE CASCADE,
        FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE,
        FOREIGN KEY (selected_answer_id) REFERENCES answer_options (id) ON DELETE SET NULL
    );
    """
    
    # SQL для создания индексов
    create_indexes_sql = [
        "CREATE INDEX IF NOT EXISTS idx_trial_ent_results_student_id ON trial_ent_results (student_id);",
        "CREATE INDEX IF NOT EXISTS idx_trial_ent_results_completed_at ON trial_ent_results (completed_at);",
        "CREATE INDEX IF NOT EXISTS idx_trial_ent_question_results_test_result_id ON trial_ent_question_results (test_result_id);",
        "CREATE INDEX IF NOT EXISTS idx_trial_ent_question_results_subject_code ON trial_ent_question_results (subject_code);",
        "CREATE INDEX IF NOT EXISTS idx_trial_ent_question_results_microtopic_number ON trial_ent_question_results (microtopic_number);"
    ]
    
    try:
        async with get_db_session() as session:
            # Создаем таблицы
            await session.execute(text(create_trial_ent_results_sql))
            logger.info("Таблица trial_ent_results создана")
            
            await session.execute(text(create_trial_ent_question_results_sql))
            logger.info("Таблица trial_ent_question_results создана")
            
            # Создаем индексы
            for index_sql in create_indexes_sql:
                await session.execute(text(index_sql))
            logger.info("Индексы для таблиц пробного ЕНТ созданы")
            
            await session.commit()
            logger.info("Миграция таблиц пробного ЕНТ выполнена успешно")
            
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц пробного ЕНТ: {e}")
        raise


async def drop_trial_ent_tables():
    """Удалить таблицы пробного ЕНТ (для отката миграции)"""
    
    drop_tables_sql = [
        "DROP TABLE IF EXISTS trial_ent_question_results;",
        "DROP TABLE IF EXISTS trial_ent_results;"
    ]
    
    try:
        async with get_db_session() as session:
            for drop_sql in drop_tables_sql:
                await session.execute(text(drop_sql))
            
            await session.commit()
            logger.info("Таблицы пробного ЕНТ удалены")
            
    except Exception as e:
        logger.error(f"Ошибка при удалении таблиц пробного ЕНТ: {e}")
        raise


async def main():
    """Запуск миграции"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        await drop_trial_ent_tables()
    else:
        await create_trial_ent_tables()


if __name__ == "__main__":
    asyncio.run(main())
