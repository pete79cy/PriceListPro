"""
Simple script to check VAT calculation for PAK-2025-028
"""
from flask import Flask
import os
from app import app, db
from models import Quotation, QuotationItem

def check_vat(quotation_number):
    with app.app_context():
        # Get the quotation
        quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
        
        if not quotation:
            print(f"Quotation {quotation_number} not found")
            return
        
        print(f"\nQuotation {quotation.quotation_number} - {quotation.customer.name}")
        print(f"Date: {quotation.quotation_date}")
        print(f"Total items: {len(quotation.items)}")
        print("-" * 80)
        
        # Breakdown by VAT rate
        items_by_rate = {}
        for item in quotation.items:
            rate = item.vat_rate
            if rate not in items_by_rate:
                items_by_rate[rate] = []
            items_by_rate[rate].append(item)
        
        # Print summary for each VAT rate
        for rate, items in items_by_rate.items():
            subtotal = sum(item.quantity * item.selling_price for item in items)
            vat_amount = subtotal * (rate / 100)
            print(f"\nItems with {rate}% VAT: {len(items)} items")
            print(f"Subtotal: €{subtotal:.2f}")
            print(f"VAT amount: €{vat_amount:.2f}")
        
        # Calculate overall total
        overall_subtotal = sum(item.quantity * item.selling_price for item in quotation.items)
        vat_totals = {}
        
        for item in quotation.items:
            item_subtotal = item.quantity * item.selling_price
            vat_rate = item.vat_rate
            vat_amount = item_subtotal * (vat_rate / 100)
            
            if vat_rate in vat_totals:
                vat_totals[vat_rate] += vat_amount
            else:
                vat_totals[vat_rate] = vat_amount
        
        # Print overall calculation
        print("\nOverall calculation:")
        print(f"Subtotal: €{overall_subtotal:.2f}")
        
        total_vat = 0
        for rate, amount in vat_totals.items():
            print(f"VAT {rate}%: €{amount:.2f}")
            total_vat += amount
        
        grand_total = overall_subtotal + total_vat
        print(f"Total VAT: €{total_vat:.2f}")
        print(f"Grand total: €{grand_total:.2f}")
        
        # Check if the quotation total matches the calculated total
        if quotation.total_amount:
            print(f"\nStored quotation total: €{quotation.total_amount:.2f}")
            if abs(grand_total - quotation.total_amount) < 0.01:
                print("✅ Calculated total matches stored total")
            else:
                print("❌ Calculated total does NOT match stored total")
                print(f"Difference: €{abs(grand_total - quotation.total_amount):.2f}")

if __name__ == "__main__":
    check_vat("PAK-2025-028")