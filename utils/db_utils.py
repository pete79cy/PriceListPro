"""
Database utility functions for handling connection issues and other database operations.
"""

import functools
import logging
import time
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from flask import flash
from app import db
from utils.logger import logger

def with_db_reconnect(max_retries=3, backoff_factor=0.5):
    """
    Decorator to handle database connection issues by attempting to reconnect.
    
    Args:
        max_retries (int): Maximum number of reconnection attempts
        backoff_factor (float): Factor to increase wait time between retries
        
    Returns:
        decorator: Function wrapper that handles database reconnection
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except OperationalError as e:
                    retries += 1
                    error_msg = str(e)
                    logger.warning(f"Database connection error: {error_msg}")
                    
                    # Check if it's a connection issue (expanded list of error messages)
                    connection_errors = [
                        "connection", "closed", "terminated", "timed out", "ssl", 
                        "broken pipe", "reset by peer", "unexpectedly", "server closed"
                    ]
                    
                    if any(msg in error_msg.lower() for msg in connection_errors):
                        if retries <= max_retries:
                            # Calculate delay with exponential backoff
                            delay = backoff_factor * (2 ** (retries - 1))
                            logger.info(f"Attempting database reconnection (attempt {retries}/{max_retries}) after {delay:.2f}s delay")
                            
                            try:
                                # Close all connections in the pool
                                db.engine.dispose()
                                db.session.rollback()
                                
                                # Wait with exponential backoff before retry
                                if delay > 0:
                                    time.sleep(delay)
                                
                                # If this is the last retry, alert the user
                                if retries == max_retries:
                                    logger.info("Final reconnection attempt")
                            except Exception as dispose_err:
                                logger.error(f"Error disposing connections: {str(dispose_err)}")
                        else:
                            # We've exhausted retries
                            logger.error(f"Maximum reconnection attempts ({max_retries}) reached. Giving up.")
                            flash("Database connection lost. Please try again later.", "danger")
                            raise
                    else:
                        # Not a connection issue, re-raise the exception
                        logger.error(f"Database error (not connection-related): {error_msg}")
                        raise
                except SQLAlchemyError as e:
                    # Handle other SQLAlchemy errors
                    logger.error(f"SQLAlchemy error: {str(e)}")
                    db.session.rollback()
                    raise
                except Exception as e:
                    # Handle other unexpected errors
                    logger.error(f"Unexpected error in database operation: {str(e)}")
                    db.session.rollback()
                    raise
            
            # If we get here, we've exhausted retries
            raise OperationalError(f"Maximum database reconnection attempts ({max_retries}) reached", None, None)
        
        return wrapper
    
    return decorator

# Simple function to test database connectivity
@with_db_reconnect(max_retries=3)
def test_db_connection():
    """Test database connectivity by executing a simple query"""
    try:
        db.session.execute("SELECT 1").scalar()
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False