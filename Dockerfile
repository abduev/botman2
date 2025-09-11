FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Скопируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# Устанавливаем uv (управление зависимостями)
RUN pip install uv

# Устанавливаем зависимости из lock-файла
RUN uv sync --frozen

# Копируем всё приложение
COPY . .

# Запуск бота
CMD ["uv", "run", "-m", "core.main"]
