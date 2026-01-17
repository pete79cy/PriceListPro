"""
Unit tests for VAT calculations and order totals.
Tests line-item VAT calculations and order-level totals.
"""
import pytest
from decimal import Decimal
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.money import money, ALLOWED_VAT_RATES


class MockOrderItem:
    """Mock OrderItem for testing VAT calculations without database."""
    
    def __init__(self, price: float, quantity: int, vat_rate: float = 19.0):
        self.price = price
        self.quantity = quantity
        self.vat_rate = vat_rate
    
    @property
    def unit_price_dec(self):
        return money(self.price)
    
    @property
    def quantity_dec(self):
        return Decimal(str(self.quantity))
    
    @property
    def net_total(self):
        return money(self.unit_price_dec * self.quantity_dec)
    
    @property
    def vat_amount(self):
        rate = Decimal(str(self.vat_rate)) / Decimal("100")
        return money(self.net_total * rate)
    
    @property
    def gross_total(self):
        return money(self.net_total + self.vat_amount)


class MockOrder:
    """Mock Order for testing order-level totals."""
    
    def __init__(self, items: list):
        self.items = items
    
    @property
    def subtotal(self):
        return money(sum(item.net_total for item in self.items))
    
    @property
    def vat_amount(self):
        return money(sum(item.vat_amount for item in self.items))
    
    @property
    def total(self):
        return money(self.subtotal + self.vat_amount)


class TestSingleLine19Percent:
    """Test case 1: Single line at 19% VAT."""
    
    def test_single_line_19_percent(self):
        """Unit: 100.00, qty: 1, VAT: 19 -> Net: 100.00, VAT: 19.00, Gross: 119.00"""
        item = MockOrderItem(price=100.00, quantity=1, vat_rate=19)
        
        assert item.net_total == Decimal("100.00")
        assert item.vat_amount == Decimal("19.00")
        assert item.gross_total == Decimal("119.00")


class TestSingleLine5Percent:
    """Test case 2: Single line at 5% VAT."""
    
    def test_single_line_5_percent(self):
        """Unit: 100.00, qty: 1, VAT: 5 -> Net: 100.00, VAT: 5.00, Gross: 105.00"""
        item = MockOrderItem(price=100.00, quantity=1, vat_rate=5)
        
        assert item.net_total == Decimal("100.00")
        assert item.vat_amount == Decimal("5.00")
        assert item.gross_total == Decimal("105.00")


class TestSingleLine0Percent:
    """Test case 3: Single line at 0% VAT."""
    
    def test_single_line_0_percent(self):
        """Unit: 100.00, qty: 1, VAT: 0 -> Net: 100.00, VAT: 0.00, Gross: 100.00"""
        item = MockOrderItem(price=100.00, quantity=1, vat_rate=0)
        
        assert item.net_total == Decimal("100.00")
        assert item.vat_amount == Decimal("0.00")
        assert item.gross_total == Decimal("100.00")


class TestMixedBasket:
    """Test case 4: Mixed basket with 19%, 5%, and 0% VAT lines."""
    
    def test_mixed_basket(self):
        """
        Line1: 9.99 x 3 @ 19%
        Line2: 12.50 x 2 @ 5%
        Line3: 100.00 x 1 @ 0%
        """
        line1 = MockOrderItem(price=9.99, quantity=3, vat_rate=19)
        line2 = MockOrderItem(price=12.50, quantity=2, vat_rate=5)
        line3 = MockOrderItem(price=100.00, quantity=1, vat_rate=0)
        
        order = MockOrder(items=[line1, line2, line3])
        
        # Verify individual line calculations
        # Line1: 9.99 * 3 = 29.97
        assert line1.net_total == Decimal("29.97")
        # Line1 VAT: 29.97 * 0.19 = 5.6943 -> 5.69
        assert line1.vat_amount == Decimal("5.69")
        
        # Line2: 12.50 * 2 = 25.00
        assert line2.net_total == Decimal("25.00")
        # Line2 VAT: 25.00 * 0.05 = 1.25
        assert line2.vat_amount == Decimal("1.25")
        
        # Line3: 100.00 * 1 = 100.00
        assert line3.net_total == Decimal("100.00")
        # Line3 VAT: 100.00 * 0.00 = 0.00
        assert line3.vat_amount == Decimal("0.00")
        
        # Order totals
        expected_subtotal = Decimal("29.97") + Decimal("25.00") + Decimal("100.00")
        expected_vat = Decimal("5.69") + Decimal("1.25") + Decimal("0.00")
        expected_total = expected_subtotal + expected_vat
        
        assert order.subtotal == money(expected_subtotal)
        assert order.vat_amount == money(expected_vat)
        assert order.total == money(expected_total)
        
        # Verify the formula: total = subtotal + vat
        assert order.total == money(order.subtotal + order.vat_amount)


class TestRoundingEdge:
    """Test case 5: Rounding edge case."""
    
    def test_rounding_edge_003_at_19(self):
        """Unit: 0.03 x 1 @ 19% - tests rounding behavior."""
        item = MockOrderItem(price=0.03, quantity=1, vat_rate=19)
        
        # Net: 0.03 * 1 = 0.03
        assert item.net_total == Decimal("0.03")
        
        # VAT: 0.03 * 0.19 = 0.0057 -> rounds to 0.01 (HALF_UP)
        assert item.vat_amount == Decimal("0.01")
        
        # Gross: 0.03 + 0.01 = 0.04
        assert item.gross_total == Decimal("0.04")


class TestQuantityDecimals:
    """Test case 6: Quantity handling (integers only for this system)."""
    
    def test_quantity_integer(self):
        """Quantity should be handled as integer."""
        item = MockOrderItem(price=10.00, quantity=3, vat_rate=19)
        
        assert item.quantity_dec == Decimal("3")
        assert item.net_total == Decimal("30.00")


class TestValidation:
    """Test case 7: Validation rules."""
    
    def test_invalid_vat_rate_not_allowed(self):
        """VAT rates outside {0, 5, 19} are invalid."""
        invalid_rates = [1, 7, 10, 15, 20, 23, 25, -5]
        for rate in invalid_rates:
            assert rate not in ALLOWED_VAT_RATES
    
    def test_valid_vat_rates_allowed(self):
        """Only VAT rates 0, 5, 19 are valid."""
        for rate in [0, 5, 19]:
            assert rate in ALLOWED_VAT_RATES
    
    def test_negative_quantity_calculation(self):
        """Negative quantities produce negative totals (validation should prevent)."""
        item = MockOrderItem(price=100.00, quantity=-1, vat_rate=19)
        # This calculates but should be rejected at form validation
        assert item.net_total == Decimal("-100.00")
    
    def test_negative_price_calculation(self):
        """Negative prices produce negative totals (validation should prevent)."""
        item = MockOrderItem(price=-100.00, quantity=1, vat_rate=19)
        # This calculates but should be rejected at form validation
        assert item.net_total == Decimal("-100.00")


class TestOrderTotalFormula:
    """Test that order totals follow the correct formula."""
    
    def test_order_total_equals_subtotal_plus_vat(self):
        """order.total = order.subtotal + order.vat_amount"""
        items = [
            MockOrderItem(price=50.00, quantity=2, vat_rate=19),
            MockOrderItem(price=75.50, quantity=1, vat_rate=5),
            MockOrderItem(price=200.00, quantity=1, vat_rate=0),
        ]
        order = MockOrder(items=items)
        
        # Verify formula
        calculated_total = money(order.subtotal + order.vat_amount)
        assert order.total == calculated_total
    
    def test_sum_of_line_nets_equals_subtotal(self):
        """order.subtotal = sum(line.net_total)"""
        items = [
            MockOrderItem(price=33.33, quantity=3, vat_rate=19),
            MockOrderItem(price=44.44, quantity=2, vat_rate=5),
        ]
        order = MockOrder(items=items)
        
        sum_of_nets = sum(item.net_total for item in items)
        assert order.subtotal == money(sum_of_nets)
    
    def test_sum_of_line_vats_equals_order_vat(self):
        """order.vat_amount = sum(line.vat_amount)"""
        items = [
            MockOrderItem(price=99.99, quantity=1, vat_rate=19),
            MockOrderItem(price=49.95, quantity=2, vat_rate=5),
        ]
        order = MockOrder(items=items)
        
        sum_of_vats = sum(item.vat_amount for item in items)
        assert order.vat_amount == money(sum_of_vats)
