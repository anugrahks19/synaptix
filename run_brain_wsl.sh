#!/bin/bash

# 1. Install Dependencies
# We use python3 explicitly. 
# If venv fails (common on WSL without sudo), we fall back to user install (which seemed to work for you).
echo "📦 Installing dependencies..."
python3 -m pip install -r requirements.txt

# 2. Run the Brain
echo "🧠 Starting Synaptix Neural Engine (Pathway+OpenRouter)..."
# Use python3 explicitly as 'python' is often missing in Ubuntu/WSL defaults
python3 src/backend/pw_engine.py
