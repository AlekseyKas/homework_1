# Анализ логов безопасности botsv1

## Описание

Проект для анализа и визуализации подозрительных событий из логов WinEventLog и DNS.

## Данные

- Источник: `bostv1.json`
- Типы логов:
  - **WinEventLog:Security** - 35 записей
  - **DNS** - 3 записи

## Анализ

### WinEventLog

Выявлены подозрительные события по EventID:
- **4703** - Token Rights Adjusted (изменение прав токена) - 12 случаев
- **4624** - Successful Logon (успешный вход в систему) - 3 случая
- **4656** - Object Handle Requested (запрос объекта) - 1 случай

### DNS

Определены потенциально вредоносные домены:
- `ajd92jd9d.com` - случайного вида домен
- `c2.maliciousdomain.com` - C2-команда злоумышленника

## Запуск

```bash
pip install pandas matplotlib seaborn --break-system-packages
python3 analyze_logs.py
```

## Результаты

График Top-10 подозрительных событий сохраняется в файл `suspicious_events.png`.

## Файлы

- `analyze_logs.py` - скрипт анализа
- `suspicious_events.png` - визуализация
- `bostv1.json` - исходные данные
