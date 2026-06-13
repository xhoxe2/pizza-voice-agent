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

## Структура

```
agent.py            # агент, сесія, обгортки інструментів
tools.py            # mock-меню, замовлення та 4 функції
tests/test_tools.py # перевірка функцій і реєстрації інструментів
requirements.txt
.env.example
```
