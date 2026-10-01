# RAG-ассистент по документации web-сервера (Ollama)

Локальная RAG-система на Python 3, которая отвечает на вопросы
по инструкции управления web-сервером, используя локальные модели Ollama.

## Как это работает

1. Документация хранится в скрипте (`DOCUMENT`) — это локальный датасет.
2. Датасет разбивается на чанки (по предложениям).
3. Для чанков и запроса считаются эмбеддинги через модель Ollama
   `nomic-embed-text`.
4. LLM генерирует ответ **строго по контексту**.

## Требования

- Установленный [Ollama](https://ollama.com/download)

## Установка

### 1. Установите Ollama

Скачайте и установите с https://ollama.com/download

Запустите сервер:

```bash
ollama serve
```

### 2. Загрузите модели

```bash
ollama pull nomic-embed-text
ollama pull llama3.2
```


### 3. Установите зависимости Python

```bash
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install requests
```

## Запуск

```bash
python rag_server.py
```

## Настройка

Все параметры — в начале `rag_server.py`:

| Параметр      | Назначение                          |
|---------------|-------------------------------------|
| `OLLAMA_HOST` | Адрес Ollama (по умолчанию `:11434`)|
| `EMBED_MODEL` | Модель эмбеддингов                  |
| `LLM_MODEL`   | Генеративная модель                 |
| `TOP_K`       | Сколько чанков подавать в контекст  |
