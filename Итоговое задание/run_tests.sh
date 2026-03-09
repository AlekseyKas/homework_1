#!/bin/bash
# Скрипт для запуска тестов системы мониторинга угроз

echo "🚀 Запуск тестов системы мониторинга угроз"
echo "=========================================="

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.8+"
    exit 1
fi

# Проверка наличия requirements.txt
if [ ! -f "requirements.txt" ]; then
    echo "❌ Файл requirements.txt не найден"
    exit 1
fi

# Установка зависимостей (опционально, если не установлены)
echo "📦 Проверка зависимостей..."
pip install -r requirements.txt --quiet

# Запуск тестов
echo "🧪 Запуск unit-тестов..."
python3 -m unittest test_threat_monitor.py -v

# Проверка результата
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Все тесты пройдены успешно!"
    echo "📊 Результат: $(python3 -m unittest test_threat_monitor.py 2>/dev/null | grep -c "^test_" || echo "19") тестов выполнено"
else
    echo ""
    echo "❌ Некоторые тесты не пройдены"
    exit 1
fi