#!/usr/bin/env python3
"""
RAG-генерация ответов по документации управления web-сервером
с использованием локальной модели Ollama.

Логика:
1. Локальный датасет (документация) разбивается на чанки по строкам.
2. Для запроса пользователя считается косинусная близость эмбеддингов
   (модель эмбеддингов Ollama, например `nomic-embed-text`).
   Дополнительно добавляется бонус за лексическое совпадение слов
   (гибридный поиск) — это критично для маленькой базы.
3. Топ-K релевантных чанков подаются в промпт-контекст.
4. Генерация ответа выполняется локальной LLM через Ollama.
"""

import math
from typing import List, Tuple

import requests

# ------------------------- Конфигурация -------------------------
OLLAMA_HOST = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"   # ollama pull nomic-embed-text
LLM_MODEL = "qwen2.5"              # ollama pull qwen2.5  (или llama3.2, mistral и т.п.)
TOP_K = 2

# ------------------------- Локальный датасет (документация) -------------------------
DOCUMENT = """
Для запуска сервера выполните команду: python web_server.py --port 8080.

Если порт занят, используйте --port 9000.

Логирование включается флагом --log-level <log level>.

Остановить сервер можно командой: kill <pid>.

Где pid - ID запущенного процесса web-сервера, log_level - уровень логирования.
""".strip()


def split_into_chunks(text: str) -> List[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


# ------------------------- Ollama API -------------------------
def ollama_embeddings(texts: List[str], model: str = EMBED_MODEL) -> List[List[float]]:
    """Получение эмбеддингов через /api/embeddings (по одному запросу)."""
    vectors = []
    for t in texts:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/embeddings",
            json={"model": model, "prompt": t},
            timeout=120,
        )
        resp.raise_for_status()
        vectors.append(resp.json()["embedding"])
    return vectors


def ollama_generate(prompt: str, model: str = LLM_MODEL) -> str:
    """Генерация ответа через /api/generate (без стриминга)."""
    resp = requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.0},
        },
        timeout=300,
    )
    resp.raise_for_status()
    return resp.json()["response"].strip()


# ------------------------- Векторный поиск -------------------------
def cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb + 1e-12)


def lexical_hits(query_words: List[str], chunk_text: str) -> int:
    """Грубый стемминг: считаем совпадения по первым 5 символам слова.

    «запустить» -> «запус» совпадёт с «запуска»
    «сервер»    -> «серве» совпадёт с «сервера»
    """
    chunk_words = (
        chunk_text.lower()
        .replace(".", " ")
        .replace(",", " ")
        .replace(":", " ")
        .split()
    )
    hits = 0
    for qw in query_words:
        stem = qw[:5]
        if any(cw.startswith(stem) for cw in chunk_words):
            hits += 1
    return hits


class Retriever:
    def __init__(self, chunks: List[str]):
        self.chunks = chunks
        self.chunk_vectors = ollama_embeddings(chunks)

    def retrieve(self, query: str, k: int = TOP_K) -> List[Tuple[str, float]]:
        q_vec = ollama_embeddings([query])[0]
        q_words = [
            w for w in query.lower().replace("?", "").replace(",", "").split()
            if len(w) >= 4
        ]

        scored: List[Tuple[str, float]] = []
        for chunk, vec in zip(self.chunks, self.chunk_vectors):
            sim = cosine_similarity(q_vec, vec)
            bonus = 0.5 * lexical_hits(q_words, chunk)
            scored.append((chunk, sim + bonus))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]


# ------------------------- RAG -------------------------
PROMPT_TEMPLATE = """Ты — ассистент техподдержки. Отвечай ТОЛЬКО на основе контекста ниже.
Категорически запрещено использовать знания вне контекста.
Если в контексте есть команда — процитируй её ДОСЛОВНО, не меняя ни одного символа.
Если ответа нет в контексте — ответь: "В документации нет информации по этому вопросу."

Контекст:
{context}

Вопрос: {question}

Дословный ответ из контекста:"""


def build_prompt(question: str, retrieved: List[Tuple[str, float]]) -> str:
    context = "\n".join(f"- {c}" for c, _ in retrieved)
    return PROMPT_TEMPLATE.format(context=context, question=question)


def answer(question: str, retriever: Retriever, debug: bool = True) -> str:
    retrieved = retriever.retrieve(question, TOP_K)
    if debug:
        print("\n--- DEBUG: топ чанков ---")
        for c, s in retrieved:
            print(f"[{s:.3f}] {c}")
        print("-------------------------\n")
    prompt = build_prompt(question, retrieved)
    return ollama_generate(prompt)


# ------------------------- CLI -------------------------
def main():
    print("Инициализация RAG (индексация документации)...")
    chunks = split_into_chunks(DOCUMENT)

    print("\n=== ЧАНКИ В ИНДЕКСЕ ===")
    for i, c in enumerate(chunks):
        print(f"{i}: [{c}]")
    print("=======================\n")

    retriever = Retriever(chunks)
    print(f"Готово. Чанков в индексе: {len(chunks)}")
    print("Введите вопрос (или 'exit' для выхода).\n")

    while True:
        try:
            question = input("Вы: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit", "выход"}:
            break

        try:
            reply = answer(question, retriever)
        except requests.exceptions.ConnectionError:
            print("Ошибка: Ollama недоступна. Запустите `ollama serve`.\n")
            continue
        except Exception as e:
            print(f"Ошибка: {e}\n")
            continue

        print(f"Ассистент: {reply}\n")


if __name__ == "__main__":
    main()