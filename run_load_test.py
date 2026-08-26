#!/usr/bin/env python
import sys
import subprocess
import time
import os
import signal
import socket
import atexit

# Пути
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SEED_SCRIPT = os.path.join(PROJECT_ROOT, "tests", "load", "seed_data.py")
LOCUST_FILE = os.path.join(PROJECT_ROOT, "tests", "load", "locustfile.py")

def is_port_open(host, port, timeout=2):
    """Проверяет, открыт ли порт."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def wait_for_server(host="localhost", port=8000, max_attempts=30, delay=1):
    """Ожидает, пока сервер поднимется."""
    print(f"⏳ Ожидание запуска сервера на {host}:{port}...")
    for attempt in range(max_attempts):
        if is_port_open(host, port):
            print("✅ Сервер запущен!")
            return True
        time.sleep(delay)
    print("❌ Сервер не запустился за отведённое время.")
    return False

def main():
    # Проверяем, передан ли аргумент для автоматического прогона
    headless_mode = "--headless" in sys.argv or len(sys.argv) > 1

    print("🚀 Запуск FastAPI сервера с тестовой БД...")
    # Запускаем сервер в фоновом процессе с ENV=test
    env = os.environ.copy()
    env["ENV"] = "test"
    server_proc = subprocess.Popen(
        ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=PROJECT_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
    )
    # Регистрируем остановку сервера при завершении скрипта
    def kill_server():
        print("🛑 Остановка сервера...")
        if sys.platform == "win32":
            server_proc.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            server_proc.terminate()
        server_proc.wait(timeout=5)
    atexit.register(kill_server)

    # Ждём, пока сервер поднимется
    if not wait_for_server():
        print("❌ Не удалось запустить сервер. Проверьте ошибки выше.")
        sys.exit(1)

    print("📦 Заполнение тестовой БД...")
    seed_result = subprocess.run([sys.executable, SEED_SCRIPT], cwd=PROJECT_ROOT)
    if seed_result.returncode != 0:
        print("❌ Ошибка заполнения БД.")
        sys.exit(1)

    print("🏃 Запуск нагрузочного теста Locust...")
    # Формируем команду Locust
    locust_cmd = ["locust", "-f", LOCUST_FILE, "--host=http://localhost:8000"]
    # Если передан хотя бы один аргумент, считаем, что пользователь хочет headless режим
    if headless_mode:
        # Если не указаны --users и др., добавляем значения по умолчанию
        if not any(arg.startswith("--users") for arg in sys.argv):
            locust_cmd.extend(["--users", "100"])
        if not any(arg.startswith("--spawn-rate") for arg in sys.argv):
            locust_cmd.extend(["--spawn-rate", "10"])
        if not any(arg.startswith("--run-time") for arg in sys.argv):
            locust_cmd.extend(["--run-time", "5m"])
        # Передаём все аргументы, кроме первого (имя скрипта)
        locust_cmd.extend(sys.argv[1:])
    else:
        # Интерактивный режим: просто передаём -f и --host
        pass

    # Запускаем Locust в том же процессе (он заблокирует выполнение до завершения)
    try:
        subprocess.run(locust_cmd, cwd=PROJECT_ROOT, check=True)
    except KeyboardInterrupt:
        print("⏹️ Тест прерван пользователем.")
    finally:
        kill_server()

if __name__ == "__main__":
    main()