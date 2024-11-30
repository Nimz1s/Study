# Використовуємо базовий образ Python
FROM python:3.10-slim

# Встановлюємо робочу директорію в контейнері
WORKDIR /app

# Копіюємо всі файли проекту в контейнер
COPY . /app

# Створюємо директорію Flask для бази даних
RUN mkdir -p Flask

# Встановлюємо залежності
RUN pip install --no-cache-dir -r requirements.txt

# Створюємо базу даних і таблиці під час запуску контейнера
RUN python -c "from models import init_db; init_db()"

# Відкриваємо порт для додатку
EXPOSE 5000

# Команда для запуску додатку
CMD ["python", "app.py"]
