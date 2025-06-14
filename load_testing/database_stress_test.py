#!/usr/bin/env python3
"""
Нагрузочное тестирование базы данных
Тестирует производительность PostgreSQL под нагрузкой
"""
import asyncio
import asyncpg
import time
import json
import argparse
import random
import statistics
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class DatabaseOperation:
    """Результат операции с базой данных"""
    operation_type: str
    execution_time: float
    success: bool
    rows_affected: int = 0
    error: str = None

class DatabaseStressTester:
    """Тестер нагрузки для базы данных"""
    
    def __init__(self):
        # Параметры подключения к БД
        self.db_config = {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": int(os.getenv("POSTGRES_PORT", "5432")),
            "database": os.getenv("POSTGRES_DB", "telebot"),
            "user": os.getenv("POSTGRES_USER", "telebot_user"),
            "password": os.getenv("POSTGRES_PASSWORD", "your_secure_password")
        }
        self.operations: List[DatabaseOperation] = []
        
        # Тестовые данные
        self.test_courses = ["Python", "JavaScript", "SQL", "DevOps", "ML"]
        self.test_subjects = ["Основы", "Практика", "Проекты", "Тестирование"]
        self.test_names = ["Иван", "Мария", "Алексей", "Елена", "Дмитрий", "Анна"]
        self.test_surnames = ["Иванов", "Петров", "Сидоров", "Козлов", "Новиков"]
    
    async def create_connection_pool(self, pool_size: int = 20) -> asyncpg.Pool:
        """Создание пула соединений"""
        try:
            pool = await asyncpg.create_pool(
                **self.db_config,
                min_size=5,
                max_size=pool_size,
                command_timeout=30
            )
            print(f"✅ Создан пул соединений (размер: {pool_size})")
            return pool
        except Exception as e:
            print(f"❌ Ошибка создания пула соединений: {e}")
            raise
    
    async def test_select_operations(self, pool: asyncpg.Pool, operations_count: int):
        """Тестирование SELECT операций"""
        queries = [
            "SELECT COUNT(*) FROM users",
            "SELECT * FROM courses LIMIT 10",
            "SELECT * FROM subjects WHERE course_id = $1",
            "SELECT u.name, c.name FROM users u JOIN students s ON u.telegram_id = s.telegram_id JOIN courses c ON s.course_id = c.id LIMIT 5",
            "SELECT COUNT(*) FROM microtopics WHERE subject_id = $1"
        ]
        
        for i in range(operations_count):
            query = random.choice(queries)
            start_time = time.time()
            
            try:
                async with pool.acquire() as conn:
                    if "$1" in query:
                        # Запрос с параметром
                        param = random.randint(1, 10)
                        result = await conn.fetch(query, param)
                    else:
                        result = await conn.fetch(query)
                    
                    execution_time = time.time() - start_time
                    
                    self.operations.append(DatabaseOperation(
                        operation_type="SELECT",
                        execution_time=execution_time,
                        success=True,
                        rows_affected=len(result)
                    ))
                    
            except Exception as e:
                execution_time = time.time() - start_time
                self.operations.append(DatabaseOperation(
                    operation_type="SELECT",
                    execution_time=execution_time,
                    success=False,
                    error=str(e)
                ))
    
    async def test_insert_operations(self, pool: asyncpg.Pool, operations_count: int):
        """Тестирование INSERT операций"""
        for i in range(operations_count):
            start_time = time.time()
            
            try:
                async with pool.acquire() as conn:
                    # Создаем тестового пользователя
                    telegram_id = 9000000 + i
                    name = f"{random.choice(self.test_names)} {random.choice(self.test_surnames)}"
                    
                    await conn.execute(
                        "INSERT INTO users (telegram_id, name) VALUES ($1, $2) ON CONFLICT (telegram_id) DO NOTHING",
                        telegram_id, name
                    )
                    
                    execution_time = time.time() - start_time
                    
                    self.operations.append(DatabaseOperation(
                        operation_type="INSERT",
                        execution_time=execution_time,
                        success=True,
                        rows_affected=1
                    ))
                    
            except Exception as e:
                execution_time = time.time() - start_time
                self.operations.append(DatabaseOperation(
                    operation_type="INSERT",
                    execution_time=execution_time,
                    success=False,
                    error=str(e)
                ))
    
    async def test_update_operations(self, pool: asyncpg.Pool, operations_count: int):
        """Тестирование UPDATE операций"""
        for i in range(operations_count):
            start_time = time.time()
            
            try:
                async with pool.acquire() as conn:
                    # Обновляем случайного пользователя
                    telegram_id = 9000000 + random.randint(0, 100)
                    new_name = f"{random.choice(self.test_names)} {random.choice(self.test_surnames)} (Updated)"
                    
                    result = await conn.execute(
                        "UPDATE users SET name = $1 WHERE telegram_id = $2",
                        new_name, telegram_id
                    )
                    
                    execution_time = time.time() - start_time
                    
                    self.operations.append(DatabaseOperation(
                        operation_type="UPDATE",
                        execution_time=execution_time,
                        success=True,
                        rows_affected=1
                    ))
                    
            except Exception as e:
                execution_time = time.time() - start_time
                self.operations.append(DatabaseOperation(
                    operation_type="UPDATE",
                    execution_time=execution_time,
                    success=False,
                    error=str(e)
                ))
    
    async def test_complex_queries(self, pool: asyncpg.Pool, operations_count: int):
        """Тестирование сложных запросов"""
        complex_queries = [
            """
            SELECT 
                c.name as course_name,
                COUNT(s.telegram_id) as students_count,
                AVG(CASE WHEN s.telegram_id IS NOT NULL THEN 1 ELSE 0 END) as avg_activity
            FROM courses c
            LEFT JOIN students s ON c.id = s.course_id
            GROUP BY c.id, c.name
            """,
            """
            SELECT 
                sub.name as subject_name,
                COUNT(m.id) as microtopics_count
            FROM subjects sub
            LEFT JOIN microtopics m ON sub.id = m.subject_id
            GROUP BY sub.id, sub.name
            ORDER BY microtopics_count DESC
            """,
            """
            SELECT 
                u.name,
                COUNT(DISTINCT s.course_id) as courses_count
            FROM users u
            JOIN students s ON u.telegram_id = s.telegram_id
            GROUP BY u.telegram_id, u.name
            HAVING COUNT(DISTINCT s.course_id) > 0
            """
        ]
        
        for i in range(operations_count):
            query = random.choice(complex_queries)
            start_time = time.time()
            
            try:
                async with pool.acquire() as conn:
                    result = await conn.fetch(query)
                    execution_time = time.time() - start_time
                    
                    self.operations.append(DatabaseOperation(
                        operation_type="COMPLEX_SELECT",
                        execution_time=execution_time,
                        success=True,
                        rows_affected=len(result)
                    ))
                    
            except Exception as e:
                execution_time = time.time() - start_time
                self.operations.append(DatabaseOperation(
                    operation_type="COMPLEX_SELECT",
                    execution_time=execution_time,
                    success=False,
                    error=str(e)
                ))
    
    async def worker(self, pool: asyncpg.Pool, worker_id: int, operations_per_worker: int):
        """Рабочий процесс для выполнения операций"""
        print(f"🔧 Воркер {worker_id} начал работу")
        
        # Распределяем операции
        select_ops = operations_per_worker // 2
        insert_ops = operations_per_worker // 4
        update_ops = operations_per_worker // 8
        complex_ops = operations_per_worker - select_ops - insert_ops - update_ops
        
        tasks = [
            self.test_select_operations(pool, select_ops),
            self.test_insert_operations(pool, insert_ops),
            self.test_update_operations(pool, update_ops),
            self.test_complex_queries(pool, complex_ops)
        ]
        
        await asyncio.gather(*tasks)
        print(f"✅ Воркер {worker_id} завершил работу")
    
    async def run_stress_test(self, concurrent_workers: int = 10, operations_per_worker: int = 100):
        """Запуск нагрузочного теста"""
        print(f"🚀 Запуск нагрузочного теста базы данных")
        print(f"🔧 Воркеров: {concurrent_workers}")
        print(f"📊 Операций на воркера: {operations_per_worker}")
        print(f"📈 Всего операций: {concurrent_workers * operations_per_worker}")
        
        # Создаем пул соединений
        pool = await self.create_connection_pool(concurrent_workers + 5)
        
        try:
            # Запускаем воркеров
            tasks = []
            for worker_id in range(concurrent_workers):
                task = asyncio.create_task(
                    self.worker(pool, worker_id, operations_per_worker)
                )
                tasks.append(task)
            
            start_time = time.time()
            await asyncio.gather(*tasks)
            total_time = time.time() - start_time
            
            self.generate_report(total_time)
            
        finally:
            await pool.close()
    
    def generate_report(self, total_time: float):
        """Генерация отчета о тестировании"""
        if not self.operations:
            print("❌ Нет операций для анализа")
            return
        
        successful_ops = [op for op in self.operations if op.success]
        failed_ops = [op for op in self.operations if not op.success]
        
        print("\n" + "="*60)
        print("📊 ОТЧЕТ О НАГРУЗОЧНОМ ТЕСТИРОВАНИИ БД")
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
        filename = f"load_testing/reports/database_test_{timestamp}.json"
        
        report_data = {
            "test_config": {
                "database_host": self.db_config["host"],
                "database_name": self.db_config["database"],
                "timestamp": timestamp
            },
            "operations": [
                {
                    "operation_type": op.operation_type,
                    "execution_time": op.execution_time,
                    "success": op.success,
                    "rows_affected": op.rows_affected,
                    "error": op.error
                }
                for op in self.operations
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Детальный отчет сохранен: {filename}")

async def main():
    parser = argparse.ArgumentParser(description='Нагрузочное тестирование базы данных')
    parser.add_argument('--workers', type=int, default=10, help='Количество одновременных воркеров')
    parser.add_argument('--operations', type=int, default=100, help='Операций на воркера')
    
    args = parser.parse_args()
    
    tester = DatabaseStressTester()
    await tester.run_stress_test(args.workers, args.operations)

if __name__ == "__main__":
    asyncio.run(main())
