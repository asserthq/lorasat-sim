from pathlib import Path

# Путь к папке, где лежит текущий файл
current_dir = Path(__file__).resolve().parent
print(f"Скрипт находится в: {current_dir}")

OUTPUT_DIR = current_dir / "output"
