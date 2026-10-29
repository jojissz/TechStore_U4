"""Los 15 escenarios del CSV del docente. Cada test usa fixtures nuevos."""
import pytest
from decimal import Decimal
from cargar_csv import load_fixture
from app.domain import OrderItem, Money, InvalidOrderData, InvalidOrderTransition, OrderItemLimitExceeded
from app.discounts import discount_rate

@pytest.fixture
def orders():
    return load_fixture()

def test_E01(orders): assert discount_rate(orders['O001']) == Decimal('0.10')
def test_E02(orders): assert discount_rate(orders['O002']) == Decimal('0.00')
def test_E03(orders):
    with pytest.raises(InvalidOrderData): orders['O003'].confirm()
    assert orders['O003'].status.value == 'DRAFT' and not orders['O003'].events

def test_E04(orders): assert discount_rate(orders['O005']) == Decimal('0.00')
def test_E05(orders): assert discount_rate(orders['O006']) == Decimal('0.05')
def test_E06(orders):
    with pytest.raises(InvalidOrderData): orders['O007'].confirm()
    assert orders['O007'].status.value == 'DRAFT'

def test_E07(orders):
    order = orders['O008']; order.confirm()
    assert order.units == 20 and order.status.value == 'CONFIRMED' and order.events[-1].name == 'OrderConfirmed'

def test_E08(orders):
    order = orders['O009']
    with pytest.raises(OrderItemLimitExceeded): order.add_item(OrderItem('SKU003', 2, Money(Decimal('120.00'))))
    assert order.units == 19 and not order.events

def test_E09(orders): assert discount_rate(orders['O010']) == Decimal('0.00')
def test_E10(orders): assert discount_rate(orders['O011']) == Decimal('0.00')
def test_E11(orders):
    order = orders['O012']; order.confirm()
    with pytest.raises(InvalidOrderData): order.ship('')
    assert order.status.value == 'CONFIRMED' and [e.name for e in order.events] == ['OrderConfirmed']

def test_E12(orders):
    order = orders['O013']; order.confirm()
    with pytest.raises(InvalidOrderTransition): order.confirm()
    assert order.status.value == 'CONFIRMED' and len(order.events) == 1

def test_E13(orders):
    order = orders['O014']; order.confirm(); order.ship('GUIA-001')
    with pytest.raises(InvalidOrderTransition): order.cancel('cliente')
    assert order.status.value == 'SHIPPED' and [e.name for e in order.events] == ['OrderConfirmed', 'OrderShipped']

def test_E14(orders):
    order = orders['O015']; order.confirm(); order.ship('GUIA-002'); order.return_order()
    assert order.status.value == 'RETURNED' and order.events[-1].name == 'OrderReturned'

def test_E15(orders):
    order = orders['O016']; order.confirm(); order.ship('GUIA-003'); order.deliver()
    assert order.status.value == 'DELIVERED' and order.events[-1].name == 'OrderDelivered'
