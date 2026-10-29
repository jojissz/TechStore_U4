from decimal import Decimal, ROUND_HALF_UP
from app.specifications import MinimumAmountSpec, MinimumUnitsSpec, VIPCustomerSpec, ActivePromotionSpec

TEN_PERCENT = VIPCustomerSpec() & MinimumAmountSpec(Decimal("500")) & MinimumUnitsSpec(4) & ~ActivePromotionSpec()
FIVE_PERCENT = MinimumAmountSpec(Decimal("5000")) & ~ActivePromotionSpec()

def discount_rate(order):
    if TEN_PERCENT.is_satisfied_by(order):
        return Decimal("0.10")
    if FIVE_PERCENT.is_satisfied_by(order):
        return Decimal("0.05")
    return Decimal("0.00")

def discount_details(order):
    rate = discount_rate(order)
    gross = order.total.amount
    savings = (gross * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return {"order_id": order.id, "subtotal": str(gross.quantize(Decimal('0.01'))),
            "discount_percent": int(rate * 100), "discount_amount": str(savings),
            "total_after_discount": str((gross - savings).quantize(Decimal('0.01')))}

