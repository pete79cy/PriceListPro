"""
Test script for the AI Insights Feedback system.
"""

import os
import random
import json
from datetime import datetime
from utils.feedback_collector import get_feedback_collector, FEEDBACK_DIR, FEEDBACK_FILE

def main():
    """Test the feedback collector."""
    print("Testing AI Insights Feedback system...")
    
    # Ensure feedback directory exists
    os.makedirs(FEEDBACK_DIR, exist_ok=True)
    print(f"Feedback directory: {FEEDBACK_DIR}")
    
    # Get feedback collector
    feedback_collector = get_feedback_collector()
    
    # Document types for testing
    document_types = ['quotation', 'invoice', 'excel', 'pdf']
    
    # Sample insight types
    insight_types = [
        'pricing_anomalies', 
        'supplier_recommendations', 
        'inventory_analysis',
        'seasonal_trends',
        None  # Test with no insight type
    ]
    
    # Sample comments
    sample_comments = [
        "Very helpful insight, saved me time analyzing the data.",
        "Somewhat useful but could be more specific.",
        "The analysis missed some key factors.",
        "Extremely accurate prediction of price trends.",
        "Helped me identify an issue with our supplier pricing.",
        None  # Test with no comment
    ]
    
    # Generate 10 random feedback entries
    print("\nGenerating random feedback entries:")
    for i in range(10):
        # Random test data
        doc_type = random.choice(document_types)
        doc_id = random.randint(1, 100)
        user_id = random.randint(1, 5)
        rating = random.randint(1, 5)
        comment = random.choice(sample_comments)
        insight_type = random.choice(insight_types)
        
        # Add feedback
        success = feedback_collector.add_feedback(
            document_type=doc_type,
            document_id=doc_id,
            user_id=user_id,
            rating=rating,
            comment=comment,
            insight_type=insight_type
        )
        
        print(f"  #{i+1}: {doc_type} #{doc_id} - Rating: {rating} - Success: {success}")
    
    # Check if feedback file exists
    if os.path.exists(FEEDBACK_FILE):
        print(f"\nFeedback file created at: {FEEDBACK_FILE}")
        
        # Read file contents
        try:
            with open(FEEDBACK_FILE, 'r') as f:
                data = json.load(f)
                print(f"  Contains {len(data)} feedback entries")
        except Exception as e:
            print(f"  Error reading feedback file: {str(e)}")
    else:
        print(f"\nError: Feedback file not created at {FEEDBACK_FILE}")
    
    # Test statistics
    print("\nTesting feedback statistics:")
    stats = feedback_collector.get_feedback_stats()
    print(f"  Total entries: {stats['total_count']}")
    print(f"  Average rating: {stats['average_rating']}")
    print(f"  Rating distribution: {stats['rating_distribution']}")
    print(f"  Document type counts: {stats['document_type_counts']}")
    
    # Test recent entries
    print("\nTesting recent feedback retrieval:")
    recent = feedback_collector.get_recent_feedback(limit=5)
    for entry in recent:
        print(f"  {entry['document_type']} #{entry['document_id']} - Rating: {entry['rating']} - {entry['timestamp']}")
    
    print("\nTest completed.")

if __name__ == "__main__":
    main()