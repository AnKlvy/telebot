#!/usr/bin/env python3
"""
Нагрузочное тестирование webhook endpoint бота
Тестирует HTTP производительность без использования Telegram API
"""
import asyncio
import aiohttp
import time
import json
import argparse
import statistics
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass
import os

@dataclass
class TestResult:
    """Результат одного запроса"""
    success: bool
    response_time: float
    status_code: int
    error: str = None

class WebhookLoadTester:
    """Тестер нагрузки для webhook endpoint"""
    
    def __init__(self, webhook_url: str, concurrent_users: int = 10):
        self.webhook_url = webhook_url
        self.concurrent_users = concurrent_users
        self.results: List[TestResult] = []
        
    def create_fake_telegram_update(self, user_id: int, message_text: str = "/start") -> Dict[str, Any]:
        """Создает поддельное обновление от Telegram"""
        return {
            "update_id": int(time.time() * 1000) + user_id,
            "message": {
                "message_id": int(time.time()),
                "from": {
                    "id": user_id,
                    "is_bot": False,
                    "first_name": f"TestUser{user_id}",
                    "username": f"testuser{user_id}",
                    "language_code": "ru"
                },
                "chat": {
                    "id": user_id,
                    "first_name": f"TestUser{user_id}",
                    "username": f"testuser{user_id}",
                    "type": "private"
                },
                "date": int(time.time()),
                "text": message_text
            }
        }
    
    async def send_request(self, session: aiohttp.ClientSession, user_id: int, message: str = "/start") -> TestResult:
        """Отправляет один запрос к webhook"""
        start_time = time.time()
        
        try:
            fake_update = self.create_fake_telegram_update(user_id, message)
            
            async with session.post(
                self.webhook_url,
                json=fake_update,
                headers={'Content-Type': 'application/json'},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_time = time.time() - start_time
                
                return TestResult(
                    success=response.status == 200,
                    response_time=response_time,
                    status_code=response.status
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                success=False,
                response_time=response_time,
                status_code=0,
                error=str(e)
            )
    
    async def user_simulation(self, session: aiohttp.ClientSession, user_id: int, requests_per_user: int, delay_between_requests: float = 0.0):
        """Симуляция одного пользователя"""
        messages = ["/start", "📚 Мои курсы", "📊 Статистика", "⚙️ Настройки", "/help"]

        for i in range(requests_per_user):
            message = messages[i % len(messages)]
            result = await self.send_request(session, user_id, message)
            self.results.append(result)

            # Настраиваемая пауза между запросами от одного пользователя
            if delay_between_requests > 0 and i < requests_per_user - 1:
                await asyncio.sleep(delay_between_requests)
    
    async def run_load_test(self, duration_seconds: int = 60, requests_per_user: int = 10,
                           test_mode: str = "burst", delay_between_requests: float = 0.0):
        """Запуск нагрузочного теста

        Args:
            duration_seconds: Максимальная длительность теста
            requests_per_user: Запросов на пользователя
            test_mode: Режим тестирования ('burst', 'sustained', 'realistic')
            delay_between_requests: Пауза между запросами одного пользователя
        """
        print(f"🚀 Запуск нагрузочного теста webhook: {self.webhook_url}")
        print(f"👥 Пользователей: {self.concurrent_users}")
        print(f"⏱️  Максимальная длительность: {duration_seconds} секунд")
        print(f"📨 Запросов на пользователя: {requests_per_user}")
        print(f"🎯 Режим тестирования: {test_mode}")

        if test_mode == "burst":
            delay_between_requests = 0.0
            print("⚡ BURST MODE: Максимальная нагрузка без пауз")
        elif test_mode == "sustained":
            delay_between_requests = 0.1
            print("🔄 SUSTAINED MODE: Постоянная нагрузка с небольшими паузами")
        elif test_mode == "realistic":
            delay_between_requests = 1.0
            print("👤 REALISTIC MODE: Имитация реальных пользователей")

        connector = aiohttp.TCPConnector(limit=self.concurrent_users * 2)
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Создаем задачи для каждого пользователя
            tasks = []
            for user_id in range(1, self.concurrent_users + 1):
                task = asyncio.create_task(
                    self.user_simulation(session, user_id + 1000000, requests_per_user, delay_between_requests)
                )
                tasks.append(task)

            # Запускаем все задачи с таймаутом
            start_time = time.time()
            try:
                await asyncio.wait_for(asyncio.gather(*tasks), timeout=duration_seconds)
            except asyncio.TimeoutError:
                print(f"⏰ Тест остановлен по таймауту ({duration_seconds} сек)")

            total_time = time.time() - start_time

        self.generate_report(total_time)
    
    def generate_report(self, total_time: float):
        """Генерация отчета о тестировании"""
        if not self.results:
            print("❌ Нет результатов для анализа")
            return
        
        successful_requests = [r for r in self.results if r.success]
        failed_requests = [r for r in self.results if not r.success]
        
        response_times = [r.response_time for r in successful_requests]
        
        print("\n" + "="*60)
        print("📊 ОТЧЕТ О НАГРУЗОЧНОМ ТЕСТИРОВАНИИ")
        print("="*60)
        
        print(f"📈 Общая статистика:")
        print(f"   Всего запросов: {len(self.results)}")
        print(f"   Успешных: {len(successful_requests)} ({len(successful_requests)/len(self.results)*100:.1f}%)")
        print(f"   Неудачных: {len(failed_requests)} ({len(failed_requests)/len(self.results)*100:.1f}%)")
        print(f"   Общее время: {total_time:.2f} сек")
        print(f"   RPS: {len(self.results)/total_time:.2f}")
        
        if response_times:
            print(f"\n⏱️  Время отклика (успешные запросы):")
            print(f"   Среднее: {statistics.mean(response_times):.3f} сек")
            print(f"   Медиана: {statistics.median(response_times):.3f} сек")
            print(f"   Минимум: {min(response_times):.3f} сек")
            print(f"   Максимум: {max(response_times):.3f} сек")
            if len(response_times) > 1:
                print(f"   95-й процентиль: {sorted(response_times)[int(len(response_times)*0.95)]:.3f} сек")
        
        if failed_requests:
            print(f"\n❌ Ошибки:")
            error_counts = {}
            for req in failed_requests:
                error_key = f"HTTP {req.status_code}" if req.status_code > 0 else req.error
                error_counts[error_key] = error_counts.get(error_key, 0) + 1
            
            for error, count in error_counts.items():
                print(f"   {error}: {count}")
        
        # Сохраняем детальный отчет
        self.save_detailed_report()
    
    def save_detailed_report(self):
        """Сохранение детального отчета в файл"""
        os.makedirs("load_testing/reports", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"load_testing/reports/webhook_test_{timestamp}.json"
        
        report_data = {
            "test_config": {
                "webhook_url": self.webhook_url,
                "concurrent_users": self.concurrent_users,
                "timestamp": timestamp
            },
            "results": [
                {
                    "success": r.success,
                    "response_time": r.response_time,
                    "status_code": r.status_code,
                    "error": r.error
                }
                for r in self.results
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Детальный отчет сохранен: {filename}")

async def main():
    parser = argparse.ArgumentParser(description='Нагрузочное тестирование webhook')
    parser.add_argument('--url', required=True, help='URL webhook endpoint')
    parser.add_argument('--users', type=int, default=10, help='Количество одновременных пользователей')
    parser.add_argument('--duration', type=int, default=60, help='Максимальная длительность теста в секундах')
    parser.add_argument('--requests', type=int, default=10, help='Запросов на пользователя')
    parser.add_argument('--mode', choices=['burst', 'sustained', 'realistic'], default='burst',
                       help='Режим тестирования: burst (максимальная нагрузка), sustained (постоянная), realistic (реалистичная)')
    parser.add_argument('--delay', type=float, default=0.0, help='Пауза между запросами одного пользователя (сек)')

    args = parser.parse_args()

    tester = WebhookLoadTester(args.url, args.users)
    await tester.run_load_test(args.duration, args.requests, args.mode, args.delay)

if __name__ == "__main__":
    asyncio.run(main())
