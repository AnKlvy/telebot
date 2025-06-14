#!/usr/bin/env python3
"""
Комплексное нагрузочное тестирование всех компонентов системы
Тестирует webhook, базу данных и Redis одновременно
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

# Импортируем наши тестеры
from webhook_load_test import WebhookLoadTester
from database_stress_test import DatabaseStressTester
from redis_performance_test import RedisPerformanceTester

@dataclass
class ComponentResult:
    """Результат тестирования компонента"""
    component: str
    success_rate: float
    avg_response_time: float
    total_operations: int
    errors: int
    duration: float

class FullSystemLoadTester:
    """Комплексный тестер всей системы"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.component_results: List[ComponentResult] = []
        
    async def test_webhook_component(self, users: int, requests_per_user: int) -> ComponentResult:
        """Тестирование webhook компонента"""
        print("🌐 Тестирование Webhook компонента...")
        
        tester = WebhookLoadTester(self.webhook_url, users)
        start_time = time.time()
        
        # Запускаем тест в burst режиме (без пауз)
        await tester.run_load_test(duration_seconds=300, requests_per_user=requests_per_user, 
                                 test_mode="burst", delay_between_requests=0.0)
        
        duration = time.time() - start_time
        
        # Анализируем результаты
        successful = [r for r in tester.results if r.success]
        failed = [r for r in tester.results if not r.success]
        
        success_rate = len(successful) / len(tester.results) * 100 if tester.results else 0
        avg_response_time = statistics.mean([r.response_time for r in successful]) if successful else 0
        
        return ComponentResult(
            component="Webhook",
            success_rate=success_rate,
            avg_response_time=avg_response_time,
            total_operations=len(tester.results),
            errors=len(failed),
            duration=duration
        )
    
    async def test_database_component(self, workers: int, operations_per_worker: int) -> ComponentResult:
        """Тестирование базы данных"""
        print("🗄️  Тестирование Database компонента...")
        
        tester = DatabaseStressTester()
        start_time = time.time()
        
        try:
            await tester.run_stress_test(workers, operations_per_worker)
            duration = time.time() - start_time
            
            # Анализируем результаты
            successful = [op for op in tester.operations if op.success]
            failed = [op for op in tester.operations if not op.success]
            
            success_rate = len(successful) / len(tester.operations) * 100 if tester.operations else 0
            avg_response_time = statistics.mean([op.execution_time for op in successful]) if successful else 0
            
            return ComponentResult(
                component="Database",
                success_rate=success_rate,
                avg_response_time=avg_response_time,
                total_operations=len(tester.operations),
                errors=len(failed),
                duration=duration
            )
            
        except Exception as e:
            print(f"❌ Ошибка тестирования БД: {e}")
            return ComponentResult(
                component="Database",
                success_rate=0,
                avg_response_time=0,
                total_operations=0,
                errors=1,
                duration=time.time() - start_time
            )
    
    async def test_redis_component(self, workers: int, operations_per_worker: int) -> ComponentResult:
        """Тестирование Redis"""
        print("🔴 Тестирование Redis компонента...")
        
        tester = RedisPerformanceTester()
        start_time = time.time()
        
        try:
            await tester.run_performance_test(workers, operations_per_worker)
            duration = time.time() - start_time
            
            # Анализируем результаты
            successful = [op for op in tester.operations if op.success]
            failed = [op for op in tester.operations if not op.success]
            
            success_rate = len(successful) / len(tester.operations) * 100 if tester.operations else 0
            avg_response_time = statistics.mean([op.execution_time for op in successful]) if successful else 0
            
            return ComponentResult(
                component="Redis",
                success_rate=success_rate,
                avg_response_time=avg_response_time,
                total_operations=len(tester.operations),
                errors=len(failed),
                duration=duration
            )
            
        except Exception as e:
            print(f"❌ Ошибка тестирования Redis: {e}")
            return ComponentResult(
                component="Redis",
                success_rate=0,
                avg_response_time=0,
                total_operations=0,
                errors=1,
                duration=time.time() - start_time
            )
    
    async def run_full_test(self, scenario: str = "basic"):
        """Запуск полного комплексного теста"""
        print(f"🚀 КОМПЛЕКСНОЕ НАГРУЗОЧНОЕ ТЕСТИРОВАНИЕ")
        print(f"🎯 Сценарий: {scenario.upper()}")
        print("="*60)
        
        # Определяем параметры для разных сценариев
        scenarios = {
            "basic": {
                "webhook_users": 10,
                "webhook_requests": 5,
                "db_workers": 5,
                "db_operations": 50,
                "redis_workers": 5,
                "redis_operations": 50
            },
            "medium": {
                "webhook_users": 25,
                "webhook_requests": 10,
                "db_workers": 10,
                "db_operations": 100,
                "redis_workers": 10,
                "redis_operations": 100
            },
            "heavy": {
                "webhook_users": 50,
                "webhook_requests": 20,
                "db_workers": 20,
                "db_operations": 200,
                "redis_workers": 20,
                "redis_operations": 200
            }
        }
        
        params = scenarios.get(scenario, scenarios["basic"])
        
        start_time = time.time()
        
        # Запускаем тесты параллельно
        tasks = [
            self.test_webhook_component(params["webhook_users"], params["webhook_requests"]),
            self.test_database_component(params["db_workers"], params["db_operations"]),
            self.test_redis_component(params["redis_workers"], params["redis_operations"])
        ]
        
        print("⚡ Запуск параллельного тестирования всех компонентов...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        # Обрабатываем результаты
        for result in results:
            if isinstance(result, ComponentResult):
                self.component_results.append(result)
            else:
                print(f"❌ Ошибка в тесте: {result}")
        
        self.generate_full_report(total_time, scenario)
    
    def generate_full_report(self, total_time: float, scenario: str):
        """Генерация комплексного отчета"""
        print("\n" + "="*80)
        print("📊 КОМПЛЕКСНЫЙ ОТЧЕТ О НАГРУЗОЧНОМ ТЕСТИРОВАНИИ")
        print("="*80)
        
        print(f"🎯 Сценарий: {scenario.upper()}")
        print(f"⏱️  Общее время тестирования: {total_time:.2f} сек")
        print(f"📈 Компонентов протестировано: {len(self.component_results)}")
        
        # Статистика по компонентам
        print(f"\n📊 Результаты по компонентам:")
        print("-" * 80)
        print(f"{'Компонент':<12} {'Успех %':<10} {'Ср.время':<12} {'Операций':<12} {'Ошибок':<10}")
        print("-" * 80)
        
        total_operations = 0
        total_errors = 0
        overall_success_rates = []
        
        for result in self.component_results:
            print(f"{result.component:<12} {result.success_rate:<10.1f} "
                  f"{result.avg_response_time:<12.4f} {result.total_operations:<12} {result.errors:<10}")
            
            total_operations += result.total_operations
            total_errors += result.errors
            overall_success_rates.append(result.success_rate)
        
        # Общая оценка системы
        overall_success_rate = statistics.mean(overall_success_rates) if overall_success_rates else 0
        
        print(f"\n🎯 Общая оценка системы:")
        print(f"   Общий процент успеха: {overall_success_rate:.1f}%")
        print(f"   Всего операций: {total_operations}")
        print(f"   Всего ошибок: {total_errors}")
        
        # Рекомендации
        print(f"\n💡 Рекомендации:")
        if overall_success_rate >= 95:
            print("   ✅ Система работает отлично под нагрузкой")
        elif overall_success_rate >= 90:
            print("   ⚠️  Система работает хорошо, но есть место для улучшений")
        elif overall_success_rate >= 80:
            print("   ⚠️  Система работает удовлетворительно, требуется оптимизация")
        else:
            print("   ❌ Система имеет серьезные проблемы производительности")
        
        # Сохраняем отчет
        self.save_full_report(scenario)
    
    def save_full_report(self, scenario: str):
        """Сохранение комплексного отчета"""
        os.makedirs("load_testing/reports", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"load_testing/reports/full_test_{scenario}_{timestamp}.json"
        
        report_data = {
            "test_config": {
                "webhook_url": self.webhook_url,
                "scenario": scenario,
                "timestamp": timestamp
            },
            "component_results": [
                {
                    "component": r.component,
                    "success_rate": r.success_rate,
                    "avg_response_time": r.avg_response_time,
                    "total_operations": r.total_operations,
                    "errors": r.errors,
                    "duration": r.duration
                }
                for r in self.component_results
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Комплексный отчет сохранен: {filename}")

async def main():
    parser = argparse.ArgumentParser(description='Комплексное нагрузочное тестирование')
    parser.add_argument('--url', required=True, help='URL webhook endpoint')
    parser.add_argument('--scenario', choices=['basic', 'medium', 'heavy'], default='basic',
                       help='Сценарий тестирования')
    
    args = parser.parse_args()
    
    tester = FullSystemLoadTester(args.url)
    await tester.run_full_test(args.scenario)

if __name__ == "__main__":
    asyncio.run(main())
