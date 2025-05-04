#!/usr/bin/env python
"""
Set or update feature flags in the environment.

This script allows for easy enabling/disabling of feature flags
without modifying code, making it useful for controlled rollout
of new features.
"""
import os
import sys
import logging
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('feature_flags')

# Known feature flags and their descriptions
FEATURE_FLAGS = {
    'QUOTATION_IMPORT': {
        'env_var': 'FEATURE_QUOTE_IMPORT',
        'description': 'Enable the Quotation Import feature for uploading and processing quotations',
        'default': 'false'
    },
    # Add more feature flags here as needed
}

def set_feature_flag(flag_name, value):
    """
    Set a feature flag in the environment
    
    Args:
        flag_name: Name of the feature flag
        value: Value to set (true/false)
        
    Returns:
        bool: True if flag was set, False otherwise
    """
    try:
        if flag_name not in FEATURE_FLAGS:
            logger.error(f"Unknown feature flag: {flag_name}")
            return False
            
        flag_info = FEATURE_FLAGS[flag_name]
        env_var = flag_info['env_var']
        
        # Set the environment variable
        os.environ[env_var] = value
        logger.info(f"Set {env_var}={value} in environment")
        
        # Also log a message about server restart
        logger.info("Note: You need to restart the server for changes to take effect")
        
        return True
    except Exception as e:
        logger.error(f"Error setting feature flag: {str(e)}")
        return False

def list_feature_flags():
    """
    List all available feature flags and their current values
    
    Returns:
        dict: Dictionary of feature flags and their values
    """
    try:
        result = {}
        
        for flag_name, flag_info in FEATURE_FLAGS.items():
            env_var = flag_info['env_var']
            current_value = os.environ.get(env_var, flag_info['default'])
            
            result[flag_name] = {
                'env_var': env_var,
                'description': flag_info['description'],
                'current_value': current_value
            }
            
        return result
    except Exception as e:
        logger.error(f"Error listing feature flags: {str(e)}")
        return {}

def main():
    """
    Command-line interface for setting feature flags
    """
    parser = argparse.ArgumentParser(description='Set or list feature flags')
    parser.add_argument('--list', action='store_true', help='List all feature flags')
    parser.add_argument('--enable', metavar='FLAG', help='Enable a feature flag')
    parser.add_argument('--disable', metavar='FLAG', help='Disable a feature flag')
    
    args = parser.parse_args()
    
    if args.list:
        flags = list_feature_flags()
        print("\nAvailable Feature Flags:\n")
        for flag_name, flag_info in flags.items():
            print(f"{flag_name} ({flag_info['env_var']})")
            print(f"  Description: {flag_info['description']}")
            print(f"  Current value: {flag_info['current_value']}")
            print()
        return 0
    elif args.enable:
        if set_feature_flag(args.enable, 'true'):
            print(f"Enabled feature flag: {args.enable}")
            return 0
        else:
            return 1
    elif args.disable:
        if set_feature_flag(args.disable, 'false'):
            print(f"Disabled feature flag: {args.disable}")
            return 0
        else:
            return 1
    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())
