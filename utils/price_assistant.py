import os
from datetime import datetime, timedelta
from sqlalchemy import desc
from models import (
    QuotationItem, Quotation, PriceList, Product, db
)
from utils.logger import logger

class PriceAssistant:
    """
    AI Price Assistant for suggesting prices based on historical data.
    The assistant searches through:
    1. Previous quotations for the same customer with the same product
    2. Price lists for the customer that include the product
    3. General product pricing history across all customers
    """
    
    @staticmethod
    def get_price_history(scientific_name, pot_size, customer_id):
        """
        Get historical price data for a product based on scientific name and pot size
        
        Args:
            scientific_name (str): Scientific name of the plant
            pot_size (str): Pot size or actual size
            customer_id (int): Customer ID
            
        Returns:
            dict: Dictionary containing historical pricing data
        """
        if not scientific_name:
            return {"error": "Scientific name is required for price history"}
        
        try:
            result = {
                "customer_price_list": [],
                "customer_quotations": [],
                "other_quotations": [],
                "suggested_price": None,
                "price_range": {"min": None, "max": None, "avg": None}
            }
            
            # Normalize inputs for database search
            scientific_name = scientific_name.strip().lower()
            pot_size = pot_size.strip().lower() if pot_size else None
            
            # 1. Check customer's price list first (most relevant)
            price_list_items = PriceList.query.filter(
                db.func.lower(Product.scientific_name) == scientific_name,
                PriceList.customer_id == customer_id,
                PriceList.product_id == Product.id
            )
            
            if pot_size:
                price_list_items = price_list_items.filter(
                    db.func.lower(Product.pot) == pot_size
                )
            
            price_list_items = price_list_items.order_by(
                desc(PriceList.updated_at)
            ).limit(5).all()
            
            for item in price_list_items:
                result["customer_price_list"].append({
                    "price": item.price,
                    "date": item.updated_at.strftime("%Y-%m-%d"),
                    "product_name": item.product.name,
                    "pot_size": item.product.pot,
                    "type": "price_list"
                })
            
            # 2. Check customer's previous quotations (second most relevant)
            customer_quotation_items = db.session.query(QuotationItem, Quotation).join(
                Quotation, QuotationItem.quotation_id == Quotation.id
            ).filter(
                db.func.lower(QuotationItem.scientific_name) == scientific_name,
                Quotation.customer_id == customer_id
            )
            
            if pot_size:
                customer_quotation_items = customer_quotation_items.filter(
                    db.func.lower(QuotationItem.pot_size) == pot_size
                )
            
            customer_quotation_items = customer_quotation_items.order_by(
                desc(Quotation.created_at)
            ).limit(5).all()
            
            for item, quotation in customer_quotation_items:
                result["customer_quotations"].append({
                    "price": item.selling_price,
                    "date": quotation.created_at.strftime("%Y-%m-%d"),
                    "quotation_number": quotation.quotation_number,
                    "quantity": item.quantity,
                    "description": item.description,
                    "pot_size": item.pot_size,
                    "type": "customer_quotation"
                })
            
            # 3. Check other customers' quotations (general market pricing)
            other_quotation_items = db.session.query(QuotationItem, Quotation).join(
                Quotation, QuotationItem.quotation_id == Quotation.id
            ).filter(
                db.func.lower(QuotationItem.scientific_name) == scientific_name,
                Quotation.customer_id != customer_id
            )
            
            if pot_size:
                other_quotation_items = other_quotation_items.filter(
                    db.func.lower(QuotationItem.pot_size) == pot_size
                )
            
            other_quotation_items = other_quotation_items.order_by(
                desc(Quotation.created_at)
            ).limit(5).all()
            
            for item, quotation in other_quotation_items:
                result["other_quotations"].append({
                    "price": item.selling_price,
                    "date": quotation.created_at.strftime("%Y-%m-%d"),
                    "customer": quotation.customer.name,  # Include customer name for reference
                    "quantity": item.quantity,
                    "description": item.description,
                    "pot_size": item.pot_size,
                    "type": "other_quotation"
                })
            
            # Calculate price statistics and suggestion
            all_prices = (
                [item["price"] for item in result["customer_price_list"]] +
                [item["price"] for item in result["customer_quotations"]] +
                [item["price"] for item in result["other_quotations"]]
            )
            
            if all_prices:
                # Calculate price range statistics
                result["price_range"]["min"] = min(all_prices)
                result["price_range"]["max"] = max(all_prices)
                result["price_range"]["avg"] = sum(all_prices) / len(all_prices)
                
                # Make price suggestion based on available data
                # Prioritize customer's price list, then recent customer quotations
                if result["customer_price_list"]:
                    # Use most recent price list entry
                    result["suggested_price"] = result["customer_price_list"][0]["price"]
                    result["source"] = "customer price list"
                elif result["customer_quotations"]:
                    # Use most recent customer quotation
                    result["suggested_price"] = result["customer_quotations"][0]["price"]
                    result["source"] = "customer quotation"
                elif result["other_quotations"]:
                    # Use average of other customers' prices
                    prices = [item["price"] for item in result["other_quotations"]]
                    result["suggested_price"] = sum(prices) / len(prices)
                    result["source"] = "market average"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting price history: {str(e)}")
            return {"error": f"Error retrieving price history: {str(e)}"}

# Singleton instance
_price_assistant = None

def get_price_assistant():
    """Get or create the price assistant singleton instance"""
    global _price_assistant
    if _price_assistant is None:
        _price_assistant = PriceAssistant()
    return _price_assistant