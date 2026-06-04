import os
import subprocess
import sys
import time


def init_env(scripts_rel_dir):
    env = os.environ.copy()
    root_dir = os.getcwd()
    scripts_dir = os.path.join(root_dir, scripts_rel_dir)
    print(f"--- Добавление в PYTHONPATH ---")
    print(f"Корень: {root_dir}")
    print(f"Папка скриптов: {scripts_dir}")
    env["PYTHONPATH"] = (
        root_dir + os.pathsep + scripts_dir + os.pathsep + env.get("PYTHONPATH", "")
    )
    return env


def run_simulation(scripts_rel_dir, background_scripts, scheduler_script):
    env = init_env(scripts_rel_dir)
    processes = []
    scripts = background_scripts + [scheduler_script]
    print(f"Скрипты задач: {scripts}")
    try:
        for script_name in scripts:
            script = os.path.join(scripts_rel_dir, script_name)
            if not os.path.exists(script):
                print(f"Ошибка: Файл не найден: {script}")
                continue

            print(f"Запуск {script}...")
            # Запускаем через uv run, чтобы использовать venv
            p = subprocess.Popen(["uv", "run", "python3", script], env=env)
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
    scripts_rel_dir = "tasks"
    background_scripts = ["ex1.py"]
    scheduler_script = "ex.py"

    run_simulation(scripts_rel_dir, background_scripts, scheduler_script)
