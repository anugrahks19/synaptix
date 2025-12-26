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

@app.post("/trigger-event")
async def trigger_event(req: TriggerRequest):
    base_dir = os.getcwd()
    config_path = os.path.join(base_dir, "data", "sim_config.json")
    
    # 1. Enable Chaos in Sim Engine
    with open(config_path, "w") as f:
        json.dump({
            "mode": "CHAOS", 
            "onset": datetime.now().timestamp() # Track when chaos started
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
            {"symbol": "YOLO-SHORT", "price": 4.20, "delta": -69.00, "news": "Hedge Fund Liquidation"}
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
            {"pid": "TRAUMA-1", "notes": "HEMORRHAGE ALERT", "bpm": 160}
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
            {"msg": "UNAUTHORIZED ROOT ACCESS ATTEMPT", "svc": "AUTH-GATEWAY"}
        ]
        scen = random.choice(scenarios)
        payload = {
            "timestamp": timestamp, "type": "syslog", "service": scen["svc"],
            "level": "FATAL", "message": scen["msg"], "action_required": True
        }

    else:
        return {"status": "error", "message": "Invalid domain"}

    # Write to file (Pathway will pick this up instantly)
    with open(files[req.domain], "a") as f:
        f.write(json.dumps(payload) + "\n")

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
                
            with open(filepath, 'r') as f:
                f.seek(file_pointers[domain])
                new_lines = f.readlines()
                file_pointers[domain] = f.tell()

                if new_lines:
                    changes_found = True
                    for line in new_lines:
                        try:
                            payload = json.loads(line)
                            payload["domain"] = domain  # Tag with domain
                            # Send to frontend
                            await manager.broadcast(json.dumps({
                                "type": "data_update",
                                "data": payload
                            }))
                        except:
                            continue
        
        await asyncio.sleep(0.5)

# Agent Watchdog: The "Agentic" part that fixes problems
async def agent_watchdog():
    base_dir = os.getcwd()
    data_dir = os.path.join(base_dir, "data", "live_feed")
    files = {
        "finance": os.path.join(data_dir, "finance.jsonl"),
        "healthcare": os.path.join(data_dir, "healthcare.jsonl"),
        "dev": os.path.join(data_dir, "developer.jsonl")
    }
    # We use independent file pointers to track what the Agent has "seen"
    agent_pointers = {k: 0 for k in files}

    # Initialize pointers to end of file to avoid reacting to old logs
    for domain, filepath in files.items():
        if os.path.exists(filepath):
            agent_pointers[domain] = os.path.getsize(filepath)

    while True:
        for domain, filepath in files.items():
            if not os.path.exists(filepath):
                continue
            
            # Check for new lines
            current_size = os.path.getsize(filepath)
            if current_size > agent_pointers[domain]:
                with open(filepath, 'r') as f:
                    f.seek(agent_pointers[domain])
                    new_lines = f.readlines()
                    agent_pointers[domain] = f.tell()

                for line in new_lines:
                    try:
                        record = json.loads(line)
                        # Reactive Logic
                        if domain == "dev" and record.get("level") == "FATAL":
                            # Context Aware Fix
                            asyncio.create_task(mitigate_dev_failure(filepath, record.get("service"), record.get("message")))
                        
                        elif domain == "healthcare" and record.get("status") == "CRITICAL":
                            asyncio.create_task(mitigate_health_crisis(filepath, record.get("patient_id"), record.get("notes")))
                            
                        elif domain == "finance" and record.get("price") == 0.0:
                            asyncio.create_task(mitigate_market_crash(filepath))

                    except:
                        pass
        
        await asyncio.sleep(1)

async def mitigate_dev_failure(filepath, service, error_msg):
    await asyncio.sleep(3) # Agent Analysis Time
    timestamp = datetime.now().isoformat()
    
    # Specific Fixes for Specific Problems
    fix_action = "Restarted Service"
    if "Memory Leak" in error_msg: fix_action = "Garbage Collection Triggered & Memory Freed"
    elif "Database" in error_msg: fix_action = "Rolled Back Transaction & Restored Consistency"
    elif "Unauthorized" in error_msg: fix_action = "IP Blocked & Session Terminated"
    elif "Deadlock" in error_msg: fix_action = "Concurrency Limits Adjusted"

    recovery_payload = {
        "timestamp": timestamp,
        "type": "syslog",
        "service": service,
        "level": "INFO",
        "message": f"SENTINEL AGENT: {fix_action}. Stability restored.",
        "action_required": False
    }
    with open(filepath, "a") as f:
        f.write(json.dumps(recovery_payload) + "\n")

async def mitigate_health_crisis(filepath, patient_id, condition):
    await asyncio.sleep(3)
    timestamp = datetime.now().isoformat()
    
    # Specific Medical Interventions
    treatment = "Administered Stabilization Protocol"
    if "Cardiac" in condition: treatment = "Defibrillator Discharged - Sinus Rhythm Restored"
    elif "Hypoxia" in condition: treatment = "Increased O2 Flow to 100% - Saturation Rising"
    elif "Seizure" in condition: treatment = "Administered Diazepam - Seizure Ceased"
    elif "Tachycardia" in condition: treatment = "Administered Beta Blockers - Heart Rate Normalized"

    recovery_payload = {
        "timestamp": timestamp,
        "type": "vitals",
        "patient_id": patient_id,
        "bpm": 80,
        "spo2": 98,
        "status": "STABLE",
        "notes": f"SENTINEL AGENT: {treatment}."
    }
    with open(filepath, "a") as f:
        f.write(json.dumps(recovery_payload) + "\n")

async def mitigate_market_crash(filepath):
    await asyncio.sleep(3)
    timestamp = datetime.now().isoformat()
    recovery_payload = {
        "timestamp": timestamp,
        "type": "market_tick",
        "symbol": "CIRCUIT-BREAKER",
        "price": 1000.00,
        "delta": 0.0,
        "news": "SENTINEL AGENT: Trading Halted. Liquidity Injection Executed.",
        "sentiment": "neutral"
    }
    with open(filepath, "a") as f:
        f.write(json.dumps(recovery_payload) + "\n")

@app.on_event("startup")
async def startup_event():
    # Start the background streamer
    asyncio.create_task(stream_live_data())
    # Start the Agent Watchdog
    asyncio.create_task(agent_watchdog())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
