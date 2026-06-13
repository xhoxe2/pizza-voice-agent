# Голосовий агент для піцерії

Голосовий помічник піцерії на **LiveKit Agents** + **OpenAI Realtime API**.
Веде розмову українською, допомагає обрати страву, оформити та відстежити
замовлення. Меню й замовлення — у `tools.py`, який під'єднано до агента
через function calling.

## Можливості

- меню цілком або за категорією (піци, напої, десерти);
- деталі страви — склад, ціна, наявність;
- оформлення замовлення (позиції, ім'я, телефон, адреса);
- статус замовлення за номером.

## Стек

- `livekit-agents` 1.6 (Worker / `AgentSession`);
- OpenAI Realtime, модель `gpt-realtime-mini` — мовлення-в-мовлення;
- Python 3.10+.

## Архітектурні рішення

- **Speech-to-speech, а не STT→LLM→TTS.** Realtime-модель обробляє голос
  напряму — це найкоротший шлях за затримкою й природніша інтонація. ТЗ
  прямо вимагає Realtime API.
- **Інструменти як методи `Agent`.** Чотири функції з `tools.py` обгорнуто
  методами з `@function_tool`; докстрінги стають описом інструментів для
  моделі — окремої схеми вести не треба.
- **Позиції замовлення — pydantic-модель `OrderLine`** (`id`, `quantity ≥ 1`).
  Дає валідовану JSON-схему для function calling замість «сирого» dict.
- **Захисна межа.** Аргументи приходять від моделі, тож `tools.py` на
  невідомий id повертає `{"success": false}`, а не падає.
- **Конфігурація — лише через `.env`.** Жодних секретів у коді; модель і
  голос теж перевизначаються змінними середовища.

Як це перевірено — див. [TESTING.md](TESTING.md).

## Запуск

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # і заповнити ключі
```

Потрібні ключі:

| Змінна | Звідки |
| --- | --- |
| `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` | LiveKit Cloud → проєкт → Settings → Keys |
| `OPENAI_API_KEY` | OpenAI, з доступом до Realtime API |

Локальна перевірка прямо в терміналі (мікрофон + динаміки, без фронтенду):

```bash
python agent.py console
```

Підключити агента до LiveKit-кімнати (для веб- чи мобільного клієнта):

```bash
python agent.py dev      # розробка з гарячим перезавантаженням
python agent.py start    # продакшн
```

Поговорити через браузер найшвидше в [LiveKit Agents Playground](https://agents-playground.livekit.io)
— підключитись до того ж проєкту.

## Тести

```bash
pip install -r requirements-dev.txt
pytest
```

End-to-end прогін діалогу через реальний Realtime-модель (перевіряє, що
всі чотири інструменти викликаються в розмові; потребує валідного `.env`):

```bash
python scripts/eval_dialog.py
```

## Структура

```
agent.py            # агент, сесія, обгортки інструментів
tools.py            # mock-меню, замовлення та 4 функції
tests/test_tools.py # перевірка функцій і реєстрації інструментів
requirements.txt
.env.example
```
