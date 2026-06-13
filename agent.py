from __future__ import annotations

import logging

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    RunContext,
    cli,
    function_tool,
)
from livekit.plugins import openai
from pydantic import BaseModel, Field

import tools

load_dotenv()

logger = logging.getLogger("pizza-agent")

INSTRUCTIONS = """
Ти — Марта, голосовий помічник піцерії «Везувіо». Спілкуєшся з клієнтом
голосом по телефону, українською мовою, тепло й по-людськи.

Як говорити:
- Коротко, одна-дві фрази за раз. Це голос, тому ніякого markdown,
  списків, зірочок, дужок чи емодзі — тільки жива розмовна мова.
- Ціни називай словами: «сто вісімдесят дев'ять гривень».
- Внутрішні коди позицій (pz1, dr2) вголос не озвучуй.

Що вмієш:
- Показати меню чи окрему категорію — піци, напої, десерти.
- Розповісти про конкретну страву: склад, ціну, наявність.
- Оформити замовлення та перевірити його статус за номером.

Чого триматися:
- Назви, ціни й наявність бери лише з інструментів, нічого не вигадуй.
- Якщо страва недоступна — чесно скажи й запропонуй схоже.
- Перед оформленням збери ім'я, телефон і адресу доставки, повтори
  замовлення вголос і дочекайся підтвердження, лише тоді створюй заказ.
- Назвав номер замовлення — проговори його як «о-эр-де сто один».
""".strip()


class OrderLine(BaseModel):
    """Одна позиція в замовленні."""

    id: str = Field(description="Код позиції меню, наприклад 'pz1'")
    quantity: int = Field(default=1, ge=1, description="Кількість порцій")


class PizzaAgent(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=INSTRUCTIONS)

    @function_tool
    async def show_menu(self, ctx: RunContext, category: str | None = None) -> list[dict]:
        """Показати меню або одну категорію.

        Args:
            category: 'pizza', 'drinks' або 'desserts'. Пропусти, щоб
                показати все меню.
        """
        logger.info("show_menu", extra={"category": category})
        return tools.get_menu(category)

    @function_tool
    async def item_details(self, ctx: RunContext, item_id: str) -> dict:
        """Деталі страви: склад, ціна, розмір, наявність.

        Args:
            item_id: Код позиції, наприклад 'pz1'.
        """
        logger.info("item_details", extra={"item_id": item_id})
        return tools.get_item_details(item_id)

    @function_tool
    async def place_order(
        self,
        ctx: RunContext,
        items: list[OrderLine],
        customer_name: str,
        phone: str,
        address: str,
    ) -> dict:
        """Оформити замовлення. Викликати тільки після підтвердження клієнта.

        Args:
            items: Перелік позицій із кодами та кількістю.
            customer_name: Ім'я клієнта.
            phone: Контактний телефон.
            address: Адреса доставки.
        """
        logger.info("place_order", extra={"customer": customer_name, "items": len(items)})
        return tools.create_order(
            items=[line.model_dump() for line in items],
            customer_name=customer_name,
            phone=phone,
            address=address,
        )

    @function_tool
    async def order_status(self, ctx: RunContext, order_id: str) -> dict:
        """Статус замовлення за номером.

        Args:
            order_id: Номер замовлення, наприклад 'ORD-101'.
        """
        logger.info("order_status", extra={"order_id": order_id})
        return tools.get_order_status(order_id)


server = AgentServer()


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    await ctx.connect()

    session = AgentSession(
        llm=openai.realtime.RealtimeModel(model="gpt-realtime-mini", voice="coral"),
    )

    await session.start(agent=PizzaAgent(), room=ctx.room)
    await session.generate_reply(
        instructions="Привітайся, відрекомендуйся як Марта з піцерії «Везувіо» "
        "і коротко спитай, чим допомогти.",
    )


if __name__ == "__main__":
    cli.run_app(server)
