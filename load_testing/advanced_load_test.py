#!/usr/bin/env python3
"""
Продвинутый нагрузочный тест с мониторингом ресурсов
Включает различные сценарии нагрузки и детальную аналитику
"""
import asyncio
import aiohttp
import time
import json
import argparse
import statistics
import psutil
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import os

@dataclass
class TestResult:
    """Результат одного запроса"""
    success: bool
    response_time: float
    status_code: int
    timestamp: float
    user_id: int
    error: str = None

@dataclass
class SystemMetrics:
    """Метрики системы"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    network_sent_mb: float
    network_recv_mb: float

class AdvancedLoadTester:
    """Продвинутый тестер нагрузки"""
    
    def __init__(self, webhook_url: str, concurrent_users: int = 10):
        self.webhook_url = webhook_url
        self.concurrent_users = concurrent_users
        self.results: List[TestResult] = []
        self.system_metrics: List[SystemMetrics] = []
        self.monitoring_active = False
        self.start_network_stats = None
        
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
                    status_code=response.status,
                    timestamp=time.time(),
                    user_id=user_id
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                success=False,
                response_time=response_time,
                status_code=0,
                timestamp=time.time(),
                user_id=user_id,
                error=str(e)
            )
    
    def start_system_monitoring(self, interval: float = 1.0):
        """Запуск мониторинга системных ресурсов"""
        self.monitoring_active = True
        self.start_network_stats = psutil.net_io_counters()
        
        def monitor():
            while self.monitoring_active:
                try:
                    # Получаем метрики системы
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    memory = psutil.virtual_memory()
                    network = psutil.net_io_counters()
                    
                    # Вычисляем сетевой трафик с начала теста
                    network_sent_mb = (network.bytes_sent - self.start_network_stats.bytes_sent) / 1024 / 1024
                    network_recv_mb = (network.bytes_recv - self.start_network_stats.bytes_recv) / 1024 / 1024
                    
                    metrics = SystemMetrics(
                        timestamp=time.time(),
                        cpu_percent=cpu_percent,
                        memory_percent=memory.percent,
                        memory_used_mb=memory.used / 1024 / 1024,
                        network_sent_mb=network_sent_mb,
                        network_recv_mb=network_recv_mb
                    )
                    
                    self.system_metrics.append(metrics)
                    time.sleep(interval)
                    
                except Exception as e:
                    print(f"⚠️  Ошибка мониторинга: {e}")
                    break
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def stop_system_monitoring(self):
        """Остановка мониторинга системных ресурсов"""
        self.monitoring_active = False
    
    async def burst_test(self, session: aiohttp.ClientSession, total_requests: int):
        """Взрывной тест - все запросы одновременно"""
        print(f"⚡ BURST TEST: {total_requests} запросов одновременно")
        
        tasks = []
        for i in range(total_requests):
            user_id = 1000000 + i
            task = asyncio.create_task(self.send_request(session, user_id, "/start"))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, TestResult):
                self.results.append(result)
    
    async def sustained_test(self, session: aiohttp.ClientSession, duration_seconds: int, rps_target: int):
        """Постоянная нагрузка с заданным RPS"""
        print(f"🔄 SUSTAINED TEST: {rps_target} RPS в течение {duration_seconds} секунд")
        
        interval = 1.0 / rps_target if rps_target > 0 else 0.1
        end_time = time.time() + duration_seconds
        request_count = 0
        
        while time.time() < end_time:
            user_id = 2000000 + request_count
            result = await self.send_request(session, user_id, "/start")
            self.results.append(result)
            
            request_count += 1
            await asyncio.sleep(interval)
    
    async def ramp_up_test(self, session: aiohttp.ClientSession, duration_seconds: int, max_rps: int):
        """Нарастающая нагрузка"""
        print(f"📈 RAMP-UP TEST: от 1 до {max_rps} RPS за {duration_seconds} секунд")
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        request_count = 0
        
        while time.time() < end_time:
            # Вычисляем текущий RPS на основе прогресса
            progress = (time.time() - start_time) / duration_seconds
            current_rps = max(1, int(max_rps * progress))
            interval = 1.0 / current_rps
            
            user_id = 3000000 + request_count
            result = await self.send_request(session, user_id, "/start")
            self.results.append(result)
            
            request_count += 1
            await asyncio.sleep(interval)
    
    async def run_advanced_test(self, test_type: str = "burst", **kwargs):
        """Запуск продвинутого теста"""
        print(f"🚀 Запуск продвинутого нагрузочного теста: {self.webhook_url}")
        print(f"🎯 Тип теста: {test_type.upper()}")
        
        # Запускаем мониторинг системы
        self.start_system_monitoring()
        
        connector = aiohttp.TCPConnector(limit=self.concurrent_users * 2)
        timeout = aiohttp.ClientTimeout(total=30)
        
        try:
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                start_time = time.time()
                
                if test_type == "burst":
                    await self.burst_test(session, kwargs.get('total_requests', 100))
                elif test_type == "sustained":
                    await self.sustained_test(session, kwargs.get('duration', 60), kwargs.get('rps', 10))
                elif test_type == "ramp_up":
                    await self.ramp_up_test(session, kwargs.get('duration', 60), kwargs.get('max_rps', 50))
                
                total_time = time.time() - start_time
                
        finally:
            self.stop_system_monitoring()
        
        self.generate_advanced_report(total_time, test_type)
    
    def generate_advanced_report(self, total_time: float, test_type: str):
        """Генерация продвинутого отчета"""
        if not self.results:
            print("❌ Нет результатов для анализа")
            return
        
        successful_requests = [r for r in self.results if r.success]
        failed_requests = [r for r in self.results if not r.success]
        
        print("\n" + "="*80)
        print(f"📊 ПРОДВИНУТЫЙ ОТЧЕТ О НАГРУЗОЧНОМ ТЕСТИРОВАНИИ ({test_type.upper()})")
        print("="*80)
        
        # Основная статистика
        self.print_basic_stats(successful_requests, failed_requests, total_time)
        
        # Статистика производительности
        if successful_requests:
            self.print_performance_stats(successful_requests)
        
        # Системные метрики
        if self.system_metrics:
            self.print_system_stats()
        
        # Анализ ошибок
        if failed_requests:
            self.print_error_analysis(failed_requests)
        
        # Сохраняем детальный отчет
        self.save_advanced_report(test_type)
    
    def print_basic_stats(self, successful: List[TestResult], failed: List[TestResult], total_time: float):
        """Вывод базовой статистики"""
        total_requests = len(self.results)
        success_rate = len(successful) / total_requests * 100
        rps = total_requests / total_time
        
        print(f"📈 Общая статистика:")
        print(f"   Всего запросов: {total_requests}")
        print(f"   Успешных: {len(successful)} ({success_rate:.1f}%)")
        print(f"   Неудачных: {len(failed)} ({100-success_rate:.1f}%)")
        print(f"   Общее время: {total_time:.2f} сек")
        print(f"   RPS (запросов/сек): {rps:.2f}")

    def print_performance_stats(self, successful: List[TestResult]):
        """Вывод статистики производительности"""
        response_times = [r.response_time for r in successful]

        print(f"\n⏱️  Время отклика:")
        print(f"   Среднее: {statistics.mean(response_times):.3f} сек")
        print(f"   Медиана: {statistics.median(response_times):.3f} сек")
        print(f"   Минимум: {min(response_times):.3f} сек")
        print(f"   Максимум: {max(response_times):.3f} сек")

        if len(response_times) > 1:
            sorted_times = sorted(response_times)
            p95 = sorted_times[int(len(sorted_times) * 0.95)]
            p99 = sorted_times[int(len(sorted_times) * 0.99)]
            print(f"   95-й процентиль: {p95:.3f} сек")
            print(f"   99-й процентиль: {p99:.3f} сек")

    def print_system_stats(self):
        """Вывод системной статистики"""
        if not self.system_metrics:
            return

        cpu_values = [m.cpu_percent for m in self.system_metrics]
        memory_values = [m.memory_percent for m in self.system_metrics]

        print(f"\n🖥️  Системные ресурсы:")
        print(f"   CPU среднее/макс: {statistics.mean(cpu_values):.1f}% / {max(cpu_values):.1f}%")
        print(f"   Память среднее/макс: {statistics.mean(memory_values):.1f}% / {max(memory_values):.1f}%")

        if self.system_metrics:
            last_metric = self.system_metrics[-1]
            print(f"   Сеть: {last_metric.network_sent_mb:.2f}MB отправлено, {last_metric.network_recv_mb:.2f}MB получено")

    def print_error_analysis(self, failed: List[TestResult]):
        """Анализ ошибок"""
        print(f"\n❌ Анализ ошибок:")
        error_counts = {}
        for req in failed:
            error_key = f"HTTP {req.status_code}" if req.status_code > 0 else req.error
            error_counts[error_key] = error_counts.get(error_key, 0) + 1

        for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {error}: {count}")

    def save_advanced_report(self, test_type: str):
        """Сохранение продвинутого отчета"""
        os.makedirs("load_testing/reports", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"load_testing/reports/advanced_test_{test_type}_{timestamp}.json"

        report_data = {
            "test_config": {
                "webhook_url": self.webhook_url,
                "test_type": test_type,
                "timestamp": timestamp
            },
            "results": [asdict(r) for r in self.results],
            "system_metrics": [asdict(m) for m in self.system_metrics]
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Отчет сохранен: {filename}")

async def main():
    parser = argparse.ArgumentParser(description='Продвинутое нагрузочное тестирование')
    parser.add_argument('--url', required=True, help='URL webhook endpoint')
    parser.add_argument('--users', type=int, default=10, help='Количество пользователей')
    parser.add_argument('--type', choices=['burst', 'sustained', 'ramp_up'], default='burst', help='Тип теста')
    parser.add_argument('--requests', type=int, default=100, help='Количество запросов (для burst)')
    parser.add_argument('--duration', type=int, default=60, help='Длительность в секундах')
    parser.add_argument('--rps', type=int, default=10, help='Запросов в секунду (для sustained)')
    parser.add_argument('--max-rps', type=int, default=50, help='Максимальный RPS (для ramp_up)')

    args = parser.parse_args()

    tester = AdvancedLoadTester(args.url, args.users)

    test_params = {
        'total_requests': args.requests,
        'duration': args.duration,
        'rps': args.rps,
        'max_rps': args.max_rps
    }

    await tester.run_advanced_test(args.type, **test_params)

if __name__ == "__main__":
    asyncio.run(main())

    def print_performance_stats(self, successful: List[TestResult]):
        """Вывод статистики производительности"""
        response_times = [r.response_time for r in successful]

        print(f"\n⏱️  Время отклика:")
        print(f"   Среднее: {statistics.mean(response_times):.3f} сек")
        print(f"   Медиана: {statistics.median(response_times):.3f} сек")
        print(f"   Минимум: {min(response_times):.3f} сек")
        print(f"   Максимум: {max(response_times):.3f} сек")

        if len(response_times) > 1:
            sorted_times = sorted(response_times)
            p95 = sorted_times[int(len(sorted_times) * 0.95)]
            p99 = sorted_times[int(len(sorted_times) * 0.99)]
            print(f"   95-й процентиль: {p95:.3f} сек")
            print(f"   99-й процентиль: {p99:.3f} сек")

    def print_system_stats(self):
        """Вывод системной статистики"""
        if not self.system_metrics:
            return

        cpu_values = [m.cpu_percent for m in self.system_metrics]
        memory_values = [m.memory_percent for m in self.system_metrics]

        print(f"\n🖥️  Системные ресурсы:")
        print(f"   CPU среднее/макс: {statistics.mean(cpu_values):.1f}% / {max(cpu_values):.1f}%")
        print(f"   Память среднее/макс: {statistics.mean(memory_values):.1f}% / {max(memory_values):.1f}%")

        if self.system_metrics:
            last_metric = self.system_metrics[-1]
            print(f"   Сеть: {last_metric.network_sent_mb:.2f}MB отправлено, {last_metric.network_recv_mb:.2f}MB получено")

    def print_error_analysis(self, failed: List[TestResult]):
        """Анализ ошибок"""
        print(f"\n❌ Анализ ошибок:")
        error_counts = {}
        for req in failed:
            error_key = f"HTTP {req.status_code}" if req.status_code > 0 else req.error
            error_counts[error_key] = error_counts.get(error_key, 0) + 1

        for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {error}: {count}")

    def save_advanced_report(self, test_type: str):
        """Сохранение продвинутого отчета"""
        os.makedirs("load_testing/reports", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"load_testing/reports/advanced_test_{test_type}_{timestamp}.json"

        report_data = {
            "test_config": {
                "webhook_url": self.webhook_url,
                "test_type": test_type,
                "timestamp": timestamp
            },
            "results": [asdict(r) for r in self.results],
            "system_metrics": [asdict(m) for m in self.system_metrics]
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Отчет сохранен: {filename}")

async def main():
    parser = argparse.ArgumentParser(description='Продвинутое нагрузочное тестирование')
    parser.add_argument('--url', required=True, help='URL webhook endpoint')
    parser.add_argument('--users', type=int, default=10, help='Количество пользователей')
    parser.add_argument('--type', choices=['burst', 'sustained', 'ramp_up'], default='burst', help='Тип теста')
    parser.add_argument('--requests', type=int, default=100, help='Количество запросов (для burst)')
    parser.add_argument('--duration', type=int, default=60, help='Длительность в секундах')
    parser.add_argument('--rps', type=int, default=10, help='Запросов в секунду (для sustained)')
    parser.add_argument('--max-rps', type=int, default=50, help='Максимальный RPS (для ramp_up)')

    args = parser.parse_args()

    tester = AdvancedLoadTester(args.url, args.users)

    test_params = {
        'total_requests': args.requests,
        'duration': args.duration,
        'rps': args.rps,
        'max_rps': args.max_rps
    }

    await tester.run_advanced_test(args.type, **test_params)

if __name__ == "__main__":
    asyncio.run(main())
