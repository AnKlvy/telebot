#!/usr/bin/env python3
"""
Имитация реальных пользователей через Telegram Bot API
Создает тестовых пользователей и отправляет сообщения боту

ВНИМАНИЕ: Этот скрипт отправляет реальные сообщения через Telegram API!
Используйте только с тестовым ботом и в ограниченных количествах.
"""
import asyncio
import aiohttp
import time
import json
import argparse
import random
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass
import os

@dataclass
class UserAction:
    """Действие пользователя"""
    user_id: int
    action_type: str
    message: str
    response_time: float
    success: bool
    error: str = None

class TelegramUserSimulator:
    """Симулятор пользователей Telegram"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        self.actions: List[UserAction] = []
        
        # Сценарии поведения пользователей
        self.user_scenarios = {
            "student": [
                "/start",
                "📚 Мои курсы", 
                "📝 Домашние задания",
                "📊 Моя статистика",
                "🔍 Поиск материалов"
            ],
            "teacher": [
                "/start",
                "👥 Мои группы",
                "📝 Создать задание", 
                "📊 Статистика группы",
                "📋 Проверить работы"
            ],
            "admin": [
                "/start",
                "👥 Управление пользователями",
                "📚 Управление курсами",
                "📊 Общая статистика",
                "⚙️ Настройки системы"
            ]
        }
    
    async def send_message(self, session: aiohttp.ClientSession, chat_id: int, text: str) -> UserAction:
        """Отправка сообщения боту от имени пользователя"""
        start_time = time.time()
        
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": text
            }
            
            async with session.post(url, json=data) as response:
                response_time = time.time() - start_time
                result = await response.json()
                
                return UserAction(
                    user_id=chat_id,
                    action_type="send_message",
                    message=text,
                    response_time=response_time,
                    success=result.get("ok", False),
                    error=result.get("description") if not result.get("ok") else None
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            return UserAction(
                user_id=chat_id,
                action_type="send_message", 
                message=text,
                response_time=response_time,
                success=False,
                error=str(e)
            )
    
    async def get_updates(self, session: aiohttp.ClientSession, offset: int = 0) -> Dict:
        """Получение обновлений от бота"""
        try:
            url = f"{self.api_url}/getUpdates"
            params = {"offset": offset, "timeout": 1}
            
            async with session.get(url, params=params) as response:
                return await response.json()
                
        except Exception as e:
            return {"ok": False, "description": str(e)}
    
    async def simulate_user(self, session: aiohttp.ClientSession, user_id: int,
                          user_type: str, actions_count: int, test_mode: str = "realistic"):
        """Симуляция одного пользователя"""
        scenario = self.user_scenarios.get(user_type, self.user_scenarios["student"])

        print(f"👤 Пользователь {user_id} ({user_type}) начал симуляцию в режиме {test_mode}")

        if test_mode == "burst":
            # BURST MODE: Все запросы одновременно без пауз
            tasks = []
            for i in range(actions_count):
                message = random.choice(scenario)
                task = asyncio.create_task(self.send_message(session, user_id, message))
                tasks.append(task)

            # Выполняем ВСЕ запросы одновременно
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(results):
                if isinstance(result, UserAction):
                    self.actions.append(result)
                    if result.success:
                        print(f"⚡ User {user_id}: {result.message} ({result.response_time:.3f}s)")
                    else:
                        print(f"❌ User {user_id}: {result.message} - {result.error}")

        else:
            # SEQUENTIAL MODE: Последовательные запросы с паузами
            for i in range(actions_count):
                message = random.choice(scenario)
                action = await self.send_message(session, user_id, message)
                self.actions.append(action)

                if action.success:
                    print(f"✅ User {user_id}: {message} ({action.response_time:.3f}s)")
                else:
                    print(f"❌ User {user_id}: {message} - {action.error}")

                # Пауза зависит от режима
                if test_mode == "realistic" and i < actions_count - 1:
                    await asyncio.sleep(random.uniform(1, 5))
                elif test_mode == "sustained" and i < actions_count - 1:
                    await asyncio.sleep(0.5)  # Быстрее чем realistic
    
    async def run_simulation(self, users_count: int, actions_per_user: int,
                           user_distribution: Dict[str, float] = None, test_mode: str = "realistic"):
        """Запуск симуляции пользователей"""
        if user_distribution is None:
            user_distribution = {"student": 0.7, "teacher": 0.2, "admin": 0.1}

        print(f"🚀 Запуск симуляции пользователей")
        print(f"👥 Количество пользователей: {users_count}")
        print(f"🎯 Действий на пользователя: {actions_per_user}")
        print(f"🎯 Режим тестирования: {test_mode}")
        print(f"📊 Распределение ролей: {user_distribution}")

        if test_mode == "burst":
            print("⚡ BURST MODE: Максимальная нагрузка - все запросы одновременно!")
        elif test_mode == "sustained":
            print("🔄 SUSTAINED MODE: Постоянная нагрузка с короткими паузами")
        else:
            print("👤 REALISTIC MODE: Имитация реальных пользователей с паузами")
        
        # Создаем список пользователей с ролями
        users = []
        base_user_id = 2000000  # Начинаем с большого ID чтобы не пересекаться с реальными
        
        for i in range(users_count):
            # Определяем роль пользователя на основе распределения
            rand = random.random()
            cumulative = 0
            user_type = "student"
            
            for role, probability in user_distribution.items():
                cumulative += probability
                if rand <= cumulative:
                    user_type = role
                    break
            
            users.append((base_user_id + i, user_type))
        
        # Запускаем симуляцию
        connector = aiohttp.TCPConnector(limit=users_count * 2)
        timeout = aiohttp.ClientTimeout(total=60)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Проверяем доступность бота
            bot_info = await self.get_bot_info(session)
            if not bot_info.get("ok"):
                print(f"❌ Ошибка подключения к боту: {bot_info.get('description')}")
                return
            
            print(f"🤖 Подключен к боту: {bot_info['result']['first_name']}")
            
            # Создаем задачи для каждого пользователя
            tasks = []
            for user_id, user_type in users:
                task = asyncio.create_task(
                    self.simulate_user(session, user_id, user_type, actions_per_user, test_mode)
                )
                tasks.append(task)
            
            # Запускаем все задачи
            start_time = time.time()
            await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time
            
        self.generate_report(total_time)
    
    async def get_bot_info(self, session: aiohttp.ClientSession) -> Dict:
        """Получение информации о боте"""
        try:
            url = f"{self.api_url}/getMe"
            async with session.get(url) as response:
                return await response.json()
        except Exception as e:
            return {"ok": False, "description": str(e)}
    
    def generate_report(self, total_time: float):
        """Генерация отчета о симуляции"""
        if not self.actions:
            print("❌ Нет действий для анализа")
            return
        
        successful_actions = [a for a in self.actions if a.success]
        failed_actions = [a for a in self.actions if not a.success]
        
        print("\n" + "="*60)
        print("📊 ОТЧЕТ О СИМУЛЯЦИИ ПОЛЬЗОВАТЕЛЕЙ")
        print("="*60)
        
        print(f"📈 Общая статистика:")
        print(f"   Всего действий: {len(self.actions)}")
        print(f"   Успешных: {len(successful_actions)} ({len(successful_actions)/len(self.actions)*100:.1f}%)")
        print(f"   Неудачных: {len(failed_actions)} ({len(failed_actions)/len(self.actions)*100:.1f}%)")
        print(f"   Общее время: {total_time:.2f} сек")
        print(f"   Действий в секунду: {len(self.actions)/total_time:.2f}")
        
        if successful_actions:
            response_times = [a.response_time for a in successful_actions]
            print(f"\n⏱️  Время отклика:")
            print(f"   Среднее: {sum(response_times)/len(response_times):.3f} сек")
            print(f"   Минимум: {min(response_times):.3f} сек")
            print(f"   Максимум: {max(response_times):.3f} сек")
        
        # Статистика по типам сообщений
        message_stats = {}
        for action in successful_actions:
            msg = action.message
            if msg not in message_stats:
                message_stats[msg] = {"count": 0, "avg_time": 0}
            message_stats[msg]["count"] += 1
            message_stats[msg]["avg_time"] += action.response_time
        
        print(f"\n📝 Популярные команды:")
        for msg, stats in sorted(message_stats.items(), key=lambda x: x[1]["count"], reverse=True)[:5]:
            avg_time = stats["avg_time"] / stats["count"]
            print(f"   {msg}: {stats['count']} раз (ср. время: {avg_time:.3f}с)")
        
        if failed_actions:
            print(f"\n❌ Ошибки:")
            error_counts = {}
            for action in failed_actions:
                error = action.error or "Unknown error"
                error_counts[error] = error_counts.get(error, 0) + 1
            
            for error, count in error_counts.items():
                print(f"   {error}: {count}")
        
        # Сохраняем детальный отчет
        self.save_detailed_report()
    
    def save_detailed_report(self):
        """Сохранение детального отчета в файл"""
        os.makedirs("load_testing/reports", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"load_testing/reports/telegram_simulation_{timestamp}.json"
        
        report_data = {
            "test_config": {
                "bot_token": self.bot_token[:10] + "...",  # Скрываем токен
                "timestamp": timestamp
            },
            "actions": [
                {
                    "user_id": a.user_id,
                    "action_type": a.action_type,
                    "message": a.message,
                    "response_time": a.response_time,
                    "success": a.success,
                    "error": a.error
                }
                for a in self.actions
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Детальный отчет сохранен: {filename}")

async def main():
    parser = argparse.ArgumentParser(description='Симуляция пользователей Telegram')
    parser.add_argument('--bot-token', required=True, help='Токен бота')
    parser.add_argument('--users', type=int, default=10, help='Количество пользователей')
    parser.add_argument('--actions', type=int, default=5, help='Действий на пользователя')
    parser.add_argument('--mode', choices=['burst', 'sustained', 'realistic'], default='realistic',
                       help='Режим тестирования: burst (максимальная нагрузка), sustained (постоянная), realistic (реалистичная)')
    parser.add_argument('--students', type=float, default=0.7, help='Доля студентов (0.0-1.0)')
    parser.add_argument('--teachers', type=float, default=0.2, help='Доля преподавателей (0.0-1.0)')
    parser.add_argument('--admins', type=float, default=0.1, help='Доля администраторов (0.0-1.0)')

    args = parser.parse_args()

    # Нормализуем распределение ролей
    total = args.students + args.teachers + args.admins
    distribution = {
        "student": args.students / total,
        "teacher": args.teachers / total,
        "admin": args.admins / total
    }

    simulator = TelegramUserSimulator(args.bot_token)
    await simulator.run_simulation(args.users, args.actions, distribution, args.mode)

if __name__ == "__main__":
    asyncio.run(main())
