#!/bin/bash

# 1. Create Data Directories
mkdir -p data/live_feed

# 2. Start the Simulation Engine in the Background
# We use & to run it as a background process
echo "Starting Simulation Engine..."
python src/generators/sim_engine.py &

# 3. Start the FastAPI Backend
# This must be the foreground process for the container
echo "Starting Synaptix Backend..."
# Use default port 8000 if PORT env var is not set
PORT=${PORT:-8000}
uvicorn src.backend.main:app --host 0.0.0.0 --port $PORT
