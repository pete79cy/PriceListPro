import os
import json
from datetime import datetime, timedelta
from openai import OpenAI
from utils.logger import logger
from models import Customer, Product, QuotationItem, PriceList, PriceListItem, SupplierProduct, Quotation
from sqlalchemy import desc
from functools import lru_cache

# Singleton pattern for AI price assistant
_ai_price_assistant_instance = None

def get_ai_price_assistant():
    """Get or create the AI price assistant singleton instance"""
    global _ai_price_assistant_instance
    if _ai_price_assistant_instance is None:
        _ai_price_assistant_instance = AIPriceAssistant()
    return _ai_price_assistant_instance

def reset_ai_price_assistant():
    """Reset the AI price assistant singleton, forcing it to reload with new settings"""
    global _ai_price_assistant_instance
    logger.info("Resetting AI price assistant singleton")
    _ai_price_assistant_instance = None
    return get_ai_price_assistant()

class AIPriceAssistant:
    """
    AI-powered price assistant that provides intelligent pricing recommendations
    using OpenAI to analyze historical data, customer segments, and market conditions.
    """
    
    def __init__(self):
        """Initialize the AI price assistant with OpenAI API key from environment"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
            logger.warning("OpenAI API key not found. AI price suggestions disabled.")
        
        # Initialize suggestion cache
        self._suggestion_cache = {}
    
    def is_enabled(self):
        """Check if the AI assistant is enabled (API key is set)"""
        return self.enabled
    
    def get_ai_price_suggestion(self, scientific_name, pot_size, customer_id, cost_price=None):
        """
        Get AI-powered price suggestion for a product and customer combination
        
        Args:
            scientific_name (str): Scientific name of the plant
            pot_size (str): Pot size or actual size
            customer_id (int): Customer ID
            cost_price (float): Optional cost price override
            
        Returns:
            dict: Dictionary containing AI price suggestion and rationale
        """
        start_time = datetime.now()
        logger.info(f"Starting AI price suggestion for {scientific_name} ({pot_size}) for customer {customer_id}")
        
        # Check if AI analysis is enabled
        if not self.enabled:
            logger.warning("AI price suggestion was requested but is not enabled")
            return {
                "error": "AI price suggestions are not enabled. Please add an OpenAI API key.",
                "error_code": "AI_NOT_ENABLED",
                "resolution": "Add your OpenAI API key in the system settings"
            }
        
        # Validate inputs
        if not scientific_name or not customer_id:
            return {
                "error": "Scientific name and customer ID are required",
                "error_code": "MISSING_PARAMETERS"
            }
        
        # Check cache first
        cache_key = f"{scientific_name}_{pot_size}_{customer_id}_{cost_price}"
        if cache_key in self._suggestion_cache:
            logger.info(f"Using cached AI suggestion for {scientific_name}")
            return self._suggestion_cache[cache_key]
        
        try:
            # Gather context data
            context = self._gather_pricing_context(scientific_name, pot_size, customer_id, cost_price)
            
            if context.get("error"):
                return context
            
            # Generate AI prompt
            prompt = self._build_pricing_prompt(context)
            
            # Get AI suggestion
            ai_response = self._get_openai_response(prompt)
            
            if ai_response and ai_response.startswith("Error:"):
                logger.error(f"OpenAI API error during price suggestion: {ai_response}")
                return {"error": ai_response, "error_code": "OPENAI_API_ERROR"}
            
            # Parse AI response
            suggestion = self._parse_ai_response(ai_response)
            
            # Cache the results (don't cache errors)
            if "error" not in suggestion:
                self._suggestion_cache[cache_key] = suggestion
                logger.info(f"Cached AI suggestion for {scientific_name}")
            
            # Log duration for performance monitoring
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"AI price suggestion completed in {duration:.2f} seconds")
            
            return suggestion
            
        except Exception as e:
            error_msg = f"Error generating AI price suggestion: {str(e)}"
            logger.error(error_msg)
            return {
                "error": error_msg,
                "error_code": "AI_SUGGESTION_ERROR"
            }
    
    def _gather_pricing_context(self, scientific_name, pot_size, customer_id, cost_price=None):
        """
        Gather all relevant context for AI pricing analysis
        
        Args:
            scientific_name (str): Scientific name of the plant
            pot_size (str): Pot size or actual size
            customer_id (int): Customer ID
            cost_price (float): Optional cost price override
            
        Returns:
            dict: Context information for AI analysis
        """
        try:
            context = {}
            
            # Get customer information
            customer = Customer.query.get(customer_id)
            if not customer:
                return {
                    "error": f"Customer with ID {customer_id} not found",
                    "error_code": "CUSTOMER_NOT_FOUND"
                }
            
            context["customer"] = {
                "id": customer.id,
                "name": customer.name,
                "segment": customer.category.name if customer.category else "Unclassified",
                "credit_terms": getattr(customer, 'credit_terms', 'standard'),
                "email": customer.email
            }
            
            # Calculate customer lifetime value (approximate)
            customer_orders = QuotationItem.query.join(Quotation).filter(
                Quotation.customer_id == customer_id
            ).all()
            
            total_value = sum(item.selling_price * item.quantity for item in customer_orders if item.selling_price)
            context["customer"]["lifetime_value"] = round(total_value, 2)
            
            # Find product information
            # Look for supplier products with matching scientific name
            supplier_products = SupplierProduct.query.filter(
                SupplierProduct.scientific_name.ilike(f"%{scientific_name}%")
            ).all()
            
            # Find the best matching product (exact scientific name and pot size if possible)
            best_match = None
            for sp in supplier_products:
                if sp.scientific_name.lower() == scientific_name.lower():
                    if pot_size and sp.pot_size and sp.pot_size.lower() == pot_size.lower():
                        best_match = sp
                        break
                    elif not best_match:
                        best_match = sp
            
            if best_match:
                context["product"] = {
                    "id": best_match.id,
                    "name": best_match.scientific_name,
                    "size": pot_size or best_match.pot_size or "",
                    "cost_price": cost_price or best_match.cost_price or 0.0,
                    "stock_qty": getattr(best_match, 'stock_qty', 0),
                    "supplier": best_match.supplier.name if best_match.supplier else "Unknown"
                }
            else:
                # Create a basic product context even if not found in supplier products
                context["product"] = {
                    "id": None,
                    "name": scientific_name,
                    "size": pot_size or "",
                    "cost_price": cost_price or 0.0,
                    "stock_qty": 0,
                    "supplier": "Unknown"
                }
            
            # Get historical pricing data
            context["historical_pricing"] = self._get_historical_pricing(scientific_name, pot_size, customer_id)
            
            # Get customer-specific price list
            context["price_list"] = self._get_customer_price_list(scientific_name, pot_size, customer_id)
            
            # Get market data (from other customers)
            context["market_data"] = self._get_market_data(scientific_name, pot_size, customer_id)
            
            return context
            
        except Exception as e:
            logger.error(f"Error gathering pricing context: {str(e)}")
            return {
                "error": f"Failed to gather pricing context: {str(e)}",
                "error_code": "CONTEXT_GATHERING_ERROR"
            }
    
    def _get_historical_pricing(self, scientific_name, pot_size, customer_id, limit=10):
        """Get historical pricing data for the product and customer"""
        try:
            # Query quotation items with matching scientific name
            historical_items = QuotationItem.query.join(Quotation).filter(
                QuotationItem.scientific_name.ilike(f"%{scientific_name}%")
            )
            
            # Add pot size filter if provided
            if pot_size:
                historical_items = historical_items.filter(QuotationItem.pot_size.ilike(f"%{pot_size}%"))
            
            # Order by most recent first
            historical_items = historical_items.order_by(desc(Quotation.quotation_date)).limit(limit).all()
            
            pricing_history = []
            for item in historical_items:
                if item.quotation and item.selling_price:
                    is_same_customer = item.quotation.customer_id == customer_id
                    pricing_history.append({
                        "date": item.quotation.quotation_date.strftime("%Y-%m-%d") if item.quotation.quotation_date else "Unknown",
                        "customer": "same customer" if is_same_customer else (item.quotation.customer.name if item.quotation.customer else "Unknown"),
                        "quantity": item.quantity or 1,
                        "unit_price": float(item.selling_price),
                        "is_same_customer": is_same_customer
                    })
            
            return pricing_history
            
        except Exception as e:
            logger.error(f"Error getting historical pricing: {str(e)}")
            return []
    
    def _get_customer_price_list(self, scientific_name, pot_size, customer_id):
        """Get customer-specific price list entry"""
        try:
            # Find price lists for this customer
            price_lists = PriceList.query.filter_by(customer_id=customer_id).all()
            
            for price_list in price_lists:
                # Look for matching items in the price list
                for item in price_list.items:
                    if (item.scientific_name and 
                        item.scientific_name.lower() == scientific_name.lower()):
                        # Check pot size if provided
                        if not pot_size or (item.pot_size and item.pot_size.lower() == pot_size.lower()):
                            return {
                                "price": float(item.price),
                                "updated_at": price_list.updated_at.strftime("%Y-%m-%d") if price_list.updated_at else "Unknown"
                            }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting customer price list: {str(e)}")
            return None
    
    def _get_market_data(self, scientific_name, pot_size, customer_id):
        """Get market data from other customers"""
        try:
            # Get pricing from other customers (not the current customer)
            market_items = QuotationItem.query.join(Quotation).filter(
                QuotationItem.scientific_name.ilike(f"%{scientific_name}%"),
                Quotation.customer_id != customer_id,
                QuotationItem.selling_price.isnot(None)
            )
            
            if pot_size:
                market_items = market_items.filter(QuotationItem.pot_size.ilike(f"%{pot_size}%"))
            
            market_items = market_items.limit(20).all()
            
            if market_items:
                prices = [float(item.selling_price) for item in market_items if item.selling_price]
                if prices:
                    avg_price = sum(prices) / len(prices)
                    return {
                        "average_market_price": round(avg_price, 2),
                        "price_range": {
                            "min": round(min(prices), 2),
                            "max": round(max(prices), 2)
                        },
                        "sample_size": len(prices)
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting market data: {str(e)}")
            return None
    
    def _build_pricing_prompt(self, context):
        """Build the AI prompt for pricing analysis"""
        
        # Format customer-specific history (Tier 1)
        customer_history_str = ""
        if context["historical_pricing"]:
            customer_items = [item for item in context["historical_pricing"] if item.get('is_same_customer')]
            if customer_items:
                for item in customer_items[:5]:
                    customer_history_str += f"  Date: {item['date']} | Qty: {item['quantity']} | Price: €{item['unit_price']:.2f}\n"
            else:
                customer_history_str = "  None"
        else:
            customer_history_str = "  None"
        
        # Format global history (Tier 2 - other customers)
        global_history_str = ""
        if context["historical_pricing"]:
            global_items = [item for item in context["historical_pricing"] if not item.get('is_same_customer')]
            if global_items:
                for item in global_items[:5]:
                    global_history_str += f"  Date: {item['date']} | Qty: {item['quantity']} | Price: €{item['unit_price']:.2f}\n"
            else:
                global_history_str = "  None"
        else:
            global_history_str = "  None"
        
        # Format price list
        price_list_str = "None"
        if context["price_list"]:
            price_list_str = f"€{context['price_list']['price']:.2f} (last updated {context['price_list']['updated_at']})"
        
        # Format market data
        market_avg_str = "n/a"
        if context["market_data"]:
            market_avg_str = f"{context['market_data']['average_market_price']:.2f}"
        
        prompt = f"""You are an expert Wholesale Pricing Analyst. Determine the unit price (Ex-VAT) for a specific inquiry.

=== 1. PRICING LOGIC & HIERARCHY ===
1. **PRIORITY - CUSTOMER DATA:** - Check "Customer Price List" and "Customer Past Transactions" first.
   - If valid data exists here, use it to ensure consistency with their history.
   
2. **FALLBACK - GLOBAL DATA:**
   - ONLY if the customer has NO price list and NO past transactions for this product, look at "Global Sales History" (sales to other people) or "Market Data".
   - **CRITICAL REQUIREMENT:** If you use this fallback, your rationale MUST explicitly state that this is a generic price because no customer history exists.

3. **MARGIN FLOOR:** Ensure price > Cost + 25% (unless Customer Segment = "VIP", then Cost + 15%).

=== 2. INPUT DATA ===

--- CONTEXT ---
• Customer: {context['customer']['name']} (ID: {context['customer']['id']}) | Segment: {context['customer']['segment']}
• Product: {context['product']['name']} | Cost: €{context['product']['cost_price']:.2f} | Stock: {context['product']['stock_qty']}
• Inquired Qty: 1

--- TIER 1: CUSTOMER SPECIFIC DATA ---
• Contract Price List: {price_list_str}
• Customer Past Transactions (This Product):
{customer_history_str}

--- TIER 2: GLOBAL DATA (FALLBACK) ---
• Global Sales History (Other Customers):
{global_history_str}
• Market Competitor Avg: €{market_avg_str}

=== 3. OUTPUT FORMAT ===
Return ONLY valid JSON. No markdown.

{{"recommended_price": 0.00, "rationale": "If Tier 1 data used: 'Matches their last purchase in Oct.' || If Tier 2 used: 'NO CUSTOMER HISTORY: Price derived from global sales average and margin targets.'"}}"""
        
        return prompt
    
    def _get_openai_response(self, prompt):
        """Get response from OpenAI API"""
        try:
            if not self.client:
                return "Error: OpenAI client not initialized"
                
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": prompt}
                ],
                temperature=0.1,  # Keep suggestions stable
                max_tokens=200,   # Limited response for JSON output
                timeout=30.0
            )
            
            if response and response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                return content.strip() if content else "Error: Empty response from AI"
            else:
                return "Error: Invalid response format from AI"
        
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return f"Error: {str(e)}"
    
    def _parse_ai_response(self, response):
        """Parse the AI response JSON"""
        try:
            # Clean the response (remove any markdown code blocks)
            cleaned_response = response.strip()
            if cleaned_response.startswith("```"):
                lines = cleaned_response.split('\n')
                cleaned_response = '\n'.join(lines[1:-1])
            
            # Parse JSON
            data = json.loads(cleaned_response)
            
            # Validate required fields
            if "recommended_price" not in data or "rationale" not in data:
                return {
                    "error": "AI response missing required fields",
                    "error_code": "INVALID_AI_RESPONSE"
                }
            
            # Validate price is reasonable
            price = float(data["recommended_price"])
            if price < 0 or price > 10000:  # Sanity check
                return {
                    "error": f"AI suggested unreasonable price: €{price}",
                    "error_code": "UNREASONABLE_PRICE"
                }
            
            return {
                "suggested_price": price,
                "rationale": data["rationale"],
                "source": "AI analysis"
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response JSON: {str(e)}")
            logger.error(f"Raw response: {response}")
            return {
                "error": f"Failed to parse AI response: {str(e)}",
                "error_code": "JSON_PARSE_ERROR"
            }
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            return {
                "error": f"Error processing AI response: {str(e)}",
                "error_code": "RESPONSE_PROCESSING_ERROR"
            }