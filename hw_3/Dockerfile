FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы
COPY scripts/ /app/scripts/
COPY prompts/ /app/prompts/
COPY tests/ /app/tests/

# Делаем скрипты исполняемыми
RUN chmod +x /app/scripts/*.py

CMD ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]