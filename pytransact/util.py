from typing import Any
from decimal import Decimal

def to_satoshi(num: Any) -> Decimal:
    number = Decimal(num)
    try:
        satoshi_accuracy: Decimal = number.quantize(Decimal('0.00000001'), rounding='ROUND_DOWN')
        return satoshi_accuracy
    except:
        return number