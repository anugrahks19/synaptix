from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import json
import os
from typing import List
from datetime import datetime

app = FastAPI()

# Mount frontend
app.mount("/static", StaticFiles(directory=os.path.join(os.getcwd(), "src", "frontend")), name="static")

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# Trigger Model
from pydantic import BaseModel
class TriggerRequest(BaseModel):
    domain: str

class UpdateRulesRequest(BaseModel):
    type: str # 'finance', 'health', 'dev'
    max_bpm: int = 140
    max_drawdown: int = 10
    max_latency: int = 2000

@app.post("/update-rules")
async def update_rules(req: UpdateRulesRequest):
    config_path = os.path.join(os.getcwd(), "data", "sim_config.json")
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except:
        config = {"mode": "CHAOS", "onset": 0, "rules": {}}

    # Initialize rules if missing
    if "rules" not in config: config["rules"] = {}

    # Update Logic
    if req.type == "health": config["rules"]["max_bpm"] = req.max_bpm
    elif req.type == "finance": config["rules"]["max_drawdown"] = req.max_drawdown
    elif req.type == "dev": config["rules"]["max_latency"] = req.max_latency
    
    with open(config_path, "w") as f:
        json.dump(config, f)
    
    return {"status": "updated", "config": config["rules"]}

@app.get("/dashboard")
async def get_dashboard():
    return FileResponse(os.path.join(os.getcwd(), "src", "frontend", "dashboard.html"))

@app.get("/network")
async def get_network():
    return FileResponse(os.path.join(os.getcwd(), "src", "frontend", "network.html"))

@app.get("/forensics")
async def get_forensics():
    return FileResponse(os.path.join(os.getcwd(), "src", "frontend", "forensics.html"))

@app.post("/trigger-event")
async def trigger_event(req: TriggerRequest):
    # Normalize domain names (Handle case sensitivity and aliases)
    d = req.domain.lower()
    if d == "health" or d == "healthcare": req.domain = "healthcare"
    elif d == "finance": req.domain = "finance"
    elif d == "dev" or "dev" in d: req.domain = "dev" # Handles 'DevTools', 'developer', etc.
    
    base_dir = os.getcwd()
    config_path = os.path.join(base_dir, "data", "sim_config.json")
    
    # 1. DO NOT ENABLE CHAOS LOOP
    # User requested: "dont makeit inject automatically only inject crisis when user taps the button"
    # So we just write the ONE event to the file, but keep config STABLE
    with open(config_path, "w") as f:
        json.dump({
            "mode": "STABLE", 
            "onset": 0
        }, f)

    timestamp = datetime.now().isoformat()
    data_dir = os.path.join(base_dir, "data", "live_feed")
    files = {
        "finance": os.path.join(data_dir, "finance.jsonl"),
        "healthcare": os.path.join(data_dir, "healthcare.jsonl"),
        "dev": os.path.join(data_dir, "developer.jsonl")
    }
    
    # 2. Varied Scenarios
    import random
    payload = {}

    if req.domain == "finance":
        scenarios = [
            {"symbol": "CRASH", "price": 0.00, "delta": -99.99, "news": "MARKET CRASH DETECTED"},
            {"symbol": "BTC-DUMP", "price": 12000.00, "delta": -40.00, "news": "Flash Sale on Crypto"},
            {"symbol": "YOLO-SHORT", "price": 4.20, "delta": -69.00, "news": "Hedge Fund Liquidation"},
            {"symbol": "FLASH-CRASH", "price": 1400.00, "delta": -35.00, "news": "High Frequency Trading Loop Detected"},
            {"symbol": "SEC-FREEZE", "price": 0.00, "delta": 0.00, "news": "Regulatory Trading Halt - Investigation Pending"},
            {"symbol": "FX-COLLAPSE", "price": 0.85, "delta": -15.00, "news": "Currency Peg Broken - Hyperinflation Risk"},
            {"symbol": "DARK-POOL", "price": 450.20, "delta": -12.00, "news": "Suspicious Dark Pool Activity Detected"},
            {"symbol": "QUANTUM", "price": 0.00, "delta": -100.00, "news": "Encryption Keys Compromised by Quantum Actor"}
        ]
        scen = random.choice(scenarios)
        payload = {
            "timestamp": timestamp, "type": "market_tick", "symbol": scen["symbol"],
            "price": scen["price"], "delta": scen["delta"], "news": scen["news"], "sentiment": "bearish"
        }

    elif req.domain == "healthcare":
        scenarios = [
            {"pid": "EMERGENCY", "notes": "CARDIAC ARREST - CODE BLUE", "bpm": 0},
            {"pid": "ICU-04", "notes": "SPO2 FAILURE - HYPOXIA", "bpm": 45},
            {"pid": "TRAUMA-1", "notes": "HEMORRHAGE ALERT", "bpm": 160},
            {"pid": "NEURO", "notes": "Seizure Activity Detected - Status Epilepticus", "bpm": 140},
            {"pid": "ALLERGY", "notes": "Anaphylaxis - Airway Compromised", "bpm": 155},
            {"pid": "SEPSIS", "notes": "Septic Shock - BP Critical", "bpm": 135},
            {"pid": "DEVICE", "notes": "Pacemaker Signal Loss - Lead Failure", "bpm": 30},
            {"pid": "ROBOT", "notes": "Surgical Robot Latency > 500ms - Safety Stop", "bpm": 90}
        ]
        scen = random.choice(scenarios)
        payload = {
            "timestamp": timestamp, "type": "vitals", "patient_id": scen["pid"],
            "bpm": scen["bpm"], "spo2": 60, "status": "CRITICAL", "notes": scen["notes"]
        }

    elif req.domain == "dev":
        scenarios = [
            {"msg": "DATA CORRUPTION DETECTED - SYSTEM HALT", "svc": "CORE-DB"},
            {"msg": "MEMORY LEAK - OOM KILLER INVOKED", "svc": "WORKER-NODE-9"},
            {"msg": "UNAUTHORIZED ROOT ACCESS ATTEMPT", "svc": "AUTH-GATEWAY"},
            {"msg": "DDOS ATTACK - 1M RPS DETECTED", "svc": "LOAD-BALANCER"},
            {"msg": "RANSOMWARE SIGNATURE FOUND - ENCRYPTING", "svc": "FILE-SERVER"},
            {"msg": "API KEY LEAKED IN PUBLIC REPO", "svc": "GIT-WATCHDOG"},
            {"msg": "DEADLOCK DETECTED - TRANSACTION STUCK", "svc": "PAYMENT-ENGINE"},
            {"msg": "RECURSIVE LAMBDA BOMB - COST SPIKE", "svc": "SERVERLESS-FUNC"}
        ]
        scen = random.choice(scenarios)
        payload = {
            "timestamp": timestamp, "type": "syslog", "service": scen["svc"],
            "level": "FATAL", "message": scen["msg"], "action_required": True
        }

    else:
        return {"status": "error", "message": "Invalid domain"}

    # 3. INSTANT FEEDBACK (Bypass File Reader Latency)
    # Broadcast directly to UI so the user sees it immediately
    payload["domain"] = req.domain
    payload["is_manual"] = True # Tag for loop filtering
    
    # Write to file (Pathway will pick this up instantly)
    with open(files[req.domain], "a") as f:
        f.write(json.dumps(payload) + "\n")
        f.flush()
        os.fsync(f.fileno())

    await manager.broadcast(json.dumps({
        "type": "data_update",
        "data": payload
    }))

    return {"status": "success", "payload": payload}

@app.post("/stabilize")
async def stabilize_system():
    # 1. Disable Chaos
    with open("d:/GITHUB/synaptix/data/sim_config.json", "w") as f:
        json.dump({"mode": "STABLE"}, f)

    timestamp = datetime.now().isoformat()
    files = {
        "finance": "d:/GITHUB/synaptix/data/live_feed/finance.jsonl",
        "healthcare": "d:/GITHUB/synaptix/data/live_feed/healthcare.jsonl",
        "dev": "d:/GITHUB/synaptix/data/live_feed/developer.jsonl"
    }
    
    # Inject Normalcy
    payloads = [
        {"file": files["finance"], "data": {"timestamp": timestamp, "type": "market_tick", "symbol": "RECOVERY", "price": 1000.0, "delta": 5.0, "news": "Market Stabilized", "sentiment": "bullish"}},
        {"file": files["healthcare"], "data": {"timestamp": timestamp, "type": "vitals", "patient_id": "SYSTEM", "bpm": 72, "spo2": 99, "status": "NORMAL", "notes": "All Systems Normal"}},
        {"file": files["dev"], "data": {"timestamp": timestamp, "type": "syslog", "service": "SYSTEM", "level": "INFO", "message": "Manual Override: Stability Restored", "action_required": False}}
    ]

    for p in payloads:
        with open(p["file"], "a") as f:
            f.write(json.dumps(p["data"]) + "\n")

    return {"status": "stabilized"}


@app.get("/")
async def read_root():
    return FileResponse(os.path.join(os.getcwd(), "src", "frontend", "index.html"))

@app.get("/dashboard")
async def read_dashboard():
    return FileResponse(os.path.join(os.getcwd(), "src", "frontend", "dashboard.html"))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We don't expect much *input* from the client in this demo, 
            # mostly pushing updates.
            data = await websocket.receive_text()
            
            # Simple "Agent" Mock response for demo interactivity
            if "analyze" in data.lower():
                await manager.broadcast(json.dumps({
                    "type": "agent_response",
                    "content": "Analyzing latest stream... Detected 3 anomalies in the last minute. Engaging protection protocols."
                }))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Background Task to stream data from the generated files to the UI
async def stream_live_data():
    base_dir = os.getcwd()
    data_dir = os.path.join(base_dir, "data", "live_feed")
    files = {
        "finance": os.path.join(data_dir, "finance.jsonl"),
        "healthcare": os.path.join(data_dir, "healthcare.jsonl"),
        "dev": os.path.join(data_dir, "developer.jsonl")
    }
    file_pointers = {k: 0 for k in files}

    while True:
        changes_found = False
        for domain, filepath in files.items():
            if not os.path.exists(filepath):
                continue
                
            with open(filepath, 'r', encoding='utf-8') as f:
                f.seek(file_pointers[domain])
                new_lines = f.readlines()
                file_pointers[domain] = f.tell()

                if new_lines:
                    changes_found = True
                    for line in new_lines:
                        try:
                            payload = json.loads(line)
                            
                            # IDEMPOTENCY KEY: If this was a manual trigger (is_manual=True),
                            # it was already broadcasted by the POST endpoint. Do not send again.
                            if payload.get("is_manual"):
                                continue
                                
                            payload["domain"] = domain  # Tag with domain
                            # Send to frontend
                            await manager.broadcast(json.dumps({
                                "type": "data_update",
                                "data": payload
                            }))
                        except:
                            continue
        
        await asyncio.sleep(0.5)

# Real-Time Agent Streamer (Reads output from Pathway AI)
async def agent_stream_listener():
    base_dir = os.getcwd()
    agent_file = os.path.join(base_dir, "data", "agent_stream.jsonl")
    
    # Ensure file exists
    if not os.path.exists(agent_file):
        with open(agent_file, "w") as f:
            pass
            
    file_pointer = 0
    
    # Fast forward to end on startup to avoid re-playing old history
    if os.path.exists(agent_file):
        file_pointer = os.path.getsize(agent_file)

    while True:
        if os.path.exists(agent_file):
            current_size = os.path.getsize(agent_file)
            if current_size > file_pointer:
                with open(agent_file, "r", encoding="utf-8") as f:
                    f.seek(file_pointer)
                    new_lines = f.readlines()
                    file_pointer = f.tell()
                
                for line in new_lines:
                    try:
                        record = json.loads(line)
                        # Broadcast to UI
                        await manager.broadcast(json.dumps({
                            "type": "agent_response",
                            "content": record.get("ai_response", "Processing..."),
                            "raw": record
                        }))
                    except:
                        pass
        
        await asyncio.sleep(0.5)

@app.on_event("startup")
async def startup_event():
    # Start the background streamer
    asyncio.create_task(stream_live_data())
    # Start the Agent Listener (Pathway Output)
    asyncio.create_task(agent_stream_listener())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
