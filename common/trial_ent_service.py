"""
Сервис для работы с пробным ЕНТ
"""
import random
import json
from typing import List, Dict, Any, Optional, Tuple
import logging
from database import (
    QuestionRepository, SubjectRepository, TrialEntResultRepository, 
    TrialEntQuestionResultRepository, StudentRepository
)

logger = logging.getLogger(__name__)


class TrialEntService:
    """Сервис для работы с пробным ЕНТ"""
    
    # Маппинг кодов предметов на их названия
    SUBJECT_NAMES = {
        "kz": "История Казахстана",
        "mathlit": "Математическая грамотность", 
        "math": "Математика",
        "geo": "География",
        "bio": "Биология",
        "chem": "Химия",
        "inf": "Информатика",
        "world": "Всемирная история"
    }
    
    # Маппинг кодов предметов на их ID в базе данных
    SUBJECT_CODE_TO_NAME_MAP = {
        "kz": "История Казахстана",
        "mathlit": "Математическая грамотность",
        "math": "Математика", 
        "geo": "География",
        "bio": "Биология",
        "chem": "Химия",
        "inf": "Информатика",
        "world": "Всемирная история"
    }
    
    # Количество вопросов для каждого типа предмета
    QUESTION_COUNTS = {
        "kz": 20,
        "mathlit": 10,
        "math": 50,
        "geo": 50,
        "bio": 50,
        "chem": 50,
        "inf": 50,
        "world": 50
    }

    @staticmethod
    async def get_subject_id_by_code(subject_code: str) -> Optional[int]:
        """Получить ID предмета по коду"""
        subject_name = TrialEntService.SUBJECT_CODE_TO_NAME_MAP.get(subject_code)
        if not subject_name:
            return None
            
        subject = await SubjectRepository.get_by_name(subject_name)
        return subject.id if subject else None

    @staticmethod
    async def get_random_questions_for_subject(subject_code: str, count: int) -> List[Dict[str, Any]]:
        """Получить случайные вопросы для предмета"""
        subject_id = await TrialEntService.get_subject_id_by_code(subject_code)
        if not subject_id:
            logger.warning(f"Предмет с кодом {subject_code} не найден")
            return []
        
        # Получаем все вопросы по предмету
        all_questions = await QuestionRepository.get_by_subject(subject_id)
        
        if len(all_questions) < count:
            logger.warning(f"Недостаточно вопросов для предмета {subject_code}. Требуется: {count}, доступно: {len(all_questions)}")
            # Используем все доступные вопросы
            selected_questions = all_questions
        else:
            # Выбираем случайные вопросы
            selected_questions = random.sample(all_questions, count)
            logger.info(f"Выбрано {len(selected_questions)} вопросов для предмета {subject_code}")
        
        # Преобразуем в формат для quiz_registrator
        questions_data = []
        for question in selected_questions:
            question_data = {
                "id": question.id,
                "text": question.text,
                "photo_path": question.photo_path,
                "subject_code": subject_code,
                "subject_name": TrialEntService.SUBJECT_NAMES.get(subject_code, ""),
                "microtopic_number": question.microtopic_number,
                "time_limit": question.time_limit or 60,  # По умолчанию 60 секунд
                "options": {},
                "correct_answer_id": None
            }

            # Добавляем варианты ответов
            for option in question.answer_options:
                option_letter = chr(65 + option.order_number - 1)  # A, B, C, D...
                question_data["options"][option_letter] = {
                    "id": option.id,
                    "text": option.text
                }
                if option.is_correct:
                    question_data["correct_answer_id"] = option.id

            questions_data.append(question_data)
        
        return questions_data

    @staticmethod
    async def generate_trial_ent_questions(
        required_subjects: List[str], 
        profile_subjects: List[str]
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Сгенерировать вопросы для пробного ЕНТ"""
        all_questions = []
        total_questions = 0
        
        # Добавляем обязательные предметы
        for subject_code in required_subjects:
            count = TrialEntService.QUESTION_COUNTS.get(subject_code, 0)
            if count > 0:
                questions = await TrialEntService.get_random_questions_for_subject(subject_code, count)
                all_questions.extend(questions)
                total_questions += len(questions)
        
        # Добавляем профильные предметы
        for subject_code in profile_subjects:
            count = TrialEntService.QUESTION_COUNTS.get(subject_code, 0)
            if count > 0:
                questions = await TrialEntService.get_random_questions_for_subject(subject_code, count)
                all_questions.extend(questions)
                total_questions += len(questions)
        
        # Перемешиваем вопросы и добавляем номера
        random.shuffle(all_questions)
        for i, question in enumerate(all_questions, 1):
            question["number"] = i
        
        return all_questions, total_questions

    @staticmethod
    async def save_trial_ent_result(
        student_id: int,
        required_subjects: List[str],
        profile_subjects: List[str],
        questions_data: List[Dict[str, Any]],
        answers: Dict[int, int]  # question_number -> selected_answer_id
    ) -> int:
        """Сохранить результат пробного ЕНТ"""
        import time
        start_time = time.time()
        logger.info(f"💾 TRIAL_ENT_SERVICE: Начинаем сохранение результата для студента {student_id}")

        # Подсчитываем правильные ответы
        correct_answers = 0
        question_results_data = []
        
        for question in questions_data:
            question_number = question["number"]
            selected_answer_id = answers.get(question_number)
            is_correct = selected_answer_id == question["correct_answer_id"]
            
            if is_correct:
                correct_answers += 1
            
            question_results_data.append({
                "question_id": question["id"],
                "selected_answer_id": selected_answer_id,
                "is_correct": is_correct,
                "subject_code": question["subject_code"],
                "microtopic_number": question["microtopic_number"]
            })
        
        # Создаем результат теста
        logger.info(f"📝 TRIAL_ENT_SERVICE: Создаем основной результат теста...")
        trial_ent_result = await TrialEntResultRepository.create(
            student_id=student_id,
            required_subjects=required_subjects,
            profile_subjects=profile_subjects,
            total_questions=len(questions_data),
            correct_answers=correct_answers
        )
        logger.info(f"✅ TRIAL_ENT_SERVICE: Основной результат создан с ID {trial_ent_result.id}")
        
        # Добавляем test_result_id к данным результатов вопросов
        for qr_data in question_results_data:
            qr_data["test_result_id"] = trial_ent_result.id
        
        # Сохраняем результаты вопросов
        logger.info(f"📊 TRIAL_ENT_SERVICE: Сохраняем {len(question_results_data)} результатов вопросов...")
        await TrialEntQuestionResultRepository.create_batch(question_results_data)

        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"🎉 TRIAL_ENT_SERVICE: Сохранение завершено за {duration:.2f} секунд")

        return trial_ent_result.id

    @staticmethod
    async def get_trial_ent_statistics(trial_ent_result_id: int) -> Dict[str, Any]:
        """Получить статистику пробного ЕНТ"""
        import time
        start_time = time.time()
        logger.info(f"📈 TRIAL_ENT_SERVICE: Получаем статистику для результата {trial_ent_result_id}")

        # Получаем результат теста
        trial_ent_result = await TrialEntResultRepository.get_by_id(trial_ent_result_id)
        if not trial_ent_result:
            return {}
        
        # Получаем статистику по предметам
        subject_stats = await TrialEntQuestionResultRepository.get_statistics_by_subject(trial_ent_result_id)
        
        # Получаем статистику по микротемам
        microtopic_stats = await TrialEntQuestionResultRepository.get_statistics_by_microtopic(trial_ent_result_id)
        
        # Парсим выбранные предметы
        required_subjects = json.loads(trial_ent_result.required_subjects)
        profile_subjects = json.loads(trial_ent_result.profile_subjects)

        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"📊 TRIAL_ENT_SERVICE: Статистика получена за {duration:.2f} секунд")

        return {
            "trial_ent_result": trial_ent_result,
            "required_subjects": required_subjects,
            "profile_subjects": profile_subjects,
            "subject_statistics": subject_stats,
            "microtopic_statistics": microtopic_stats,
            "total_correct": trial_ent_result.correct_answers,
            "total_questions": trial_ent_result.total_questions
        }

    @staticmethod
    async def get_student_trial_ent_history(student_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Получить историю пробных ЕНТ студента"""
        results = await TrialEntResultRepository.get_by_student(student_id, limit)
        
        history = []
        for result in results:
            required_subjects = json.loads(result.required_subjects)
            profile_subjects = json.loads(result.profile_subjects)
            
            history.append({
                "id": result.id,
                "required_subjects": required_subjects,
                "profile_subjects": profile_subjects,
                "total_questions": result.total_questions,
                "correct_answers": result.correct_answers,
                "percentage": round((result.correct_answers / result.total_questions) * 100) if result.total_questions > 0 else 0,
                "completed_at": result.completed_at
            })
        
        return history

    @staticmethod
    def get_subject_name(subject_code: str) -> str:
        """Получить название предмета по коду"""
        return TrialEntService.SUBJECT_NAMES.get(subject_code, subject_code)
