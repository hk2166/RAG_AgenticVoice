#!/bin/bash

# Navigate to project root
cd "$(dirname "$0")"

# Activate Python 3.10 virtual environment
source venv/bin/activate

# Verify Python version
echo "Using Python version:"
python --version

# Navigate to backend
cd backend

# Start the server
echo "Starting server..."
uvicorn app.main:app --reload
