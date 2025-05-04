#!/bin/bash

# Deploy with Database Migrations Script
# This script demonstrates the process for safely deploying changes
# with feature flags and database migrations.

set -e  # Exit on any error

# Step 1: Apply database migrations first (non-destructive)
echo "Applying database migrations..."
python apply_migration.py

# Step 2: Keep the feature flag disabled for controlled rollout
echo "Setting feature flag to disabled by default..."
python set_feature_flag.py --disable QUOTATION_IMPORT

# Step 3: Run tests
echo "Running tests..."
# Add your test commands here, for example:
# python -m pytest tests/

# Step 4: Restart the application
echo "Restarting application..."
# Add your restart command here, for example:
# sudo systemctl restart your_service

echo "Deployment completed successfully!"
echo "To enable the feature, run: python set_feature_flag.py --enable QUOTATION_IMPORT"
