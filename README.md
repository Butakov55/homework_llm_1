# Генератор тестовых сценариев

## Установка

```bash
# 1. Установить библиотеку requests
pip install requests

# 2. Проверить установленные модели Ollama
ollama list

# 3. Если нет модели qwen2.5, скачать
ollama pull qwen2.5

# Базовый запуск (5 сценариев)
python homework_llm_2.py

# С указанием количества сценариев
python homework_llm_2.py 10

# С указанием модели
python homework_llm_2.py 5 -m qwen2.5

# С указанием выходного файла
python homework_llm_2.py 5 -o my_scenarios.md