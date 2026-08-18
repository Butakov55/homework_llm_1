import argparse
import json
import requests
from datetime import datetime

def generate_scenarios(count, model="qwen2.5"):
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
            'http://localhost:11434/api/generate',
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=300  # Увеличили до 5 минут
        )
        
        data = response.json()
        
        if 'response' in data:
            content = data['response']
        else:
            print(f"⚠️ Неожиданный формат ответа")
            return fallback_scenarios(count)
        
        start = content.find('[')
        end = content.rfind(']') + 1
        
        if start == -1 or end == 0:
            print("⚠️ JSON не найден в ответе, используем резервные сценарии")
            return fallback_scenarios(count)
        
        json_str = content[start:end]
        scenarios = json.loads(json_str)
        
        if not isinstance(scenarios, list):
            return fallback_scenarios(count)
        
        return scenarios
        
    except Exception as e:
        print(f"⚠️ Ошибка: {e}, используем резервные сценарии")
        return fallback_scenarios(count)

def fallback_scenarios(count):
    all_scenarios = [
        {"id": "TC-001", "title": "Успешная регистрация с корректными данными", "type": "Позитивный",
         "precondition": "Форма регистрации открыта", 
         "steps": "1. Ввести имя пользователя 'testuser123'\n2. Ввести пароль 'Test@123456'\n3. Подтвердить пароль\n4. Нажать кнопку 'Зарегистрировать'",
         "expected_result": "Пользователь успешно зарегистрирован, отображается сообщение об успехе", "priority": "High"},
        
        {"id": "TC-002", "title": "Регистрация с пустым именем пользователя", "type": "Негативный",
         "precondition": "Форма регистрации открыта",
         "steps": "1. Оставить поле 'Имя пользователя' пустым\n2. Ввести корректный пароль\n3. Подтвердить пароль\n4. Нажать 'Зарегистрировать'",
         "expected_result": "Ошибка: 'Имя пользователя обязательно для заполнения'", "priority": "High"},
        
        {"id": "TC-003", "title": "Регистрация с несовпадающими паролями", "type": "Негативный",
         "precondition": "Форма регистрации открыта",
         "steps": "1. Ввести имя 'testuser'\n2. Ввести пароль 'Password123'\n3. Ввести подтверждение 'Password124'\n4. Нажать 'Зарегистрировать'",
         "expected_result": "Ошибка: 'Пароли не совпадают'", "priority": "High"},
        
        {"id": "TC-004", "title": "Регистрация с слишком коротким паролем", "type": "Негативный",
         "precondition": "Форма регистрации открыта",
         "steps": "1. Ввести имя 'testuser'\n2. Ввести пароль '123'\n3. Подтвердить пароль '123'\n4. Нажать 'Зарегистрировать'",
         "expected_result": "Ошибка: 'Пароль должен содержать минимум 8 символов'", "priority": "High"},
        
        {"id": "TC-005", "title": "Регистрация с существующим именем пользователя", "type": "Негативный",
         "precondition": "Пользователь 'existing_user' уже существует в системе",
         "steps": "1. Ввести имя 'existing_user'\n2. Ввести корректный пароль\n3. Подтвердить пароль\n4. Нажать 'Зарегистрировать'",
         "expected_result": "Ошибка: 'Пользователь с таким именем уже существует'", "priority": "Medium"},
    ]
    
    return all_scenarios[:count] if count <= len(all_scenarios) else all_scenarios

def save_markdown(scenarios, filename="scenarios.md"):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# Тестовые сценарии для формы регистрации\n\n")
        f.write(f"**Дата генерации:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Всего сценариев:** {len(scenarios)}\n\n")
        f.write("---\n\n")
        
        for s in scenarios:
            f.write(f"## {s['id']}: {s['title']}\n\n")
            f.write(f"**Тип:** {s['type']}\n")
            f.write(f"**Приоритет:** {s.get('priority', 'Medium')}\n\n")
            f.write(f"**Предусловия:**\n\n{s['precondition']}\n\n")
            f.write(f"**Шаги:**\n\n{s['steps']}\n\n")
            f.write(f"**Ожидаемый результат:**\n\n{s['expected_result']}\n\n")
            f.write("---\n\n")
        
        pos = sum(1 for s in scenarios if "позитив" in s['type'].lower())
        neg = len(scenarios) - pos
        
        f.write(f"## Статистика\n\n")
        f.write(f"- **Позитивные сценарии:** {pos}\n")
        f.write(f"- **Негативные сценарии:** {neg}\n")
        f.write(f"- **Всего:** {len(scenarios)}\n")

def main():
    parser = argparse.ArgumentParser(description="Генератор тестовых сценариев")
    parser.add_argument("count", type=int, nargs="?", default=5, help="Количество сценариев")
    parser.add_argument("-m", "--model", default="qwen2.5", help="Модель Ollama")
    parser.add_argument("-o", "--output", default="scenarios.md", help="Выходной файл")
    args = parser.parse_args()
    
    print(f"🤖 Генерация {args.count} тестовых сценариев...")
    print(f"📦 Модель: {args.model}")
    print(f"⏳ Это может занять несколько минут, пожалуйста, подождите...")
    
    try:
        requests.get('http://localhost:11434/api/tags', timeout=2)
        print("✅ Ollama запущен и доступен")
    except:
        print("⚠️ Ollama не доступен, используются резервные сценарии")
    
    scenarios = generate_scenarios(args.count, args.model)
    save_markdown(scenarios, args.output)
    
    pos = sum(1 for s in scenarios if "позитив" in s['type'].lower())
    neg = len(scenarios) - pos
    
    print(f"\n✅ Сценарии сохранены в {args.output}")
    print(f"📊 Статистика: Позитивных: {pos}, Негативных: {neg}, Всего: {len(scenarios)}")

if __name__ == "__main__":
    main()