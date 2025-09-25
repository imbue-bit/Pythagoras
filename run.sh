#!/bin/bash

# Set the PYTHONPATH to include the project root
export PYTHONPATH=$(pwd)

# Activate virtual environment if you have one
# source venv/bin/activate

echo "Starting Pythagoras server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
