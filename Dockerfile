# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем ВСЕ файлы из текущей папки проекта в /app
COPY . .

# Устанавливаем зависимости (если есть)
RUN pip install --no-cache-dir -r requirements.txt

# Команда для запуска приложения (замените на свою, например, "python main.py")
CMD ["python", "main.py"]