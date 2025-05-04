"""Feature flags for controlling access to new features

This module provides a simple feature flag system to enable or disable features
based on configuration. This helps with gradual rollout of new functionality.
"""
import os
import logging

logger = logging.getLogger(__name__)

# Define feature flags with default values
FEATURE_FLAGS = {
    'QUOTATION_IMPORT': os.environ.get('FEATURE_QUOTE_IMPORT', 'false').lower() == 'true',
}

def is_feature_enabled(feature_name):
    """
    Check if a feature is enabled
    
    Args:
        feature_name: Name of the feature to check
        
    Returns:
        bool: True if the feature is enabled, False otherwise
    """
    if feature_name not in FEATURE_FLAGS:
        logger.warning(f"Checking for unknown feature flag: {feature_name}")
        return False
        
    return FEATURE_FLAGS.get(feature_name, False)

def enable_feature(feature_name):
    """
    Enable a feature (for testing or dynamic enabling)
    
    Args:
        feature_name: Name of the feature to enable
        
    Returns:
        bool: True if successful, False if feature doesn't exist
    """
    if feature_name not in FEATURE_FLAGS:
        logger.warning(f"Attempting to enable unknown feature flag: {feature_name}")
        return False
        
    FEATURE_FLAGS[feature_name] = True
    return True

def disable_feature(feature_name):
    """
    Disable a feature
    
    Args:
        feature_name: Name of the feature to disable
        
    Returns:
        bool: True if successful, False if feature doesn't exist
    """
    if feature_name not in FEATURE_FLAGS:
        logger.warning(f"Attempting to disable unknown feature flag: {feature_name}")
        return False
        
    FEATURE_FLAGS[feature_name] = False
    return True
