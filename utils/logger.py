"""
Enhanced logging setup with structured logs for the application.
Provides consistent log formats and context for easier analysis.
"""
import logging
import os
import json
import time
import traceback
import socket
import functools
from datetime import datetime
from flask import request

# Create a custom logger
logger = logging.getLogger('plant_pricing_system')

# Default log level - can be overridden with environment variable
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
LOG_FORMAT = os.environ.get('LOG_FORMAT', 'TEXT')  # TEXT or JSON
HOSTNAME = socket.gethostname()

# Define a custom JSON formatter
class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the log record.
    
    Attributes:
        static_fields (dict): Static fields to add to every log message
    """
    def __init__(self, static_fields=None):
        """
        Initialize the formatter with static fields.
        
        Args:
            static_fields (dict, optional): Static fields to add to all log messages
        """
        super(JsonFormatter, self).__init__()
        self.static_fields = static_fields or {}
    
    def format(self, record):
        """
        Format the specified record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            str: Formatted JSON string
        """
        message = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'logger': record.name,
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process_id': record.process,
            'thread_id': record.thread,
            'hostname': HOSTNAME
        }
        
        # Add exception info if present
        if record.exc_info:
            message['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields from the record
        if hasattr(record, 'extra_fields'):
            message.update(record.extra_fields)
        
        # Add static fields
        message.update(self.static_fields)
        
        return json.dumps(message)

# Text formatter with more context
class DetailedFormatter(logging.Formatter):
    """A more detailed text formatter with color support for console output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[41m',  # Red background
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        """Format the log record with colors and extra context."""
        # Check if running in a terminal that supports colors
        use_colors = hasattr(logging, '_console_supports_color') and logging._console_supports_color
        
        # Add color to level name if supported
        if use_colors and record.levelname in self.COLORS:
            colored_level = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        else:
            colored_level = record.levelname
        
        # Format the basic message
        log_message = f"{datetime.fromtimestamp(record.created).isoformat()} - {colored_level} - {record.name} - {record.getMessage()}"
        
        # Add context information (module, function, line)
        context = f" [{record.module}.{record.funcName}:{record.lineno}]"
        log_message += context
        
        # Add exception info if present
        if record.exc_info:
            log_message += f"\nException: {record.exc_info[0].__name__}: {record.exc_info[1]}"
            log_message += f"\nTraceback:\n{''.join(traceback.format_exception(*record.exc_info))}"
        
        return log_message

# Configure the logger if not already configured
if not logger.handlers:
    # Set the level of the logger based on environment variable
    level = getattr(logging, LOG_LEVEL, logging.INFO)
    logger.setLevel(level)
    
    # Create a handler to send log messages to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Choose formatter based on environment variable
    if LOG_FORMAT.upper() == 'JSON':
        formatter = JsonFormatter()
    else:
        formatter = DetailedFormatter()
    
    console_handler.setFormatter(formatter)
    
    # Add the handler to the logger
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger to avoid duplicate logs
    logger.propagate = False
    
    # Log that the logger is configured
    logger.debug("Logger initialized with level: %s, format: %s", LOG_LEVEL, LOG_FORMAT)

# Create helper functions for structured logging
def log_with_context(level, message, **kwargs):
    """
    Log a message with additional context fields.
    
    Args:
        level: Log level (e.g., 'info', 'error')
        message: Log message
        **kwargs: Additional context fields to include in the log
    """
    extra = {'extra_fields': kwargs}
    getattr(logger, level)(message, extra=extra)

def log_function_call(func_name, duration_ms=None, **kwargs):
    """
    Log information about a function call with timing.
    
    Args:
        func_name: Name of the function
        duration_ms: Duration in milliseconds
        **kwargs: Additional context to include
    """
    context = {
        'function': func_name,
        'duration_ms': duration_ms,
        **kwargs
    }
    log_with_context('info', f"Function {func_name} completed in {duration_ms}ms", **context)

def log_api_request(endpoint, method, status_code, duration_ms, **kwargs):
    """
    Log an API request with timing and result.
    
    Args:
        endpoint: API endpoint
        method: HTTP method
        status_code: HTTP status code
        duration_ms: Duration in milliseconds
        **kwargs: Additional context to include
    """
    context = {
        'endpoint': endpoint,
        'method': method,
        'status_code': status_code,
        'duration_ms': duration_ms,
        **kwargs
    }
    log_with_context('info', 
                    f"API {method} {endpoint} completed with status {status_code} in {duration_ms}ms", 
                    **context)

def log_document_processing(document_type, document_id, status, duration_ms=None, **kwargs):
    """
    Log document processing information.
    
    Args:
        document_type: Type of document (e.g., 'excel', 'pdf')
        document_id: Document identifier
        status: Processing status
        duration_ms: Duration in milliseconds
        **kwargs: Additional context to include
    """
    context = {
        'document_type': document_type,
        'document_id': document_id,
        'status': status,
        'duration_ms': duration_ms,
        **kwargs
    }
    log_with_context('info', 
                    f"Document {document_type} #{document_id} processing {status} in {duration_ms}ms", 
                    **context)

def log_user_action(user_id, action, status, **kwargs):
    """
    Log a user action.
    
    Args:
        user_id: User identifier
        action: Action performed
        status: Action status
        **kwargs: Additional context to include
    """
    context = {
        'user_id': user_id,
        'action': action,
        'status': status,
        **kwargs
    }
    log_with_context('info', f"User {user_id} {action} - {status}", **context)
    
def log_api_request(func):
    """
    Decorator to log API requests with timing and status code.
    
    Args:
        func: The function to decorate
        
    Returns:
        The decorated function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        endpoint = request.path
        method = request.method
        client_ip = request.remote_addr
        
        try:
            response = func(*args, **kwargs)
            status_code = response[1] if isinstance(response, tuple) and len(response) > 1 else 200
            
            # Log successful request
            duration_ms = round((time.time() - start_time) * 1000, 2)
            log_api_request(endpoint, method, status_code, duration_ms, client_ip=client_ip)
            
            return response
        except Exception as e:
            # Log failed request
            duration_ms = round((time.time() - start_time) * 1000, 2)
            log_with_context('error', 
                            f"API {method} {endpoint} failed after {duration_ms}ms: {str(e)}",
                            endpoint=endpoint,
                            method=method,
                            status_code=500,
                            duration_ms=duration_ms,
                            client_ip=client_ip,
                            exception=str(e))
            raise
            
    return wrapper

# Context manager for timing operations
class TimingLogger:
    """Context manager for timing operations and logging the duration."""
    
    def __init__(self, operation_name, log_level='info', **extra_context):
        """
        Initialize the timing logger.
        
        Args:
            operation_name: Name of the operation to time
            log_level: Log level to use
            **extra_context: Additional context to include in the log
        """
        self.operation_name = operation_name
        self.log_level = log_level
        self.extra_context = extra_context
        self.start_time = None
    
    def __enter__(self):
        """Start the timer when entering the context."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Log the duration when exiting the context."""
        duration_ms = round((time.time() - self.start_time) * 1000, 2)
        
        if exc_type:
            # Log exceptions with the error level
            log_with_context('error', 
                            f"{self.operation_name} failed after {duration_ms}ms: {exc_val}",
                            duration_ms=duration_ms,
                            exception_type=exc_type.__name__,
                            exception=str(exc_val),
                            **self.extra_context)
        else:
            # Log successful completion
            log_with_context(self.log_level, 
                            f"{self.operation_name} completed in {duration_ms}ms",
                            duration_ms=duration_ms,
                            **self.extra_context)