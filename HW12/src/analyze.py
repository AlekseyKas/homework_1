import pyshark
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
from datetime import datetime
import os

# --- Настройки ---
PCAP_FILE = '../data/dhcp.pcapng'  # Путь к файлу дампа (относительно src/)
OUTPUT_DIR = '../output'

# Создаем папку для результатов, если её нет
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- 1. Загрузка данных и извлечение артефактов ---
print(f"[*] Анализ файла: {PCAP_FILE}")
print("[*] Чтение дампа. Это может занять некоторое время...")

# Читаем файл .pcapng. Используем только несколько первых пакетов для теста,
# но в реальности уберите параметр 'only_summaries' и 'packet_count',
# если хотите проанализировать весь файл.
# ВАЖНО: Для полного анализа большого файла уберите packet_count.
try:
    # Используем only_summaries=True для скорости, но мы потеряем детали по DNS.
    # Для этого задания лучше читать полностью, но с ограничением на количество пакетов.
    cap = pyshark.FileCapture(PCAP_FILE, use_json=True, include_raw=False)
    # Если файл очень большой, можно ограничить количество пакетов для теста:
    # cap = pyshark.FileCapture(PCAP_FILE, use_json=True, include_raw=False, only_summaries=False)
except FileNotFoundError:
    print(f"[!] Ошибка: Файл {PCAP_FILE} не найден. Поместите дамп в папку 'data'.")
    exit()
except Exception as e:
    print(f"[!] Ошибка при открытии файла: {e}")
    exit()

# Структуры для хранения данных
dns_records = []        # Список словарей для DNS-запросов и ответов
ip_connections = []     # Список словарей для IP-адресов
dns_over_time = defaultdict(int) # Словарь для подсчета DNS-запросов по секундам

packet_count = 0
print("[*] Обработка пакетов...")

# Проходим по каждому пакету
for pkt in cap:
    packet_count += 1
    if packet_count % 1000 == 0:
        print(f"   Обработано {packet_count} пакетов...")

    # --- Извлечение IP-адресов ---
    if hasattr(pkt, 'ip'):
        src_ip = pkt.ip.src
        dst_ip = pkt.ip.dst
        ip_connections.append({
            'src_ip': src_ip,
            'dst_ip': dst_ip,
            'protocol': pkt.transport_layer if hasattr(pkt, 'transport_layer') else 'N/A',
            'time': pkt.sniff_time  # Время захвата пакета
        })

        # --- Извлечение DNS-запросов ---
        if hasattr(pkt, 'dns'):
            # Проверяем, что это запрос (QR == 0)
            if pkt.dns.qry_name and hasattr(pkt.dns, 'qr') and pkt.dns.qr == '0':
                query_name = pkt.dns.qry_name
                query_time = pkt.sniff_time

                # Для временного ряда округлим время до секунды
                time_key = query_time.replace(microsecond=0)
                dns_over_time[time_key] += 1

                # Ищем ответ на этот запрос в этом же пакете (бывает в дампах редко)
                # или просто сохраняем факт запроса.
                # Более сложный анализ потребовал бы сопоставления транзакций (ID).
                # Для простоты сохраним, что запрос был, и посмотрим, есть ли в пакете ответ.
                response_ips = []
                if hasattr(pkt.dns, 'a'):
                    # В ответе могут быть несколько A-записей
                    for answer in pkt.dns.a.all_fields:
                        response_ips.append(answer)

                dns_records.append({
                    'timestamp': query_time,
                    'query': query_name,
                    'response_ips': ', '.join(response_ips) if response_ips else 'No answer in this packet',
                    'src_ip': src_ip,
                    'dst_ip': dst_ip
                })

cap.close()
print(f"[+] Обработка завершена. Всего пакетов: {packet_count}")

# --- 2. Сохранение логов в CSV ---
print("[*] Сохранение результатов в CSV...")

# Сохраняем DNS записи
if dns_records:
    df_dns = pd.DataFrame(dns_records)
    dns_csv_path = os.path.join(OUTPUT_DIR, 'dns_queries.csv')
    df_dns.to_csv(dns_csv_path, index=False)
    print(f"   [+] DNS-запросы сохранены: {dns_csv_path}")
else:
    print("   [!] DNS-запросы не найдены.")
    # Создадим пустой датафрейм для избежания ошибок
    df_dns = pd.DataFrame(columns=['timestamp', 'query', 'response_ips', 'src_ip', 'dst_ip'])


# Сохраняем IP-соединения (выборочно, первые 5000, чтобы файл не был огромным)
if ip_connections:
    # Для больших дампов сохраним только первые 5000 строк для примера
    df_ip = pd.DataFrame(ip_connections[:5000])
    ip_csv_path = os.path.join(OUTPUT_DIR, 'ip_addresses.csv')
    df_ip.to_csv(ip_csv_path, index=False)
    print(f"   [+] Информация об IP-соединениях (первые 5000) сохранена: {ip_csv_path}")
else:
    print("   [!] IP-пакеты не найдены.")


# --- 3. Визуализация ---
print("[*] Создание визуализации...")

if dns_over_time:
    # Преобразуем наш словарь в DataFrame для удобства
    df_timeline = pd.DataFrame(list(dns_over_time.items()), columns=['Time', 'DNS_Count'])
    df_timeline.sort_values('Time', inplace=True)

    # Строим график
    plt.figure(figsize=(12, 6))
    sns.set_style("darkgrid")
    plt.plot(df_timeline['Time'], df_timeline['DNS_Count'], marker='o', linestyle='-', markersize=4)
    plt.title('Количество DNS-запросов во времени', fontsize=16)
    plt.xlabel('Время', fontsize=12)
    plt.ylabel('Количество запросов', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Сохраняем график
    plot_path = os.path.join(OUTPUT_DIR, 'dns_timeline.png')
    plt.savefig(plot_path, dpi=150)
    print(f"   [+] График DNS-запросов сохранен: {plot_path}")
    # Если вы в IDE, можете показать график:
    # plt.show()
    plt.close()
else:
    print("   [!] Недостаточно данных для построения графика DNS.")

print("[+] Анализ завершен. Все результаты сохранены в папке 'output'.")

# Вывод небольшой статистики на экран
print("\n--- Краткая статистика ---")
print(f"Всего DNS-запросов: {len(dns_records)}")
print(f"Уникальных DNS-имен: {df_dns['query'].nunique() if not df_dns.empty else 0}")
print(f"Всего IP-пакетов (уникальных пар src-dst) в выборке: {df_ip['src_ip'].nunique() if 'df_ip' in locals() and not df_ip.empty else 0}")
print("--------------------------\n")
