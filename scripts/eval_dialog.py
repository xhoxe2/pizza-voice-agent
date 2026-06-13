"""Текстовий end-to-end прогін агента через реальний Realtime-модель.

Проганяє 4 сценарії ТЗ і друкує, які інструменти викликались.
Запуск: python scripts/eval_dialog.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from livekit.agents import AgentSession
from livekit.plugins import openai

from agent import PizzaAgent

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def dump(turn: str, result) -> set[str]:
    called = set()
    print(f"\n=== USER: {turn}")
    for ev in result.events:
        et = getattr(ev, "type", "")
        if et == "function_call":
            item = ev.item
            print(f"  → TOOL CALL: {item.name}({item.arguments})")
            called.add(item.name)
        elif et == "function_call_output":
            out = str(ev.item.output)
            print(f"  ← TOOL OUT : {out[:160]}")
        elif et == "message":
            text = " ".join(c for c in ev.item.content if isinstance(c, str))
            print(f"  AGENT: {text.strip()}")
    return called


async def main() -> None:
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(model="gpt-realtime-mini", voice="coral"),
    )
    async with session:
        await session.start(PizzaAgent())

        all_called: set[str] = set()
        all_called |= dump("Які піци у вас є?", await session.run(user_input="Які піци у вас є?"))
        all_called |= dump(
            "Розкажи детальніше про Пепероні",
            await session.run(user_input="Розкажи детальніше про Пепероні"),
        )
        all_called |= dump(
            "Хочу дві Маргарити. Мене звати Іван, телефон 0991112233, адреса Шевченка 5",
            await session.run(
                user_input="Хочу дві Маргарити. Мене звати Іван, "
                "телефон 0991112233, адреса вулиця Шевченка 5"
            ),
        )
        all_called |= dump(
            "Так, підтверджую",
            await session.run(user_input="Так, усе вірно, підтверджую замовлення"),
        )
        all_called |= dump(
            "Який статус замовлення ORD-101?",
            await session.run(user_input="Перевір статус замовлення ORD-101"),
        )

        expected = {"show_menu", "item_details", "place_order", "order_status"}
        print("\n================ ПІДСУМОК ================")
        print("Викликані інструменти:", sorted(all_called))
        missing = expected - all_called
        if missing:
            print("НЕ ВИКЛИКАНО:", sorted(missing))
            sys.exit(1)
        print("OK — усі 4 інструменти спрацювали в живому діалозі.")


if __name__ == "__main__":
    asyncio.run(main())
