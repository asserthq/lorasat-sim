import os
import subprocess
import sys
import time

# Список скриптов для запуска
scripts = [
    "tasks/simulator.py",
    # "tasks/control.py",
    "tasks/plot2D.py",
    "tasks/plot3D.py",
]


def run_simulation():
    processes = []

    # Добавляем корень проекта в PYTHONPATH
    # Это позволит скриптам делать "import db", даже если они в подпапках
    env = os.environ.copy()
    root_dir = os.getcwd()
    src_dir = root_dir + "/src"
    env["PYTHONPATH"] = (
        root_dir + os.pathsep + src_dir + os.pathsep + env.get("PYTHONPATH", "")
    )

    print(f"--- Запуск ADCS симуляции ---")
    print(f"Root: {src_dir}")

    try:
        for script in scripts:
            script_path = os.path.join(src_dir, script)
            if not os.path.exists(script_path):
                print(f"Ошибка: Файл не найден: {script_path}")
                continue

            print(f"Запуск {script}...")
            # Запускаем через uv run, чтобы использовать venv
            p = subprocess.Popen(["uv", "run", "python3", script_path], env=env)
            processes.append(p)
            time.sleep(0.5)

        print("\nСимуляция запущена. Ctrl+C для остановки.")

        while True:
            for p in processes:
                if p.poll() is not None:
                    print(f"\nПроцесс {p.pid} завершился с кодом {p.returncode}")
                    raise KeyboardInterrupt
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nОстановка всех процессов...")
        for p in processes:
            p.terminate()
        print("Готово.")


if __name__ == "__main__":
    run_simulation()
