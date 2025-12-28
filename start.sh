#!/bin/bash

# 1. Start Simulation (Background)
echo "Starting Simulation Engine..."
python src/generators/sim_engine.py &

# 2. Start Pathway Engine (Background)
echo "Starting Pathway Engine..."
python src/backend/pw_engine.py &

# 3. Start API Server (Foreground)
# This keeps the container alive
echo "Starting Synaptix API..."
python src/backend/main.py
