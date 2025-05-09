"""
External quotation system integration utilities.

This module provides functionality to interact with an external quotation system via its API.
It allows creating draft quotes from Lead data in the external system.
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Any, Union

# Environment variables for API configuration
QUOTER_API_URL = os.environ.get("QUOTER_API_URL")     # e.g. https://quotes.yourvendor.com/api/drafts
QUOTER_API_TOKEN = os.environ.get("QUOTER_API_TOKEN")  # Bearer token or API key

# Get logger
from utils.logger import logger

def create_draft_quote(lead) -> Optional[Dict[str, Any]]:
    """
    Push a new draft quote into the external quotation system.
    
    Args:
        lead: Lead object containing customer and item information
        
    Returns:
        Dictionary with the response from the API or None if the API call failed
        
    Expects the external API to accept JSON like:
    {
      "customer_name": "...",
      "customer_email": "...",
      "customer_phone": "...",
      "items": [
         {"plant_id": 123, "name": "Blue bango", "size": "2L", "qty": 50},
         ...
      ]
    }
    """
    # Check if API configuration is available
    if not QUOTER_API_URL or not QUOTER_API_TOKEN:
        logger.error("External quotation system API not configured - missing environment variables")
        return None
        
    # Convert lead items from JSON if needed
    items = lead.items
    if isinstance(items, str):
        import json
        try:
            items = json.loads(items)
        except Exception as e:
            logger.error(f"Failed to parse lead items JSON: {str(e)}")
            items = []
    
    # Prepare the payload for the external API
    payload = {
        "customer_name": lead.name,
        "customer_email": lead.email,
        "customer_phone": lead.phone or "",
        "items": [
            {
                "plant_id": item.get("id", 0),
                "name": item.get("name", ""),
                "size": item.get("size", ""),
                "qty": item.get("qty", 1),
            }
            for item in items if isinstance(item, dict)
        ]
    }
    
    # Prepare headers with authentication
    headers = {
        "Authorization": f"Bearer {QUOTER_API_TOKEN}",
        "Content-Type": "application/json",
    }

    # Call the external API
    try:
        response = requests.post(QUOTER_API_URL, 
                               json=payload, 
                               headers=headers, 
                               timeout=10)
        response.raise_for_status()  # Raise exception for 4xx/5xx responses
        
        # Parse the response
        data = response.json()
        logger.info(f"Created draft quote #{lead.id} in external system, external_id={data.get('draft_id')}")
        
        # Update the lead with the external draft ID if available
        if data.get('draft_id') and hasattr(lead, 'quoter_draft_id'):
            from app import db
            lead.quoter_draft_id = data.get('draft_id')
            db.session.commit()
            logger.info(f"Updated lead #{lead.id} with external draft ID {lead.quoter_draft_id}")
            
        return data

    except requests.RequestException as e:
        logger.error(f"Failed to create draft quote for Lead {lead.id}: {str(e)}")
        logger.error(f"Request payload: {payload}")
        return None

def get_quote_status(draft_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the status of a draft quote in the external system.
    
    Args:
        draft_id: The ID of the draft in the external system
        
    Returns:
        Dictionary with the response from the API or None if the API call failed
    """
    # Check if API configuration is available
    if not QUOTER_API_URL or not QUOTER_API_TOKEN:
        logger.error("External quotation system API not configured - missing environment variables")
        return None
        
    # Prepare URL for the GET request
    url = f"{QUOTER_API_URL}/{draft_id}"
    
    # Prepare headers with authentication
    headers = {
        "Authorization": f"Bearer {QUOTER_API_TOKEN}",
        "Content-Type": "application/json",
    }
    
    # Call the external API
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    
    except requests.RequestException as e:
        logger.error(f"Failed to get status for draft quote {draft_id}: {str(e)}")
        return None