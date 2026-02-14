#!/usr/bin/env python3
"""
Минимальный PoC (Proof of Concept) для эмуляции уязвимости CVE-2024-6387 (RegreSSHion).
ВНИМАНИЕ: Данный скрипт НЕ активирует реальную уязвимость, а лишь имитирует
взаимодействие с целью демонстрации принципа атаки.
"""

import socket
import time
import sys
import threading

def emulate_exploit(target_host, target_port=22, attempts=50):
    """
    Эмулирует попытку эксплуатации CVE-2024-6387.
    1. Устанавливает соединение с SSH-сервером.
    2. Получает баннер (подпись версии).
    3. Не отправляет credentials, ожидая срабатывания таймера LoginGraceTime.
    4. Имитирует состояние гонки путем многопоточных повторных подключений.
    """
    print(f"[*] Цель: {target_host}:{target_port}")
    print("[*] Эмуляция CVE-2024-6387 (RegreSSHion)...")
    print("[!] Это имитация, реальная эксплуатация не производится.\n")

    # --- Шаг 1: Проверка версии и эмуляция таймаута ---
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((target_host, target_port))

        # Получаем баннер SSH (имитация сбора информации)
        banner = sock.recv(1024).decode().strip()
        print(f"[+] Баннер сервера: {banner}")

        # Имитация ожидания срабатывания LoginGraceTime (не отправляем аутентификацию)
        print("[*] Имитация бездействия клиента (ожидание LoginGraceTime)...")
        time.sleep(5)  # В реальности таймаут составляет 120с, здесь сокращено для демо
        sock.close()

    except socket.timeout:
        print("[-] Таймаут соединения.")
        return False
    except Exception as e:
        print(f"[-] Ошибка подключения: {e}")
        return False

    # --- Шаг 2: Имитация многопоточных попыток (Race Condition) ---
    print("\n[*] Эмуляция состояния гонки (Race Condition) через множественные подключения...")

    def thread_worker(thread_id):
        """Имитация быстрого подключения/отключения для создания нагрузки."""
        try:
            # Быстрое подключение и отправка мусора
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((target_host, target_port))
            s.send(b"AAAAAAA\n")  # Мусорные данные вместо корректного рукопожатия
            s.close()
            print(f"    [Поток-{thread_id}] Запрос отправлен.")
        except:
            pass  # Игнорируем ошибки в имитации

    threads = []
    for i in range(min(attempts, 20)):  # Ограничиваем до 20 потоков для наглядности
        t = threading.Thread(target=thread_worker, args=(i,))
        t.start()
        threads.append(t)
        time.sleep(0.05)  # Небольшая задержка между запуском потоков

    for t in threads:
        t.join()

    print("\n[!] Имитация атаки завершена.")
    print("[+] Потенциально уязвимая цель: В реальных условиях могла бы быть предпринята попытка RCE.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python3 CVE-2024-6387_poc.py <IP-адрес> [порт]")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 22
    emulate_exploit(host, port)