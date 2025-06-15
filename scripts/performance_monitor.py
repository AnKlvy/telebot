"""
Скрипт для мониторинга производительности бота в реальном времени
"""
import asyncio
import json
import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import redis.asyncio as redis
from os import getenv
from dotenv import load_dotenv

load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Монитор производительности бота"""
    
    def __init__(self):
        self.redis_client = None
        self.monitoring = False
        
    async def connect_redis(self):
        """Подключение к Redis"""
        try:
            redis_host = getenv("REDIS_HOST", "redis")
            redis_port = int(getenv("REDIS_PORT", "6379"))
            redis_db = int(getenv("REDIS_DB", "0"))
            redis_password = getenv("REDIS_PASSWORD", None)
            
            self.redis_client = redis.from_url(
                f"redis://{redis_host}:{redis_port}/{redis_db}",
                password=redis_password,
                encoding="utf-8",
                decode_responses=True
            )
            
            await self.redis_client.ping()
            logger.info("✅ Подключение к Redis успешно")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Redis: {e}")
            return False
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """Получить статистику производительности из Redis"""
        if not self.redis_client:
            return {}
        
        try:
            # Получаем агрегированную статистику
            stats_data = await self.redis_client.get("performance_stats")
            if stats_data:
                stats = json.loads(stats_data)
            else:
                stats = {}
            
            # Получаем метрики за последние 5 минут
            current_time = datetime.now()
            five_minutes_ago = current_time - timedelta(minutes=5)
            
            recent_metrics = []
            pattern = "performance_metrics:*"
            keys = await self.redis_client.keys(pattern)
            
            for key in keys:
                try:
                    metric_data = await self.redis_client.get(key)
                    if metric_data:
                        metric = json.loads(metric_data)
                        metric_time = datetime.fromisoformat(metric['timestamp'])
                        if metric_time >= five_minutes_ago:
                            recent_metrics.append(metric)
                except Exception:
                    continue
            
            # Анализируем недавние метрики
            if recent_metrics:
                response_times = [m['execution_time'] for m in recent_metrics]
                memory_usage = [m['memory_usage'] for m in recent_metrics]
                active_requests = [m['active_requests'] for m in recent_metrics]
                
                stats.update({
                    'recent_avg_response_time': sum(response_times) / len(response_times),
                    'recent_max_response_time': max(response_times),
                    'recent_min_response_time': min(response_times),
                    'recent_avg_memory': sum(memory_usage) / len(memory_usage),
                    'recent_max_active_requests': max(active_requests),
                    'recent_requests_count': len(recent_metrics)
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики: {e}")
            return {}
    
    async def get_db_stats(self) -> Dict[str, Any]:
        """Получить статистику базы данных"""
        if not self.redis_client:
            return {}
        
        try:
            # Получаем метрики БД за последние 5 минут
            current_time = datetime.now()
            five_minutes_ago = current_time - timedelta(minutes=5)
            
            db_metrics = []
            pattern = "db_metrics:*"
            keys = await self.redis_client.keys(pattern)
            
            for key in keys:
                try:
                    metric_data = await self.redis_client.get(key)
                    if metric_data:
                        metric = json.loads(metric_data)
                        metric_time = datetime.fromisoformat(metric['timestamp'])
                        if metric_time >= five_minutes_ago:
                            db_metrics.append(metric)
                except Exception:
                    continue
            
            if db_metrics:
                query_times = [m['execution_time'] for m in db_metrics]
                return {
                    'db_queries_count': len(db_metrics),
                    'db_avg_query_time': sum(query_times) / len(query_times),
                    'db_max_query_time': max(query_times),
                    'db_min_query_time': min(query_times),
                    'db_slow_queries': len([t for t in query_times if t > 0.5])
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики БД: {e}")
            return {}
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Получить системную статистику"""
        try:
            # CPU и память
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Сетевая статистика
            net_io = psutil.net_io_counters()
            
            return {
                'cpu_percent': cpu_percent,
                'memory_total_gb': memory.total / (1024**3),
                'memory_used_gb': memory.used / (1024**3),
                'memory_percent': memory.percent,
                'disk_total_gb': disk.total / (1024**3),
                'disk_used_gb': disk.used / (1024**3),
                'disk_percent': (disk.used / disk.total) * 100,
                'network_bytes_sent': net_io.bytes_sent,
                'network_bytes_recv': net_io.bytes_recv
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения системной статистики: {e}")
            return {}
    
    def format_stats_report(self, perf_stats: Dict, db_stats: Dict, sys_stats: Dict) -> str:
        """Форматировать отчет о производительности"""
        report = []
        report.append("=" * 60)
        report.append(f"📊 ОТЧЕТ О ПРОИЗВОДИТЕЛЬНОСТИ - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        
        # Статистика запросов
        if perf_stats:
            report.append("\n🚀 ПРОИЗВОДИТЕЛЬНОСТЬ БОТА:")
            report.append(f"  • Всего запросов: {perf_stats.get('total_requests', 0)}")
            report.append(f"  • Среднее время ответа: {perf_stats.get('avg_time', 0):.3f}с")
            report.append(f"  • Максимальное время: {perf_stats.get('max_time', 0):.3f}с")
            report.append(f"  • Минимальное время: {perf_stats.get('min_time', 0):.3f}с")
            report.append(f"  • Макс. одновременных: {perf_stats.get('max_concurrent', 0)}")
            
            if 'recent_requests_count' in perf_stats:
                report.append(f"\n📈 ПОСЛЕДНИЕ 5 МИНУТ:")
                report.append(f"  • Запросов: {perf_stats.get('recent_requests_count', 0)}")
                report.append(f"  • Среднее время: {perf_stats.get('recent_avg_response_time', 0):.3f}с")
                report.append(f"  • Макс. время: {perf_stats.get('recent_max_response_time', 0):.3f}с")
                report.append(f"  • Макс. активных: {perf_stats.get('recent_max_active_requests', 0)}")
                report.append(f"  • Средняя память: {perf_stats.get('recent_avg_memory', 0):.1f}MB")
        
        # Статистика БД
        if db_stats:
            report.append(f"\n🗄️ БАЗА ДАННЫХ (последние 5 мин):")
            report.append(f"  • Запросов к БД: {db_stats.get('db_queries_count', 0)}")
            report.append(f"  • Среднее время: {db_stats.get('db_avg_query_time', 0):.3f}с")
            report.append(f"  • Макс. время: {db_stats.get('db_max_query_time', 0):.3f}с")
            report.append(f"  • Медленных запросов: {db_stats.get('db_slow_queries', 0)}")
        
        # Системная статистика
        if sys_stats:
            report.append(f"\n💻 СИСТЕМА:")
            report.append(f"  • CPU: {sys_stats.get('cpu_percent', 0):.1f}%")
            report.append(f"  • Память: {sys_stats.get('memory_used_gb', 0):.1f}GB / {sys_stats.get('memory_total_gb', 0):.1f}GB ({sys_stats.get('memory_percent', 0):.1f}%)")
            report.append(f"  • Диск: {sys_stats.get('disk_used_gb', 0):.1f}GB / {sys_stats.get('disk_total_gb', 0):.1f}GB ({sys_stats.get('disk_percent', 0):.1f}%)")
        
        report.append("=" * 60)
        return "\n".join(report)
    
    async def monitor_loop(self, interval: int = 30):
        """Основной цикл мониторинга"""
        logger.info(f"🔍 Запуск мониторинга с интервалом {interval} секунд")
        self.monitoring = True
        
        while self.monitoring:
            try:
                # Собираем статистику
                perf_stats = await self.get_performance_stats()
                db_stats = await self.get_db_stats()
                sys_stats = self.get_system_stats()
                
                # Выводим отчет
                report = self.format_stats_report(perf_stats, db_stats, sys_stats)
                print(report)
                
                # Проверяем критические показатели
                await self.check_alerts(perf_stats, db_stats, sys_stats)
                
                # Ждем следующий интервал
                await asyncio.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 Остановка мониторинга по запросу пользователя")
                break
            except Exception as e:
                logger.error(f"❌ Ошибка в цикле мониторинга: {e}")
                await asyncio.sleep(5)
    
    async def check_alerts(self, perf_stats: Dict, db_stats: Dict, sys_stats: Dict):
        """Проверка критических показателей"""
        alerts = []
        
        # Проверяем время ответа
        if perf_stats.get('recent_avg_response_time', 0) > 2.0:
            alerts.append("🚨 Высокое время ответа!")
        
        # Проверяем использование памяти
        if sys_stats.get('memory_percent', 0) > 80:
            alerts.append("🚨 Высокое использование памяти!")
        
        # Проверяем CPU
        if sys_stats.get('cpu_percent', 0) > 80:
            alerts.append("🚨 Высокая загрузка CPU!")
        
        # Проверяем медленные запросы к БД
        if db_stats.get('db_slow_queries', 0) > 5:
            alerts.append("🚨 Много медленных запросов к БД!")
        
        if alerts:
            logger.warning("КРИТИЧЕСКИЕ ПОКАЗАТЕЛИ:")
            for alert in alerts:
                logger.warning(f"  {alert}")
    
    def stop_monitoring(self):
        """Остановить мониторинг"""
        self.monitoring = False


async def main():
    """Главная функция"""
    monitor = PerformanceMonitor()
    
    # Подключаемся к Redis
    if not await monitor.connect_redis():
        logger.error("❌ Не удалось подключиться к Redis. Мониторинг недоступен.")
        return
    
    try:
        # Запускаем мониторинг
        await monitor.monitor_loop(interval=30)
    except KeyboardInterrupt:
        logger.info("🛑 Мониторинг остановлен")
    finally:
        if monitor.redis_client:
            await monitor.redis_client.close()


if __name__ == "__main__":
    asyncio.run(main())
