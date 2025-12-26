# Synaptix Run Guide 🚀

## Prerequisites
- Python 3.10+
- A modern browser (Chrome/Edge/Firefox)

## Step 1: Install Dependencies
Open a terminal in `d:/GITHUB/synaptix` and run:
```bash
pip install -r requirements.txt
```

## Step 2: Ignite the Data Engine 🔥
This script simulates real-time stock ticks, patient vitals, and server logs.
**Open Terminal A:**
```bash
python src/generators/sim_engine.py
```
*You should see colored logs streaming in the terminal.*

## Step 3: Launch the Neural Core 🧠
This starts the Web Server and the Agent.
**Open Terminal B:**
```bash
python src/backend/main.py
```
*It will start the server at http://0.0.0.0:8000*

## Step 4: Experience the Frontend ✨
1. Open your browser and go to: **[http://localhost:8000](http://localhost:8000)**
2. You will see the **Finance Dashboard** by default.
3. **Click the Sidebar Tabs** to morph the UI:
   - **Healthcare**: Theme turns Cyan, data shifts to Patient Vitals.
   - **DevTools**: Theme turns Neon Red, data shifts to Server Logs.
4. **Watch the "Agent"**: When a simulated "CRITICAL" event happens (Red text in Terminal A), the Agent on the right sidebar will wake up and "Perform Analysis".
