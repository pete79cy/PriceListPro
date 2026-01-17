"""
Money and VAT calculation utilities for PriceListPro.
This module is designed to be importable without triggering Flask app initialization.
"""
from decimal import Decimal, ROUND_HALF_UP

# Cyprus VAT rates (as percentages)
CYPRUS_VAT_STANDARD = 19  # Standard rate
CYPRUS_VAT_REDUCED = 5    # Reduced rate
CYPRUS_VAT_ZERO = 0       # Zero rate (for exports, etc.)
ALLOWED_VAT_RATES = [CYPRUS_VAT_STANDARD, CYPRUS_VAT_REDUCED, CYPRUS_VAT_ZERO]

# Decimal precision for money calculations
TWOPLACES = Decimal("0.01")


def money(value) -> Decimal:
    """
    Convert a value to a Decimal with 2 decimal places.
    Uses ROUND_HALF_UP for consistent rounding.
    Prevents float precision issues in money calculations.
    
    Args:
        value: The value to convert (int, float, str, Decimal, or None)
        
    Returns:
        Decimal: The value quantized to 2 decimal places
    """
    if value is None:
        return Decimal("0.00")
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def validate_vat_rate(rate) -> bool:
    """
    Check if a VAT rate is valid for Cyprus.
    
    Args:
        rate: The VAT rate to validate (as integer percentage)
        
    Returns:
        bool: True if the rate is valid, False otherwise
    """
    return int(rate) in ALLOWED_VAT_RATES


def calculate_vat(net_amount, vat_rate) -> Decimal:
    """
    Calculate VAT amount from a net amount.
    
    Args:
        net_amount: The net amount (before VAT)
        vat_rate: The VAT rate as a percentage (e.g., 19 for 19%)
        
    Returns:
        Decimal: The VAT amount
    """
    net = money(net_amount)
    rate = Decimal(str(vat_rate)) / Decimal("100")
    return money(net * rate)


def calculate_gross(net_amount, vat_rate) -> Decimal:
    """
    Calculate gross amount (net + VAT) from a net amount.
    
    Args:
        net_amount: The net amount (before VAT)
        vat_rate: The VAT rate as a percentage (e.g., 19 for 19%)
        
    Returns:
        Decimal: The gross amount (net + VAT)
    """
    net = money(net_amount)
    vat = calculate_vat(net, vat_rate)
    return money(net + vat)
