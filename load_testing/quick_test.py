#!/usr/bin/env python3
"""
Быстрый тест производительности бота
Простой скрипт для базового тестирования без лишних зависимостей
"""
import asyncio
import aiohttp
import time
import json
import argparse
from datetime import datetime

async def test_webhook(url: str, users: int = 10, requests: int = 5):
    """Простой тест webhook"""
    print(f"🚀 Тестируем webhook: {url}")
    print(f"👥 Пользователей: {users}, запросов на пользователя: {requests}")
    
    results = []
    
    async def send_request(session, user_id):
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
        
        for i in range(requests):
            start = time.time()
            try:
                async with session.post(url, json=fake_update) as resp:
                    duration = time.time() - start
                    results.append({
                        "success": resp.status == 200,
                        "time": duration,
                        "status": resp.status
                    })
                    print(f"✅ User {user_id}: {resp.status} ({duration:.3f}s)")
            except Exception as e:
                duration = time.time() - start
                results.append({
                    "success": False,
                    "time": duration,
                    "error": str(e)
                })
                print(f"❌ User {user_id}: {e}")
            
            await asyncio.sleep(0.5)
    
    async with aiohttp.ClientSession() as session:
        tasks = [send_request(session, i+1000000) for i in range(users)]
        start_time = time.time()
        await asyncio.gather(*tasks)
        total_time = time.time() - start_time
    
    # Отчет
    successful = len([r for r in results if r.success])
    total = len(results)
    avg_time = sum(r["time"] for r in results) / total if total > 0 else 0
    
    print(f"\n📊 РЕЗУЛЬТАТЫ:")
    print(f"   Всего запросов: {total}")
    print(f"   Успешных: {successful} ({successful/total*100:.1f}%)")
    print(f"   Среднее время: {avg_time:.3f} сек")
    print(f"   RPS: {total/total_time:.2f}")
    
    return results

async def main():
    parser = argparse.ArgumentParser(description='Быстрый тест бота')
    parser.add_argument('--url', required=True, help='URL webhook')
    parser.add_argument('--users', type=int, default=10, help='Количество пользователей')
    parser.add_argument('--requests', type=int, default=5, help='Запросов на пользователя')
    
    args = parser.parse_args()
    await test_webhook(args.url, args.users, args.requests)

if __name__ == "__main__":
    asyncio.run(main())
