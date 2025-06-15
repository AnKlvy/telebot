"""
Скрипт для нагрузочного тестирования домашних заданий
Симулирует одновременную работу 50 учеников
"""
import asyncio
import aiohttp
import json
import time
import random
from typing import List, Dict, Any
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(f'logs/load_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HomeworkLoadTester:
    """Класс для нагрузочного тестирования домашних заданий"""
    
    def __init__(self, webhook_url: str, bot_token: str):
        self.webhook_url = webhook_url
        self.bot_token = bot_token
        self.students = []
        self.results = []
        
    def generate_students(self, count: int = 50) -> List[Dict[str, Any]]:
        """Генерация тестовых студентов"""
        students = []
        for i in range(count):
            student = {
                'user_id': 1000000 + i,
                'first_name': f'Student{i+1}',
                'username': f'student{i+1}',
                'chat_id': 1000000 + i
            }
            students.append(student)
        return students
    
    def create_telegram_update(self, student: Dict, message_text: str = None, callback_data: str = None) -> Dict:
        """Создание Telegram Update объекта"""
        update_id = random.randint(100000, 999999)
        
        if callback_data:
            # Callback query
            update = {
                "update_id": update_id,
                "callback_query": {
                    "id": str(random.randint(1000000000, 9999999999)),
                    "from": {
                        "id": student['user_id'],
                        "is_bot": False,
                        "first_name": student['first_name'],
                        "username": student['username']
                    },
                    "message": {
                        "message_id": random.randint(1000, 9999),
                        "from": {
                            "id": 123456789,  # Bot ID
                            "is_bot": True,
                            "first_name": "EduBot"
                        },
                        "chat": {
                            "id": student['chat_id'],
                            "first_name": student['first_name'],
                            "username": student['username'],
                            "type": "private"
                        },
                        "date": int(time.time()),
                        "text": "Выбери курс..."
                    },
                    "data": callback_data
                }
            }
        else:
            # Text message
            update = {
                "update_id": update_id,
                "message": {
                    "message_id": random.randint(1000, 9999),
                    "from": {
                        "id": student['user_id'],
                        "is_bot": False,
                        "first_name": student['first_name'],
                        "username": student['username']
                    },
                    "chat": {
                        "id": student['chat_id'],
                        "first_name": student['first_name'],
                        "username": student['username'],
                        "type": "private"
                    },
                    "date": int(time.time()),
                    "text": message_text or "/start"
                }
            }
        
        return update
    
    async def send_update(self, session: aiohttp.ClientSession, student: Dict, 
                         message_text: str = None, callback_data: str = None) -> Dict:
        """Отправка update на webhook"""
        update = self.create_telegram_update(student, message_text, callback_data)
        
        start_time = time.time()
        try:
            async with session.post(
                self.webhook_url,
                json=update,
                headers={'Content-Type': 'application/json'},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_time = time.time() - start_time
                status = response.status
                
                result = {
                    'student_id': student['user_id'],
                    'action': callback_data or message_text or '/start',
                    'response_time': response_time,
                    'status_code': status,
                    'success': status == 200,
                    'timestamp': datetime.now().isoformat()
                }
                
                if status != 200:
                    result['error'] = await response.text()
                
                return result
                
        except Exception as e:
            response_time = time.time() - start_time
            return {
                'student_id': student['user_id'],
                'action': callback_data or message_text or '/start',
                'response_time': response_time,
                'status_code': 0,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def simulate_homework_flow(self, session: aiohttp.ClientSession, student: Dict) -> List[Dict]:
        """Симуляция полного прохождения домашнего задания"""
        results = []
        
        # Последовательность действий студента
        actions = [
            ('/start', None),
            (None, 'homework'),  # Выбор домашних заданий
            (None, 'course_1'),  # Выбор курса
            (None, 'subject_1'), # Выбор предмета
            (None, 'lesson_1'),  # Выбор урока
            (None, 'homework_1'), # Выбор домашнего задания
            (None, 'start_test'), # Начало теста
        ]
        
        # Добавляем ответы на вопросы (15 вопросов)
        for i in range(15):
            answer = random.choice(['A', 'B', 'C', 'D'])
            actions.append((None, f'answer_{answer}'))
        
        # Выполняем действия с задержками
        for i, (message, callback) in enumerate(actions):
            # Случайная задержка между действиями (0.5-2 секунды)
            if i > 0:
                await asyncio.sleep(random.uniform(0.5, 2.0))
            
            result = await self.send_update(session, student, message, callback)
            results.append(result)
            
            # Логируем прогресс
            if not result['success']:
                logger.error(f"Ошибка для студента {student['user_id']}: {result.get('error', 'Unknown error')}")
        
        return results
    
    async def run_concurrent_test(self, student_count: int = 50) -> Dict[str, Any]:
        """Запуск нагрузочного теста с одновременными пользователями"""
        logger.info(f"🚀 Начинаем нагрузочный тест с {student_count} студентами")
        
        # Генерируем студентов
        self.students = self.generate_students(student_count)
        
        start_time = time.time()
        
        # Создаем сессию для HTTP запросов
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)
        async with aiohttp.ClientSession(connector=connector) as session:
            
            # Запускаем симуляцию для всех студентов одновременно
            tasks = []
            for student in self.students:
                task = asyncio.create_task(
                    self.simulate_homework_flow(session, student)
                )
                tasks.append(task)
            
            # Ждем завершения всех задач
            all_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        # Обрабатываем результаты
        successful_students = 0
        failed_students = 0
        all_response_times = []
        
        for student_results in all_results:
            if isinstance(student_results, Exception):
                failed_students += 1
                logger.error(f"Исключение для студента: {student_results}")
                continue
            
            student_successful = True
            for result in student_results:
                all_response_times.append(result['response_time'])
                if not result['success']:
                    student_successful = False
            
            if student_successful:
                successful_students += 1
            else:
                failed_students += 1
        
        # Статистика
        stats = {
            'total_students': student_count,
            'successful_students': successful_students,
            'failed_students': failed_students,
            'success_rate': (successful_students / student_count) * 100,
            'total_test_time': total_time,
            'total_requests': len(all_response_times),
            'avg_response_time': sum(all_response_times) / len(all_response_times) if all_response_times else 0,
            'min_response_time': min(all_response_times) if all_response_times else 0,
            'max_response_time': max(all_response_times) if all_response_times else 0,
            'requests_per_second': len(all_response_times) / total_time if total_time > 0 else 0
        }
        
        logger.info(f"✅ Тест завершен за {total_time:.2f} секунд")
        logger.info(f"📊 Успешных студентов: {successful_students}/{student_count} ({stats['success_rate']:.1f}%)")
        logger.info(f"⚡ Среднее время ответа: {stats['avg_response_time']:.3f}с")
        logger.info(f"🔥 Запросов в секунду: {stats['requests_per_second']:.1f}")
        
        return stats


async def main():
    """Главная функция для запуска тестов"""
    # Конфигурация
    WEBHOOK_URL = "https://edubot.schoolpro.kz/webhook"  # Ваш webhook URL
    BOT_TOKEN = "your_bot_token"  # Не используется для webhook тестов
    
    tester = HomeworkLoadTester(WEBHOOK_URL, BOT_TOKEN)
    
    # Запускаем тест с разным количеством студентов
    test_scenarios = [10, 25, 50]
    
    for student_count in test_scenarios:
        logger.info(f"\n{'='*50}")
        logger.info(f"ТЕСТ С {student_count} СТУДЕНТАМИ")
        logger.info(f"{'='*50}")
        
        stats = await tester.run_concurrent_test(student_count)
        
        # Сохраняем результаты в файл
        with open(f'logs/load_test_results_{student_count}students_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        # Пауза между тестами
        if student_count != test_scenarios[-1]:
            logger.info("⏳ Пауза 30 секунд перед следующим тестом...")
            await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(main())
