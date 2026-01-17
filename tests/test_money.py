"""
Unit tests for the money() helper function.
Tests Decimal rounding behavior with ROUND_HALF_UP to 2 decimal places.
"""
import pytest
from decimal import Decimal
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.money import money, TWOPLACES, ALLOWED_VAT_RATES, CYPRUS_VAT_STANDARD, CYPRUS_VAT_REDUCED, CYPRUS_VAT_ZERO


class TestMoneyHelper:
    """Test cases for the money() helper function."""
    
    def test_money_returns_decimal(self):
        """money() should always return a Decimal."""
        result = money(100)
        assert isinstance(result, Decimal)
    
    def test_money_none_returns_zero(self):
        """money(None) should return Decimal('0.00')."""
        result = money(None)
        assert result == Decimal("0.00")
    
    def test_money_integer_input(self):
        """money() should handle integer input."""
        result = money(100)
        assert result == Decimal("100.00")
    
    def test_money_float_input(self):
        """money() should handle float input via string conversion."""
        result = money(9.99)
        assert result == Decimal("9.99")
    
    def test_money_string_input(self):
        """money() should handle string input."""
        result = money("12.50")
        assert result == Decimal("12.50")
    
    def test_money_decimal_input(self):
        """money() should handle Decimal input."""
        result = money(Decimal("123.456"))
        assert result == Decimal("123.46")  # Rounded
    
    def test_money_round_half_up_at_5(self):
        """ROUND_HALF_UP: .005 should round up to .01."""
        result = money(Decimal("1.005"))
        assert result == Decimal("1.01")
    
    def test_money_round_half_up_below_5(self):
        """ROUND_HALF_UP: .004 should round down to .00."""
        result = money(Decimal("1.004"))
        assert result == Decimal("1.00")
    
    def test_money_round_half_up_above_5(self):
        """ROUND_HALF_UP: .006 should round up to .01."""
        result = money(Decimal("1.006"))
        assert result == Decimal("1.01")
    
    def test_money_very_small_value(self):
        """Test rounding of very small value 0.03 (edge case from spec)."""
        result = money(Decimal("0.03"))
        assert result == Decimal("0.03")
    
    def test_money_vat_calculation_edge(self):
        """Test VAT calculation edge case: 0.03 * 19% = 0.0057 -> 0.01."""
        unit_price = money(Decimal("0.03"))
        vat_rate = Decimal("19") / Decimal("100")
        vat_amount = money(unit_price * vat_rate)
        assert vat_amount == Decimal("0.01")  # 0.0057 rounds up to 0.01
    
    def test_money_two_decimal_places(self):
        """money() should always return exactly 2 decimal places."""
        result = money(Decimal("100"))
        assert str(result) == "100.00"
        
        result2 = money(Decimal("1.1"))
        assert str(result2) == "1.10"


class TestVATRates:
    """Test cases for Cyprus VAT rate constants."""
    
    def test_standard_vat_rate(self):
        """Standard VAT rate should be 19."""
        assert CYPRUS_VAT_STANDARD == 19
    
    def test_reduced_vat_rate(self):
        """Reduced VAT rate should be 5."""
        assert CYPRUS_VAT_REDUCED == 5
    
    def test_zero_vat_rate(self):
        """Zero VAT rate should be 0."""
        assert CYPRUS_VAT_ZERO == 0
    
    def test_allowed_vat_rates(self):
        """ALLOWED_VAT_RATES should contain exactly 19, 5, and 0."""
        assert set(ALLOWED_VAT_RATES) == {19, 5, 0}
    
    def test_invalid_vat_rate_not_allowed(self):
        """VAT rate 23 should not be in allowed rates."""
        assert 23 not in ALLOWED_VAT_RATES
