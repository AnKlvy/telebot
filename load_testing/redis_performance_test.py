#!/usr/bin/env python3
"""
Нагрузочное тестирование Redis
Тестирует производительность кэширования под нагрузкой
"""
import asyncio
import aioredis
import time
import json
import argparse
import random
import statistics
import string
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class RedisOperation:
    """Результат операции с Redis"""
    operation_type: str
    execution_time: float
    success: bool
    key: str = None
    error: str = None

class RedisPerformanceTester:
    """Тестер производительности Redis"""
    
    def __init__(self):
        # Параметры подключения к Redis
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_db = int(os.getenv("REDIS_DB", "0"))
        self.redis_password = os.getenv("REDIS_PASSWORD", None)
        
        self.operations: List[RedisOperation] = []
        self.redis_pool = None
    
    async def create_redis_pool(self, pool_size: int = 20) -> aioredis.ConnectionPool:
        """Создание пула соединений Redis"""
        try:
            self.redis_pool = aioredis.ConnectionPool.from_url(
                f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}",
                password=self.redis_password,
                max_connections=pool_size,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Проверяем соединение
            redis = aioredis.Redis(connection_pool=self.redis_pool)
            await redis.ping()
            await redis.close()
            
            print(f"✅ Создан пул соединений Redis (размер: {pool_size})")
            return self.redis_pool
            
        except Exception as e:
            print(f"❌ Ошибка создания пула Redis: {e}")
            raise
    
    def generate_test_data(self, size: str = "small") -> str:
        """Генерация тестовых данных разного размера"""
        sizes = {
            "small": 100,      # 100 байт
            "medium": 1024,    # 1 KB
            "large": 10240,    # 10 KB
            "xlarge": 102400   # 100 KB
        }
        
        data_size = sizes.get(size, 100)
        return ''.join(random.choices(string.ascii_letters + string.digits, k=data_size))
    
    async def test_set_operations(self, operations_count: int, data_size: str = "small"):
        """Тестирование SET операций"""
        redis = aioredis.Redis(connection_pool=self.redis_pool)
        
        try:
            for i in range(operations_count):
                key = f"test:set:{i}:{random.randint(1000, 9999)}"
                value = self.generate_test_data(data_size)
                start_time = time.time()
                
                try:
                    await redis.set(key, value, ex=3600)  # TTL 1 час
                    execution_time = time.time() - start_time
                    
                    self.operations.append(RedisOperation(
                        operation_type="SET",
                        execution_time=execution_time,
                        success=True,
                        key=key
                    ))
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    self.operations.append(RedisOperation(
                        operation_type="SET",
                        execution_time=execution_time,
                        success=False,
                        key=key,
                        error=str(e)
                    ))
        finally:
            await redis.close()
    
    async def test_get_operations(self, operations_count: int):
        """Тестирование GET операций"""
        redis = aioredis.Redis(connection_pool=self.redis_pool)
        
        try:
            # Сначала создаем ключи для чтения
            test_keys = []
            for i in range(min(100, operations_count)):
                key = f"test:get:{i}"
                value = self.generate_test_data("medium")
                await redis.set(key, value, ex=3600)
                test_keys.append(key)
            
            # Теперь читаем
            for i in range(operations_count):
                key = random.choice(test_keys)
                start_time = time.time()
                
                try:
                    result = await redis.get(key)
                    execution_time = time.time() - start_time
                    
                    self.operations.append(RedisOperation(
                        operation_type="GET",
                        execution_time=execution_time,
                        success=result is not None,
                        key=key
                    ))
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    self.operations.append(RedisOperation(
                        operation_type="GET",
                        execution_time=execution_time,
                        success=False,
                        key=key,
                        error=str(e)
                    ))
        finally:
            await redis.close()
    
    async def test_hash_operations(self, operations_count: int):
        """Тестирование операций с хэшами"""
        redis = aioredis.Redis(connection_pool=self.redis_pool)
        
        try:
            for i in range(operations_count):
                hash_key = f"test:hash:{i // 10}"  # Группируем по 10
                field = f"field_{i % 10}"
                value = self.generate_test_data("small")
                start_time = time.time()
                
                try:
                    await redis.hset(hash_key, field, value)
                    execution_time = time.time() - start_time
                    
                    self.operations.append(RedisOperation(
                        operation_type="HSET",
                        execution_time=execution_time,
                        success=True,
                        key=f"{hash_key}:{field}"
                    ))
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    self.operations.append(RedisOperation(
                        operation_type="HSET",
                        execution_time=execution_time,
                        success=False,
                        key=f"{hash_key}:{field}",
                        error=str(e)
                    ))
        finally:
            await redis.close()
    
    async def test_list_operations(self, operations_count: int):
        """Тестирование операций со списками"""
        redis = aioredis.Redis(connection_pool=self.redis_pool)
        
        try:
            list_key = "test:list:performance"
            
            for i in range(operations_count):
                value = f"list_item_{i}_{random.randint(1000, 9999)}"
                start_time = time.time()
                
                try:
                    if i % 2 == 0:
                        # LPUSH
                        await redis.lpush(list_key, value)
                        op_type = "LPUSH"
                    else:
                        # RPOP
                        result = await redis.rpop(list_key)
                        op_type = "RPOP"
                    
                    execution_time = time.time() - start_time
                    
                    self.operations.append(RedisOperation(
                        operation_type=op_type,
                        execution_time=execution_time,
                        success=True,
                        key=list_key
                    ))
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    self.operations.append(RedisOperation(
                        operation_type=op_type,
                        execution_time=execution_time,
                        success=False,
                        key=list_key,
                        error=str(e)
                    ))
        finally:
            await redis.close()
    
    async def test_pipeline_operations(self, operations_count: int):
        """Тестирование пакетных операций (pipeline)"""
        redis = aioredis.Redis(connection_pool=self.redis_pool)
        
        try:
            batch_size = 10
            for batch_start in range(0, operations_count, batch_size):
                start_time = time.time()
                
                try:
                    pipe = redis.pipeline()
                    
                    # Добавляем операции в пакет
                    for i in range(batch_start, min(batch_start + batch_size, operations_count)):
                        key = f"test:pipeline:{i}"
                        value = self.generate_test_data("small")
                        pipe.set(key, value, ex=3600)
                    
                    # Выполняем пакет
                    await pipe.execute()
                    execution_time = time.time() - start_time
                    
                    self.operations.append(RedisOperation(
                        operation_type="PIPELINE",
                        execution_time=execution_time,
                        success=True,
                        key=f"batch_{batch_start}_{batch_start + batch_size}"
                    ))
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    self.operations.append(RedisOperation(
                        operation_type="PIPELINE",
                        execution_time=execution_time,
                        success=False,
                        key=f"batch_{batch_start}_{batch_start + batch_size}",
                        error=str(e)
                    ))
        finally:
            await redis.close()
    
    async def worker(self, worker_id: int, operations_per_worker: int):
        """Рабочий процесс для выполнения операций"""
        print(f"🔧 Redis воркер {worker_id} начал работу")
        
        # Распределяем операции
        set_ops = operations_per_worker // 3
        get_ops = operations_per_worker // 3
        hash_ops = operations_per_worker // 6
        list_ops = operations_per_worker // 6
        pipeline_ops = operations_per_worker - set_ops - get_ops - hash_ops - list_ops
        
        tasks = [
            self.test_set_operations(set_ops, "medium"),
            self.test_get_operations(get_ops),
            self.test_hash_operations(hash_ops),
            self.test_list_operations(list_ops),
            self.test_pipeline_operations(pipeline_ops)
        ]
        
        await asyncio.gather(*tasks)
        print(f"✅ Redis воркер {worker_id} завершил работу")
    
    async def run_performance_test(self, concurrent_workers: int = 10, operations_per_worker: int = 100):
        """Запуск теста производительности"""
        print(f"🚀 Запуск теста производительности Redis")
        print(f"🔧 Воркеров: {concurrent_workers}")
        print(f"📊 Операций на воркера: {operations_per_worker}")
        print(f"📈 Всего операций: {concurrent_workers * operations_per_worker}")
        
        # Создаем пул соединений
        await self.create_redis_pool(concurrent_workers + 5)
        
        try:
            # Запускаем воркеров
            tasks = []
            for worker_id in range(concurrent_workers):
                task = asyncio.create_task(
                    self.worker(worker_id, operations_per_worker)
                )
                tasks.append(task)
            
            start_time = time.time()
            await asyncio.gather(*tasks)
            total_time = time.time() - start_time
            
            self.generate_report(total_time)
            
        finally:
            if self.redis_pool:
                await self.redis_pool.disconnect()
    
    def generate_report(self, total_time: float):
        """Генерация отчета о тестировании"""
        if not self.operations:
            print("❌ Нет операций для анализа")
            return
        
        successful_ops = [op for op in self.operations if op.success]
        failed_ops = [op for op in self.operations if not op.success]
        
        print("\n" + "="*60)
        print("📊 ОТЧЕТ О ТЕСТИРОВАНИИ ПРОИЗВОДИТЕЛЬНОСТИ REDIS")
        print("="*60)
        
        print(f"📈 Общая статистика:")
        print(f"   Всего операций: {len(self.operations)}")
        print(f"   Успешных: {len(successful_ops)} ({len(successful_ops)/len(self.operations)*100:.1f}%)")
        print(f"   Неудачных: {len(failed_ops)} ({len(failed_ops)/len(self.operations)*100:.1f}%)")
        print(f"   Общее время: {total_time:.2f} сек")
        print(f"   Операций в секунду: {len(self.operations)/total_time:.2f}")
        
        # Статистика по типам операций
        op_types = {}
        for op in successful_ops:
            if op.operation_type not in op_types:
                op_types[op.operation_type] = []
            op_types[op.operation_type].append(op.execution_time)
        
        print(f"\n⏱️  Время выполнения по типам операций:")
        for op_type, times in op_types.items():
            if times:
                avg_time = statistics.mean(times)
                min_time = min(times)
                max_time = max(times)
                print(f"   {op_type}:")
                print(f"     Количество: {len(times)}")
                print(f"     Среднее время: {avg_time:.4f} сек")
                print(f"     Мин/Макс: {min_time:.4f} / {max_time:.4f} сек")
        
        if failed_ops:
            print(f"\n❌ Ошибки:")
            error_counts = {}
            for op in failed_ops:
                error = op.error or "Unknown error"
                error_counts[error] = error_counts.get(error, 0) + 1
            
            for error, count in error_counts.items():
                print(f"   {error}: {count}")
        
        # Сохраняем детальный отчет
        self.save_detailed_report()
    
    def save_detailed_report(self):
        """Сохранение детального отчета в файл"""
        os.makedirs("load_testing/reports", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"load_testing/reports/redis_test_{timestamp}.json"
        
        report_data = {
            "test_config": {
                "redis_host": self.redis_host,
                "redis_port": self.redis_port,
                "redis_db": self.redis_db,
                "timestamp": timestamp
            },
            "operations": [
                {
                    "operation_type": op.operation_type,
                    "execution_time": op.execution_time,
                    "success": op.success,
                    "key": op.key,
                    "error": op.error
                }
                for op in self.operations
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Детальный отчет сохранен: {filename}")

async def main():
    parser = argparse.ArgumentParser(description='Тестирование производительности Redis')
    parser.add_argument('--workers', type=int, default=10, help='Количество одновременных воркеров')
    parser.add_argument('--operations', type=int, default=100, help='Операций на воркера')
    
    args = parser.parse_args()
    
    tester = RedisPerformanceTester()
    await tester.run_performance_test(args.workers, args.operations)

if __name__ == "__main__":
    asyncio.run(main())
