"""
User feedback collection and management system for AI insights and analysis.
Allows users to rate the quality and accuracy of AI-generated insights.
"""

import os
import json
import time
from datetime import datetime, timedelta
import logging
from threading import Lock
from utils.logger import logger

# Constants
FEEDBACK_DIR = 'data/feedback'
FEEDBACK_FILE = os.path.join(FEEDBACK_DIR, 'ai_insights_feedback.json')

# Singleton instance
_feedback_collector = None
_feedback_collector_lock = Lock()

class FeedbackCollector:
    """
    Class for collecting and storing user feedback on AI insights.
    Maintains a persistent record of feedback for future model improvements.
    """
    
    def __init__(self):
        """Initialize the feedback collector."""
        # Create feedback directory if it doesn't exist
        os.makedirs(FEEDBACK_DIR, exist_ok=True)
        
        # Initialize feedback data
        self.feedback_data = []
        self._load_feedback()
        
        # Log initialization
        logger.info("Feedback collector initialized")
        
    def _load_feedback(self):
        """Load existing feedback data from file."""
        try:
            if os.path.exists(FEEDBACK_FILE):
                with open(FEEDBACK_FILE, 'r') as f:
                    self.feedback_data = json.load(f)
                logger.info(f"Loaded {len(self.feedback_data)} feedback entries from {FEEDBACK_FILE}")
            else:
                logger.info(f"No existing feedback file found at {FEEDBACK_FILE}")
                self.feedback_data = []
        except Exception as e:
            logger.error(f"Error loading feedback data: {str(e)}")
            self.feedback_data = []
    
    def _save_feedback(self):
        """Save current feedback data to file."""
        try:
            with open(FEEDBACK_FILE, 'w') as f:
                json.dump(self.feedback_data, f, indent=2)
            logger.info(f"Saved {len(self.feedback_data)} feedback entries to {FEEDBACK_FILE}")
            return True
        except Exception as e:
            logger.error(f"Error saving feedback data: {str(e)}")
            return False
    
    def add_feedback(self, document_type, document_id, user_id, rating, comment=None, insight_type=None):
        """
        Add a new feedback entry.
        
        Args:
            document_type: Type of document ('quotation', 'invoice', 'excel', 'pdf')
            document_id: ID of the document
            user_id: ID of the user providing feedback
            rating: Numerical rating (1-5)
            comment: Optional user comment
            insight_type: Optional specific section of the insights being rated
            
        Returns:
            bool: Success status
        """
        try:
            # Validate rating
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    logger.warning(f"Invalid rating value: {rating}. Must be between 1-5.")
                    rating = max(1, min(5, rating))  # Clamp to valid range
            except (ValueError, TypeError):
                logger.error(f"Invalid rating format: {rating}")
                return False
            
            # Create feedback entry
            feedback_entry = {
                'id': len(self.feedback_data) + 1,
                'document_type': document_type,
                'document_id': document_id,
                'user_id': user_id,
                'rating': rating,
                'timestamp': datetime.now().isoformat(),
                'comment': comment,
                'insight_type': insight_type
            }
            
            # Add to collection
            self.feedback_data.append(feedback_entry)
            
            # Save to disk
            return self._save_feedback()
        
        except Exception as e:
            logger.error(f"Error adding feedback: {str(e)}")
            return False
    
    def get_feedback_stats(self, document_type=None, days=30):
        """
        Get feedback statistics.
        
        Args:
            document_type: Optional filter by document type
            days: Number of days to include in statistics (default: 30)
            
        Returns:
            dict: Feedback statistics
        """
        try:
            # Calculate the cutoff date
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Filter entries by date and optionally by document type
            filtered_entries = [
                entry for entry in self.feedback_data 
                if entry['timestamp'] >= cutoff_date and
                (document_type is None or entry['document_type'] == document_type)
            ]
            
            # Count total entries
            total_count = len(filtered_entries)
            
            # Calculate average rating
            if total_count > 0:
                average_rating = round(sum(entry['rating'] for entry in filtered_entries) / total_count, 1)
            else:
                average_rating = 0
            
            # Count by document type
            document_type_counts = {}
            for entry in filtered_entries:
                doc_type = entry['document_type']
                document_type_counts[doc_type] = document_type_counts.get(doc_type, 0) + 1
            
            # Distribution of ratings
            rating_distribution = {str(i): 0 for i in range(1, 6)}
            for entry in filtered_entries:
                rating = str(entry['rating'])
                rating_distribution[rating] = rating_distribution.get(rating, 0) + 1
            
            # Return statistics
            return {
                'total_count': total_count,
                'average_rating': average_rating,
                'document_type_counts': document_type_counts,
                'rating_distribution': rating_distribution,
                'time_period': f"Last {days} days"
            }
        
        except Exception as e:
            logger.error(f"Error calculating feedback stats: {str(e)}")
            return {
                'total_count': 0,
                'average_rating': 0,
                'document_type_counts': {},
                'rating_distribution': {str(i): 0 for i in range(1, 6)},
                'time_period': f"Last {days} days",
                'error': str(e)
            }
    
    def get_recent_feedback(self, limit=10, document_type=None):
        """
        Get recent feedback entries.
        
        Args:
            limit: Maximum number of entries to return
            document_type: Optional filter by document type
            
        Returns:
            list: Recent feedback entries
        """
        try:
            # Apply filters
            filtered_entries = self.feedback_data
            if document_type:
                filtered_entries = [e for e in filtered_entries if e['document_type'] == document_type]
            
            # Sort by timestamp (newest first)
            sorted_entries = sorted(filtered_entries, key=lambda x: x['timestamp'], reverse=True)
            
            # Return limited entries
            return sorted_entries[:limit]
        
        except Exception as e:
            logger.error(f"Error retrieving recent feedback: {str(e)}")
            return []

def get_feedback_collector():
    """Get or create the feedback collector singleton."""
    global _feedback_collector
    
    if _feedback_collector is None:
        with _feedback_collector_lock:
            if _feedback_collector is None:
                _feedback_collector = FeedbackCollector()
    
    return _feedback_collector