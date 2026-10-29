from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from datetime import datetime, timezone

class DomainException(Exception): pass
class InvalidOrderData(DomainException): pass
class InvalidOrderTransition(DomainException): pass
class OrderItemLimitExceeded(DomainException): pass

@dataclass(frozen=True)
class DomainEvent:
    name: str
    order_id: str
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "MXN"
    
    def __post_init__(self):
        if not self.amount.is_finite() or self.amount < 0:
            raise InvalidOrderData("El monto especificado no es válido.")
            
    def add(self, other):
        if self.currency != other.currency:
            raise InvalidOrderData("No se pueden combinar montos con monedas distintas.")
        return Money(self.amount + other.amount, self.currency)

@dataclass(frozen=True)
class Customer:
    id: str
    is_vip: bool = False
    active: bool = True

@dataclass(frozen=True)
class OrderItem:
    sku: str
    quantity: int
    unit_price: Money
    
    def __post_init__(self):
        if not self.sku.strip() or self.quantity <= 0:
            raise InvalidOrderData("El artículo o la cantidad especificada no son válidos.")
            
    @property
    def subtotal(self):
        return Money(self.unit_price.amount * self.quantity)

class OrderStatus(str, Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    RETURNED = "RETURNED"

@dataclass
class Order:
    customer: Customer
    id: str
    has_promotion: bool = False
    status: OrderStatus = OrderStatus.DRAFT
    items: list[OrderItem] = field(default_factory=list)
    events: list = field(default_factory=list)
    
    @property
    def units(self):
        return sum(item.quantity for item in self.items)
        
    @property
    def total(self):
        amount = sum((x.subtotal.amount for x in self.items), Decimal("0"))
        return Money(amount)
        
    def add_item(self, item):
        if self.status != OrderStatus.DRAFT:
            raise InvalidOrderTransition("El pedido ya no se encuentra en borrador, por lo que no es posible agregar más artículos.")
        if self.units + item.quantity > 20:
            raise OrderItemLimitExceeded("Has superado el límite permitido de 20 unidades por pedido.")
        if item.unit_price.currency != "MXN":
            raise InvalidOrderData("Solo se aceptan transacciones y precios en moneda nacional (MXN).")
        self.items.append(item)

    def confirm(self):
        if self.status != OrderStatus.DRAFT:
            raise InvalidOrderTransition("Este pedido ya fue confirmado o procesado anteriormente y no se puede volver a confirmar.")
        if not self.items or not self.customer.active:
            raise InvalidOrderData("No se puede confirmar el pedido porque está vacío o el cliente no se encuentra activo.")
        self.status = OrderStatus.CONFIRMED
        self.events.append(DomainEvent("OrderConfirmed", self.id))

    def ship(self, tracking_number: str):
        if self.status != OrderStatus.CONFIRMED:
            raise InvalidOrderTransition("El pedido debe estar previamente confirmado antes de poder realizar su envío.")
        if not tracking_number.strip():
            raise InvalidOrderData("Es necesario proporcionar un número de guía válido para registrar el envío.")
        self.status = OrderStatus.SHIPPED
        self.events.append(DomainEvent("OrderShipped", self.id))

    def cancel(self, reason: str):
        if self.status != OrderStatus.CONFIRMED:
            raise InvalidOrderTransition("El pedido no se puede cancelar en su estado actual.")
        if not reason.strip():
            raise InvalidOrderData("Es obligatorio indicar un motivo válido para la cancelación.")
        self.status = OrderStatus.CANCELLED
        self.events.append(DomainEvent("OrderCancelled", self.id))

    def deliver(self):
        if self.status != OrderStatus.SHIPPED:
            raise InvalidOrderTransition("El pedido debe haber sido enviado previamente para poder marcarlo como entregado.")
        self.status = OrderStatus.DELIVERED
        self.events.append(DomainEvent("OrderDelivered", self.id))

    def return_order(self):
        if self.status != OrderStatus.SHIPPED:
            raise InvalidOrderTransition("El pedido debe encontrarse en tránsito (enviado) para poder procesar su devolución.")
        self.status = OrderStatus.RETURNED
        self.events.append(DomainEvent("OrderReturned", self.id))