"""
Notification utilities for sending alerts to various channels (Slack, email, etc.).
"""

import os
import json
import logging
import requests
from typing import Optional, Dict, Any, Union

# Environment variables for Slack configuration
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

# Get logger
from utils.logger import logger

def send_slack_notification(lead) -> bool:
    """
    Send a notification to Slack when a new lead is created.
    
    Args:
        lead: The Lead object to notify about
        
    Returns:
        bool: True if the notification was sent successfully, False otherwise
    """
    if not SLACK_WEBHOOK_URL:
        logger.warning("Slack webhook URL not configured - notification not sent")
        return False
        
    # Format items if they exist
    items_text = ""
    if lead.items:
        items = lead.items
        if isinstance(items, str):
            try:
                items = json.loads(items)
            except Exception as e:
                logger.error(f"Failed to parse lead items JSON: {str(e)}")
                items = []
                
        items_list = []
        for item in items:
            if isinstance(item, dict):
                name = item.get('name', 'Unknown')
                size = item.get('size', '')
                qty = item.get('qty', 1)
                items_list.append(f"• {name} ({size}) x{qty}")
        
        if items_list:
            items_text = "\n".join(items_list)
        
    # Prepare the Slack message payload
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🌱 New Quote Request",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Customer:*\n{lead.name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Contact:*\n{lead.email}"
                    }
                ]
            }
        ]
    }
    
    # Add phone if available
    if lead.phone:
        message["blocks"].append({
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Phone:*\n{lead.phone}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Status:*\n{lead.status}"
                }
            ]
        })
        
    # Add message if available
    if lead.message:
        message["blocks"].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Message:*\n{lead.message}"
            }
        })
        
    # Add items if available
    if items_text:
        message["blocks"].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Requested Items:*\n{items_text}"
            }
        })
        
    # Add a divider
    message["blocks"].append({
        "type": "divider"
    })
    
    # Add a link to view the lead in the admin panel
    message["blocks"].append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"Lead ID: {lead.id} • Created at: {lead.created_at.strftime('%Y-%m-%d %H:%M')}"
            }
        ]
    })
    
    # Send the notification to Slack
    try:
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json=message,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        logger.info(f"Slack notification sent for lead #{lead.id}")
        return True
        
    except requests.RequestException as e:
        logger.error(f"Failed to send Slack notification: {str(e)}")
        return False