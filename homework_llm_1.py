import argparse
import json
import requests
from datetime import datetime

def generate_scenarios(count, model="llama3.2"):
    prompt = f"""Сгенерируй {count} тестовых сценариев для формы регистрации.
    Сценарии должны быть как позитивные, так и негативные.
    
    Форма регистрации имеет поля: имя пользователя, пароль, подтверждение пароля, кнопка "Зарегистрировать".
    
    Верни только JSON массив с объектами, содержащими поля:
    id, title, type (Позитивный/Негативный), precondition, steps, expected_result, priority (High/Medium/Low)
    
    Пример:
    [
      {{"id": "TC-001", "title": "Успешная регистрация", "type": "Позитивный", 
        "precondition": "Форма открыта", "steps": "1. Ввести данные\\n2. Нажать кнопку", 
        "expected_result": "Регистрация успешна", "priority": "High"}}
    ]
    """
    
    try:
        response = requests.post(
            'http://localhost:11434/api/chat',
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            },
            timeout=60
        )
        content = response.json()['message']['content']
        start = content.find('[')
        end = content.rfind(']') + 1
        return json.loads(content[start:end])
    except Exception as e:
        print(f"Ошибка при генерации: {e}")
        return fallback_scenarios(count)

def fallback_scenarios(count):
    scenarios = [
        {"id": "TC-001", "title": "Успешная регистрация", "type": "Позитивный",
         "precondition": "Форма открыта", 
         "steps": "1. Ввести имя user123\n2. Ввести пароль Pass123!\n3. Подтвердить пароль\n4. Нажать Зарегистрировать",
         "expected_result": "Пользователь создан", "priority": "High"},
        {"id": "TC-002", "title": "Пустое имя пользователя", "type": "Негативный",
         "precondition": "Форма открыта",
         "steps": "1. Оставить имя пустым\n2. Ввести пароль\n3. Подтвердить\n4. Нажать Зарегистрировать",
         "expected_result": "Ошибка: Имя обязательно", "priority": "High"},
        {"id": "TC-003", "title": "Пароли не совпадают", "type": "Негативный",
         "precondition": "Форма открыта",
         "steps": "1. Ввести имя\n2. Ввести пароль 123\n3. Подтвердить 456\n4. Нажать Зарегистрировать",
         "expected_result": "Ошибка: Пароли не совпадают", "priority": "High"},
        {"id": "TC-004", "title": "Короткий пароль", "type": "Негативный",
         "precondition": "Форма открыта",
         "steps": "1. Ввести имя\n2. Ввести пароль 123\n3. Подтвердить 123\n4. Нажать Зарегистрировать",
         "expected_result": "Ошибка: Пароль минимум 8 символов", "priority": "High"},
        {"id": "TC-005", "title": "Существующий пользователь", "type": "Негативный",
         "precondition": "Пользователь test уже существует",
         "steps": "1. Ввести имя test\n2. Ввести пароль\n3. Подтвердить\n4. Нажать Зарегистрировать",
         "expected_result": "Ошибка: Пользователь уже существует", "priority": "Medium"}
    ]
    return scenarios[:count]

def save_markdown(scenarios, filename="scenarios.md"):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# Тестовые сценарии для формы регистрации\n\n")
        f.write(f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Всего сценариев:** {len(scenarios)}\n\n---\n\n")
        
        for s in scenarios:
            f.write(f"## {s['id']}: {s['title']}\n\n")
            f.write(f"**Тип:** {s['type']}\n")
            f.write(f"**Приоритет:** {s.get('priority', 'Medium')}\n\n")
            f.write(f"**Предусловия:**\n{s['precondition']}\n\n")
            f.write(f"**Шаги:**\n{s['steps']}\n\n")
            f.write(f"**Ожидаемый результат:**\n{s['expected_result']}\n\n---\n\n")
        
        pos = sum(1 for s in scenarios if "позитив" in s['type'].lower())
        neg = len(scenarios) - pos
        f.write(f"## Статистика\n\n")
        f.write(f"- **Позитивные сценарии:** {pos}\n")
        f.write(f"- **Негативные сценарии:** {neg}\n")
        f.write(f"- **Всего:** {len(scenarios)}\n")

def main():
    parser = argparse.ArgumentParser(description="Генератор тестовых сценариев")
    parser.add_argument("count", type=int, nargs="?", default=5, help="Количество сценариев")
    parser.add_argument("-m", "--model", default="llama3.2", help="Модель Ollama")
    parser.add_argument("-o", "--output", default="scenarios.md", help="Выходной файл")
    args = parser.parse_args()
    
    print(f"🤖 Генерация {args.count} тестовых сценариев...")
    print(f"📦 Модель: {args.model}")
    
    # Проверяем доступность Ollama
    try:
        requests.get('http://localhost:11434/api/tags', timeout=2)
        print("✅ Ollama запущен и доступен")
    except:
        print("⚠️ Ollama не доступен, будут использованы резервные сценарии")
    
    scenarios = generate_scenarios(args.count, args.model)
    save_markdown(scenarios, args.output)
    
    pos = sum(1 for s in scenarios if "позитив" in s['type'].lower())
    neg = len(scenarios) - pos
    
    print(f"\n✅ Сценарии сохранены в {args.output}")
    print(f"📊 Статистика: Позитивных: {pos}, Негативных: {neg}, Всего: {len(scenarios)}")

if __name__ == "__main__":
    main()