from decimal import Decimal

class Specification:
    def is_satisfied_by(self, order) -> bool:
        raise NotImplementedError
    
    def __and__(self, other):
        return AndSpec(self, other)
    
    def __or__(self, other):
        return OrSpec(self, other)
    
    def __invert__(self):
        return NotSpec(self)

class AndSpec(Specification):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def is_satisfied_by(self, order) -> bool:
        return self.left.is_satisfied_by(order) and self.right.is_satisfied_by(order)

class OrSpec(Specification):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def is_satisfied_by(self, order) -> bool:
        return self.left.is_satisfied_by(order) or self.right.is_satisfied_by(order)

class NotSpec(Specification):
    def __init__(self, spec):
        self.spec = spec
    
    def is_satisfied_by(self, order) -> bool:
        return not self.spec.is_satisfied_by(order)

# Especificaciones concretas de negocio
class MinimumAmountSpec(Specification):
    def __init__(self, threshold: Decimal):
        self.threshold = threshold
    
    def is_satisfied_by(self, order) -> bool:
        return order.total.amount > self.threshold

class VIPCustomerSpec(Specification):
    def is_satisfied_by(self, order) -> bool:
        return order.customer.is_vip

class MinimumUnitsSpec(Specification):
    def __init__(self, min_units: int):
        self.min_units = min_units
    
    def is_satisfied_by(self, order) -> bool:
        return order.units >= self.min_units

class ActivePromotionSpec(Specification):
    def is_satisfied_by(self, order) -> bool:
        return order.has_promotion