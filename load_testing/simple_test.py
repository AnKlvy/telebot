#!/usr/bin/env python3
"""
Настоящий нагрузочный тест для быстрого тестирования бота
Отправляет запросы параллельно без пауз
"""
import asyncio
import aiohttp
import time
import argparse
import statistics
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class RequestResult:
    """Результат одного запроса"""
    success: bool
    response_time: float
    status_code: int
    error: str = None

async def send_single_request(session: aiohttp.ClientSession, url: str, user_id: int) -> RequestResult:
    """Отправка одного запроса"""
    fake_update = {
        "update_id": int(time.time() * 1000) + user_id,
        "message": {
            "message_id": int(time.time()),
            "from": {"id": user_id, "first_name": f"TestUser{user_id}"},
            "chat": {"id": user_id, "type": "private"},
            "date": int(time.time()),
            "text": "/start"
        }
    }

    start_time = time.time()
    try:
        async with session.post(url, json=fake_update, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            response_time = time.time() - start_time
            return RequestResult(
                success=resp.status == 200,
                response_time=response_time,
                status_code=resp.status
            )
    except Exception as e:
        response_time = time.time() - start_time
        return RequestResult(
            success=False,
            response_time=response_time,
            status_code=0,
            error=str(e)
        )

async def test_webhook_parallel(url: str, concurrent_requests: int = 10):
    """Настоящий параллельный нагрузочный тест"""
    print(f"🚀 НАГРУЗОЧНЫЙ ТЕСТ: {url}")
    print(f"⚡ Параллельных запросов: {concurrent_requests}")
    print(f"🎯 Все запросы отправляются ОДНОВРЕМЕННО")

    connector = aiohttp.TCPConnector(limit=concurrent_requests + 10)
    timeout = aiohttp.ClientTimeout(total=30)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        # Создаем все задачи сразу
        tasks = []
        for i in range(concurrent_requests):
            task = asyncio.create_task(send_single_request(session, url, 1000000 + i))
            tasks.append(task)

        print(f"⏱️  Запуск {concurrent_requests} параллельных запросов...")
        start_time = time.time()

        # Выполняем ВСЕ запросы одновременно
        results = await asyncio.gather(*tasks, return_exceptions=True)

        total_time = time.time() - start_time

        # Обрабатываем результаты
        valid_results = [r for r in results if isinstance(r, RequestResult)]
        successful = [r for r in valid_results if r.success]
        failed = [r for r in valid_results if not r.success]

        print_results(valid_results, successful, failed, total_time, concurrent_requests)

def print_results(all_results: List[RequestResult], successful: List[RequestResult],
                 failed: List[RequestResult], total_time: float, concurrent_requests: int):
    """Вывод результатов тестирования"""
    print(f"\n" + "="*60)
    print("📊 РЕЗУЛЬТАТЫ НАГРУЗОЧНОГО ТЕСТА")
    print("="*60)

    print(f"📈 Общая статистика:")
    print(f"   Всего запросов: {len(all_results)}")
    print(f"   Успешных: {len(successful)} ({len(successful)/len(all_results)*100:.1f}%)")
    print(f"   Неудачных: {len(failed)} ({len(failed)/len(all_results)*100:.1f}%)")
    print(f"   Общее время: {total_time:.3f} сек")
    print(f"   RPS (запросов/сек): {len(all_results)/total_time:.2f}")

    if successful:
        response_times = [r.response_time for r in successful]
        print(f"\n⏱️  Время отклика (успешные запросы):")
        print(f"   Среднее: {statistics.mean(response_times):.3f} сек")
        print(f"   Медиана: {statistics.median(response_times):.3f} сек")
        print(f"   Минимум: {min(response_times):.3f} сек")
        print(f"   Максимум: {max(response_times):.3f} сек")
        if len(response_times) > 1:
            p95 = sorted(response_times)[int(len(response_times) * 0.95)]
            print(f"   95-й процентиль: {p95:.3f} сек")

    if failed:
        print(f"\n❌ Ошибки:")
        error_counts = {}
        for r in failed:
            error_key = f"HTTP {r.status_code}" if r.status_code > 0 else r.error
            error_counts[error_key] = error_counts.get(error_key, 0) + 1

        for error, count in error_counts.items():
            print(f"   {error}: {count}")

    # Оценка производительности
    rps = len(all_results) / total_time
    success_rate = len(successful) / len(all_results) * 100

    print(f"\n🎯 Оценка производительности:")
    if success_rate >= 95 and rps >= 50:
        print("   ✅ ОТЛИЧНО - Высокая производительность")
    elif success_rate >= 90 and rps >= 20:
        print("   ⚠️  ХОРОШО - Приемлемая производительность")
    elif success_rate >= 80:
        print("   ⚠️  УДОВЛЕТВОРИТЕЛЬНО - Есть проблемы")
    else:
        print("   ❌ ПЛОХО - Серьезные проблемы производительности")

async def main():
    parser = argparse.ArgumentParser(description='Быстрый нагрузочный тест webhook')
    parser.add_argument('--url', required=True, help='URL webhook endpoint')
    parser.add_argument('--requests', type=int, default=10, help='Количество параллельных запросов')

    args = parser.parse_args()
    await test_webhook_parallel(args.url, args.requests)

if __name__ == "__main__":
    asyncio.run(main())
