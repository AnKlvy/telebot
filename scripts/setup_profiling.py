"""
Скрипт для установки и настройки инструментов профилирования
"""
import subprocess
import sys
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

def run_command(command: str, description: str = None):
    """Выполнить команду в shell"""
    if description:
        logger.info(f"🔧 {description}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            logger.info(result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Ошибка выполнения команды: {command}")
        logger.error(f"❌ {e.stderr}")
        return False

def install_python_packages():
    """Установка Python пакетов для профилирования"""
    packages = [
        "py-spy",           # Профайлер без изменения кода
        "snakeviz",         # Визуализация cProfile
        "memory-profiler",  # Профилирование памяти
        "psutil",          # Системная информация
        "aiohttp-devtools", # Инструменты для aiohttp
        "line-profiler",   # Построчное профилирование
        "pympler",         # Анализ памяти
        "objgraph",        # Граф объектов
    ]
    
    logger.info("📦 Установка Python пакетов для профилирования...")
    
    for package in packages:
        if run_command(f"pip install {package}", f"Установка {package}"):
            logger.info(f"✅ {package} установлен")
        else:
            logger.warning(f"⚠️ Не удалось установить {package}")

def create_profiling_scripts():
    """Создание скриптов для профилирования"""
    
    # Скрипт для py-spy профилирования
    py_spy_script = """#!/bin/bash
# Скрипт для профилирования с py-spy

PID=$(pgrep -f "python.*main.py")

if [ -z "$PID" ]; then
    echo "❌ Процесс бота не найден"
    exit 1
fi

echo "🔍 Профилирование процесса $PID с py-spy..."

# Создаем папку для результатов
mkdir -p profiling_results

# Профилирование в течение 60 секунд
py-spy record -o profiling_results/profile_$(date +%Y%m%d_%H%M%S).svg -d 60 -p $PID

echo "✅ Профилирование завершено. Результат сохранен в profiling_results/"
"""
    
    # Скрипт для мониторинга памяти
    memory_monitor_script = """#!/bin/bash
# Скрипт для мониторинга памяти

PID=$(pgrep -f "python.*main.py")

if [ -z "$PID" ]; then
    echo "❌ Процесс бота не найден"
    exit 1
fi

echo "🧠 Мониторинг памяти процесса $PID..."

# Создаем папку для результатов
mkdir -p profiling_results

# Мониторинг памяти каждые 5 секунд в течение 5 минут
mprof run --interval 5 --timeout 300 --output profiling_results/memory_$(date +%Y%m%d_%H%M%S).dat python -c "
import time
import psutil
import os

pid = $PID
process = psutil.Process(pid)

print(f'Мониторинг памяти процесса {pid}')
for i in range(60):  # 5 минут
    try:
        memory_info = process.memory_info()
        print(f'RSS: {memory_info.rss / 1024 / 1024:.1f}MB, VMS: {memory_info.vms / 1024 / 1024:.1f}MB')
        time.sleep(5)
    except psutil.NoSuchProcess:
        print('Процесс завершен')
        break
"

echo "✅ Мониторинг памяти завершен"
"""
    
    # Скрипт для cProfile
    cprofile_script = """#!/bin/bash
# Скрипт для профилирования с cProfile

echo "📊 Запуск бота с cProfile..."

# Создаем папку для результатов
mkdir -p profiling_results

# Запускаем бот с профилированием
python -m cProfile -o profiling_results/cprofile_$(date +%Y%m%d_%H%M%S).prof main.py &

PROF_PID=$!
echo "🔍 Профилирование запущено (PID: $PROF_PID)"
echo "⏱️ Дайте боту поработать, затем нажмите Ctrl+C для остановки"

# Ждем сигнал остановки
trap "kill $PROF_PID; echo '✅ Профилирование остановлено'" INT

wait $PROF_PID
"""
    
    scripts = {
        "scripts/profile_with_py_spy.sh": py_spy_script,
        "scripts/monitor_memory.sh": memory_monitor_script,
        "scripts/profile_with_cprofile.sh": cprofile_script
    }
    
    logger.info("📝 Создание скриптов профилирования...")
    
    for script_path, content in scripts.items():
        try:
            Path(script_path).parent.mkdir(exist_ok=True)
            with open(script_path, 'w') as f:
                f.write(content)
            
            # Делаем скрипт исполняемым
            os.chmod(script_path, 0o755)
            logger.info(f"✅ Создан скрипт: {script_path}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания скрипта {script_path}: {e}")

def create_analysis_script():
    """Создание скрипта для анализа результатов"""
    
    analysis_script = """#!/usr/bin/env python3
\"\"\"
Скрипт для анализа результатов профилирования
\"\"\"
import os
import sys
import subprocess
from pathlib import Path

def analyze_cprofile(prof_file):
    \"\"\"Анализ cProfile результатов\"\"\"
    print(f"📊 Анализ cProfile: {prof_file}")
    
    # Запускаем snakeviz для визуализации
    try:
        subprocess.run([sys.executable, "-m", "snakeviz", prof_file], check=True)
    except subprocess.CalledProcessError:
        print("❌ Ошибка запуска snakeviz")
    
    # Выводим топ функций
    try:
        result = subprocess.run([
            sys.executable, "-c", 
            f"import pstats; p = pstats.Stats('{prof_file}'); p.sort_stats('cumulative').print_stats(20)"
        ], capture_output=True, text=True)
        
        print("🔝 Топ 20 функций по времени выполнения:")
        print(result.stdout)
        
    except Exception as e:
        print(f"❌ Ошибка анализа: {e}")

def main():
    profiling_dir = Path("profiling_results")
    
    if not profiling_dir.exists():
        print("❌ Папка profiling_results не найдена")
        return
    
    # Ищем файлы профилирования
    prof_files = list(profiling_dir.glob("*.prof"))
    svg_files = list(profiling_dir.glob("*.svg"))
    dat_files = list(profiling_dir.glob("*.dat"))
    
    print(f"📁 Найдено файлов профилирования:")
    print(f"  • cProfile: {len(prof_files)}")
    print(f"  • py-spy SVG: {len(svg_files)}")
    print(f"  • Memory data: {len(dat_files)}")
    
    if prof_files:
        latest_prof = max(prof_files, key=os.path.getctime)
        analyze_cprofile(latest_prof)
    
    if svg_files:
        latest_svg = max(svg_files, key=os.path.getctime)
        print(f"🔥 Последний flame graph: {latest_svg}")
        print(f"   Откройте в браузере для просмотра")
    
    if dat_files:
        latest_dat = max(dat_files, key=os.path.getctime)
        print(f"🧠 Последние данные памяти: {latest_dat}")
        try:
            subprocess.run([sys.executable, "-m", "mprof", "plot", str(latest_dat)])
        except subprocess.CalledProcessError:
            print("❌ Ошибка построения графика памяти")

if __name__ == "__main__":
    main()
"""
    
    script_path = "scripts/analyze_profiling.py"
    
    try:
        with open(script_path, 'w') as f:
            f.write(analysis_script)
        
        os.chmod(script_path, 0o755)
        logger.info(f"✅ Создан скрипт анализа: {script_path}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания скрипта анализа: {e}")

def create_directories():
    """Создание необходимых директорий"""
    directories = [
        "profiling_results",
        "logs",
        "scripts"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"📁 Создана директория: {directory}")

def main():
    """Главная функция установки"""
    logger.info("🚀 Настройка инструментов профилирования...")
    
    # Создаем директории
    create_directories()
    
    # Устанавливаем пакеты
    install_python_packages()
    
    # Создаем скрипты
    create_profiling_scripts()
    create_analysis_script()
    
    logger.info("✅ Настройка завершена!")
    logger.info("\n📋 Доступные инструменты:")
    logger.info("  • scripts/profile_with_py_spy.sh - Профилирование с py-spy")
    logger.info("  • scripts/monitor_memory.sh - Мониторинг памяти")
    logger.info("  • scripts/profile_with_cprofile.sh - Профилирование с cProfile")
    logger.info("  • scripts/analyze_profiling.py - Анализ результатов")
    logger.info("  • scripts/performance_monitor.py - Мониторинг в реальном времени")
    logger.info("  • scripts/load_test_homework.py - Нагрузочное тестирование")

if __name__ == "__main__":
    main()
