"""Перевірка mock-функцій та того, що агент під'єднує їх як інструменти."""

from __future__ import annotations

import pytest

import tools


@pytest.fixture(autouse=True)
def _isolate_order_state(monkeypatch):
    """Кожен тест працює з власною копією замовлень — без перетікання стану."""
    monkeypatch.setattr(tools, "ORDERS", {k: v for k, v in tools.ORDERS.items()})
    monkeypatch.setattr(tools, "_next_order_id", tools._next_order_id)


def test_get_menu_returns_all_items():
    menu = tools.get_menu()
    assert len(menu) == 10
    assert {item["category"] for item in menu} == {"pizza", "drinks", "desserts"}


def test_get_menu_filters_by_category_alias():
    assert all(item["category"] == "pizza" for item in tools.get_menu("піца"))


def test_item_details_known_and_unknown():
    assert tools.get_item_details("pz1")["name"] == "Маргарита"
    assert tools.get_item_details("nope")["success"] is False


def test_create_order_computes_total():
    result = tools.create_order(
        items=[{"id": "pz1", "quantity": 2}, {"id": "dr1", "quantity": 1}],
        customer_name="Тест",
        phone="+380000000000",
        address="вул. Тестова, 1",
    )
    assert result["success"] is True
    assert result["total"] == 189 * 2 + 49
    assert result["order_id"].startswith("ORD-")


def test_create_order_rejects_unavailable_item():
    result = tools.create_order(
        items=[{"id": "pz4", "quantity": 1}],
        customer_name="Тест",
        phone="+380000000000",
        address="вул. Тестова, 1",
    )
    assert result["success"] is False


def test_order_status_known_and_unknown():
    assert tools.get_order_status("ORD-101")["success"] is True
    assert tools.get_order_status("ORD-999")["success"] is False


def test_agent_exposes_all_four_tools():
    agent = pytest.importorskip("agent")  # requires livekit-agents installed
    tool_names = {t.info.name for t in agent.PizzaAgent().tools}
    assert tool_names == {"show_menu", "item_details", "place_order", "order_status"}
