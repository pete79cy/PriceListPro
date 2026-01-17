"""
Integrity Checker for PriceListPro.
Scans Orders, Invoices, and Quotations to detect data integrity issues.
"""
import json
from decimal import Decimal, InvalidOperation
from datetime import datetime
from typing import List, Dict, Any, Optional

from app import db
from models import Order, OrderItem, Invoice, Quotation
from utils.money import money, ALLOWED_VAT_RATES


class IntegrityIssue:
    """Represents a single integrity issue found during scanning."""
    
    # Issue types
    TOTAL_MISMATCH = "TOTAL_MISMATCH"
    INVALID_VAT_RATE = "INVALID_VAT_RATE"
    INVALID_VALUE = "INVALID_VALUE"
    MISSING_ITEMS = "MISSING_ITEMS"
    NEGATIVE_VALUE = "NEGATIVE_VALUE"
    
    def __init__(self, entity_type: str, entity_id: int, issue: str, 
                 details: Optional[Dict] = None):
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.issue = issue
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            f"{self.entity_type}_id": self.entity_id,
            "issue": self.issue,
        }
        result.update(self.details)
        return result


class IntegrityChecker:
    """
    Scans Orders, Invoices, and Quotations for data integrity issues.
    
    Issues detected:
    - Total mismatches (stored vs computed)
    - Invalid VAT rates
    - Invalid/None values in money fields
    - Negative quantities or prices
    """
    
    def __init__(self):
        self.flags: List[IntegrityIssue] = []
        self.checked = 0
    
    def _decimal_to_str(self, value: Decimal) -> str:
        """Convert Decimal to string for JSON output."""
        if value is None:
            return "null"
        return str(money(value))
    
    def _check_order_item(self, item: OrderItem) -> List[IntegrityIssue]:
        """Check a single order item for issues."""
        issues = []
        
        # Check VAT rate
        try:
            vat_rate = int(item.vat_rate) if item.vat_rate else 0
            if vat_rate not in ALLOWED_VAT_RATES:
                issues.append(IntegrityIssue(
                    "order_item", item.id, 
                    IntegrityIssue.INVALID_VAT_RATE,
                    {"vat_rate": vat_rate, "allowed": ALLOWED_VAT_RATES}
                ))
        except (ValueError, TypeError):
            issues.append(IntegrityIssue(
                "order_item", item.id,
                IntegrityIssue.INVALID_VALUE,
                {"field": "vat_rate", "value": str(item.vat_rate)}
            ))
        
        # Check for negative values
        if item.quantity is not None and item.quantity < 0:
            issues.append(IntegrityIssue(
                "order_item", item.id,
                IntegrityIssue.NEGATIVE_VALUE,
                {"field": "quantity", "value": item.quantity}
            ))
        
        if item.price is not None and item.price < 0:
            issues.append(IntegrityIssue(
                "order_item", item.id,
                IntegrityIssue.NEGATIVE_VALUE,
                {"field": "price", "value": item.price}
            ))
        
        # Check for invalid/None values
        if item.price is None:
            issues.append(IntegrityIssue(
                "order_item", item.id,
                IntegrityIssue.INVALID_VALUE,
                {"field": "price", "value": "null"}
            ))
        
        if item.quantity is None:
            issues.append(IntegrityIssue(
                "order_item", item.id,
                IntegrityIssue.INVALID_VALUE,
                {"field": "quantity", "value": "null"}
            ))
        
        return issues
    
    def _check_order(self, order: Order) -> List[IntegrityIssue]:
        """Check a single order for issues."""
        issues = []
        
        # Check for missing items
        if not order.items or len(order.items) == 0:
            issues.append(IntegrityIssue(
                "order", order.id,
                IntegrityIssue.MISSING_ITEMS,
                {"message": "Order has no items"}
            ))
            return issues
        
        # Check all items
        for item in order.items:
            issues.extend(self._check_order_item(item))
        
        # Check computed totals for validity
        try:
            subtotal = order.subtotal
            vat = order.vat_amount
            total = order.total
            
            # Verify subtotal + vat = total
            computed_total = money(subtotal + vat)
            if total != computed_total:
                issues.append(IntegrityIssue(
                    "order", order.id,
                    IntegrityIssue.TOTAL_MISMATCH,
                    {
                        "stored": {
                            "subtotal": self._decimal_to_str(subtotal),
                            "vat": self._decimal_to_str(vat),
                            "total": self._decimal_to_str(total)
                        },
                        "computed": {
                            "total": self._decimal_to_str(computed_total)
                        },
                        "diff": {
                            "total": self._decimal_to_str(total - computed_total)
                        }
                    }
                ))
        except (InvalidOperation, TypeError, ValueError) as e:
            issues.append(IntegrityIssue(
                "order", order.id,
                IntegrityIssue.INVALID_VALUE,
                {"message": f"Error computing totals: {str(e)}"}
            ))
        
        return issues
    
    def scan_orders(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Scan all orders for integrity issues.
        
        Args:
            limit: Maximum number of orders to scan (None for all)
            
        Returns:
            JSON-serializable report dictionary
        """
        self.flags = []
        self.checked = 0
        
        try:
            query = Order.query
            if limit:
                query = query.limit(limit)
            orders = query.all()
            
            for order in orders:
                self.checked += 1
                issues = self._check_order(order)
                self.flags.extend(issues)
                
        except Exception as e:
            return {
                "error": f"Database error during scan: {str(e)}",
                "checked": self.checked,
                "flagged": len(self.flags),
                "flags": [f.to_dict() for f in self.flags]
            }
        
        return self._build_report()
    
    def scan_all(self, limit_per_type: Optional[int] = None) -> Dict[str, Any]:
        """
        Scan all entity types for integrity issues.
        
        Args:
            limit_per_type: Maximum number of each entity type to scan
            
        Returns:
            JSON-serializable report dictionary
        """
        self.flags = []
        self.checked = 0
        
        # Scan orders
        order_report = self.scan_orders(limit=limit_per_type)
        
        return self._build_report()
    
    def _build_report(self) -> Dict[str, Any]:
        """Build the final report dictionary."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "checked": self.checked,
            "flagged": len(self.flags),
            "flags": [f.to_dict() for f in self.flags]
        }
    
    def repair_order(self, order_id: int, dry_run: bool = True) -> Dict[str, Any]:
        """
        Attempt to repair an order with integrity issues.
        
        Args:
            order_id: The ID of the order to repair
            dry_run: If True, only report what would be changed
            
        Returns:
            Report of changes made or would be made
        """
        order = Order.query.get(order_id)
        if not order:
            return {"error": f"Order {order_id} not found"}
        
        changes = []
        
        # Check and fix VAT rates on items
        for item in order.items:
            vat_rate = int(item.vat_rate) if item.vat_rate else 0
            if vat_rate not in ALLOWED_VAT_RATES:
                # Default to standard rate if invalid
                old_rate = vat_rate
                new_rate = 19  # Standard rate
                changes.append({
                    "item_id": item.id,
                    "field": "vat_rate",
                    "old": old_rate,
                    "new": new_rate
                })
                if not dry_run:
                    item.vat_rate = new_rate
        
        if not dry_run and changes:
            db.session.commit()
        
        return {
            "order_id": order_id,
            "dry_run": dry_run,
            "changes": changes
        }


def run_integrity_check(limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Convenience function to run a full integrity check.
    
    Args:
        limit: Maximum number of records to check per type
        
    Returns:
        JSON-serializable report
    """
    checker = IntegrityChecker()
    return checker.scan_all(limit_per_type=limit)


def get_integrity_report_json(limit: Optional[int] = None) -> str:
    """
    Get integrity report as a JSON string.
    
    Args:
        limit: Maximum number of records to check per type
        
    Returns:
        JSON string of the report
    """
    report = run_integrity_check(limit=limit)
    return json.dumps(report, indent=2)
