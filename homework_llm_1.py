from collections import defaultdict

class TestLLM:
    def __init__(self):
        self.ngram_counts: defaultdict[str, defaultdict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.train_data: list[str] = []
    
    def train(self, data: list[str]) -> None:
        """
        Обучает модель на списке предложений.
        Для каждого слова запоминает, какие слова встречались после него.
        """
        self.train_data = data
        self.ngram_counts.clear()  # Очищаем предыдущие данные при новом обучении
        
        for sentence in data:
            # Разбиваем предложение на слова
            words = sentence.split()
            
            # Проходим по всем парам соседних слов
            for i in range(len(words) - 1):
                current_word = words[i]
                next_word = words[i + 1]
                # Увеличиваем счётчик для пары (current_word -> next_word)
                self.ngram_counts[current_word][next_word] += 1
    
    def predict_next_word(self, start_word: str) -> str:
        if start_word not in self.ngram_counts:
            return "Слово не найдено в обучающей выборке"
        
        next_words: defaultdict[str, int] = self.ngram_counts[start_word]
        
        if not next_words:
            return "Нет данных для предсказания"
        
        # Находим самое частотное следующее слово
        most_frequent: str = max(next_words, key=next_words.get)
        
        return most_frequent


# Данные для обучения
data: list[str] = [
    "кот спит на диване",
    "кот ест рыбу",
    "кот играет с мячом",
    "кот спит на окне",
    "кот гуляет по улице",
    "кот ест молоко",
    "кот играет с мышкой",
    "кот спит в коробке",
    "кот смотрит в окно",
    "кот гуляет в парке"
]

# Создаём и обучаем модель
test_llm_model: TestLLM = TestLLM()
test_llm_model.train(data)

# Для тестирования
print("=" * 50)
print("Модель предсказания следующего слова")
print("=" * 50)
print("Введите слово для предсказания (или 'exit' для выхода):")
print()

while True:
    user_input = input("> ").strip().lower()
    
    if user_input == 'exit' or user_input == 'выход':
        print("До свидания!")
        break
    
    if not user_input:
        print("Пожалуйста, введите слово.\n")
        continue
    
    prediction = test_llm_model.predict_next_word(user_input)
    print(f"Предсказанное следующее слово: '{prediction}'\n")