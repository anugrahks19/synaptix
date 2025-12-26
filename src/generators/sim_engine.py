import time
import json
import random
import os
from datetime import datetime
from termcolor import colored

# Configuration
BASE_DIR = os.getcwd() # Run from project root
DATA_DIR = os.path.join(BASE_DIR, "data", "live_feed")
os.makedirs(DATA_DIR, exist_ok=True)

DOMAINS = {
    "finance": {
        "file": os.path.join(DATA_DIR, "finance.jsonl"),
        "symbols": ["PATH", "GOOGL", "NVDA", "MSFT", "TSLA"],
        "events": ["Earnings Beat", "FDA Approval", "CEO Scandal", "Product Launch"]
    },
    "healthcare": {
        "file": os.path.join(DATA_DIR, "healthcare.jsonl"),
        "patients": ["P-101", "P-102", "P-205", "P-999"],
        "alerts": ["Tachycardia", "Bradycardia", "Stable", "O2 Saturation Drop"]
    },
    "developer": {
        "file": os.path.join(DATA_DIR, "developer.jsonl"),
        "services": ["Auth-Service", "Payment-Gateway", "Frontend-X", "DB-Shard-01"],
        "errors": ["ConnectionRefused", "Timeout", "SegFault", "DeploySuccess"]
    }
}

# Default Rules
RULES = {
    "max_bpm": 140,
    "max_drawdown": 10, # 10% drop override
    "max_latency": 2000 # 2000ms
}

def generate_finance(force_critical=False, is_chaos=False):
    symbol = random.choice(DOMAINS["finance"]["symbols"])
    
    # 1. Base Prices
    price = round(random.uniform(100, 1500), 2)
    change = round(random.uniform(-5, 5), 2) # Normal volatility
    sentiment = "bullish" if change > 0 else "bearish"
    event = "Regular Trading"

    if is_chaos:
        # Check Rule Violation
        droppct = abs((change / price) * 100)
        rule_break = change < 0 and droppct > RULES["max_drawdown"]

        if force_critical or rule_break:
            symbol = "CRASH" if force_critical else symbol
            change = -round(random.uniform(20, 50), 2) # Crash
            event = "MARKET ANOMALY DETECTED"
            sentiment = "bearish"
    
    return {
        "timestamp": datetime.now().isoformat(),
        "type": "market_tick",
        "symbol": symbol,
        "price": price,
        "delta": change,
        "news": event,
        "sentiment": sentiment
    }

def generate_health(force_critical=False, is_chaos=False):
    patient = random.choice(DOMAINS["healthcare"]["patients"])
    
    # Defaults
    bpm = random.randint(60, 100)
    spo2 = random.randint(95, 100)
    status = "NORMAL"
    notes = "Vitals Stable"

    if is_chaos:
        # Rule Check
        # If chaos, we allow higher range for rule testing
        bpm = random.randint(60, 160) 
        rule_break = bpm > RULES["max_bpm"]

        if force_critical:
            status = "CRITICAL"
            bpm = 0 if random.random() > 0.5 else 180
            notes = "CARDIAC EVENT"
            spo2 = 70
        elif rule_break:
            status = "CRITICAL"
            notes = f"Rule Breach: BPM {bpm} > {RULES['max_bpm']}"
            spo2 = 85

    return {
        "timestamp": datetime.now().isoformat(),
        "type": "vitals",
        "patient_id": patient,
        "bpm": bpm,
        "spo2": spo2,
        "status": status,
        "notes": notes
    }

def generate_dev(force_critical=False, is_chaos=False):
    service = random.choice(DOMAINS["developer"]["services"])
    level = "INFO"
    msg = "Health Check OK"
    action = False

    if is_chaos:
        latency = random.randint(10, 3000)
        rule_break = latency > RULES["max_latency"]

        if force_critical:
            level = "FATAL"
            msg = "SYSTEM OUTAGE"
            action = True
        elif rule_break:
            level = "ERROR"
            msg = f"SLA Breach: {latency}ms"
            action = True
    
    return {
        "timestamp": datetime.now().isoformat(),
        "type": "syslog",
        "service": service,
        "level": level,
        "message": msg,
        "action_required": action
    }

def run_simulation():
    print(colored("Starting Synaptix Data Simulation Engine...", "green", attrs=["bold"]))
    print(f"Feeding data to {DATA_DIR}")
    
    # Clear old files
    for d in DOMAINS.values():
        open(d["file"], 'w').close()

    # State tracking for Crisis Timing
    events_triggered = 0
    last_event_time = time.time()
    domain_cycle = 0

    current_onset = 0
    
    # FORCE STABLE ON STARTUP
    with open("d:/GITHUB/synaptix/data/sim_config.json", "w") as f:
        json.dump({"mode": "STABLE", "onset": 0, "rules": {"max_bpm": 140, "max_drawdown": 10, "max_latency": 2000}}, f)
    print(colored("--- SYSTEM RESET: STABLE MODE ---", "cyan"))

    while True:
        # Read Config
        try:
            with open("d:/GITHUB/synaptix/data/sim_config.json", "r") as f:
                config = json.load(f)
                is_chaos = config.get("mode") == "CHAOS"
                onset = config.get("onset", 0)
                
                # Detect New Crisis Trigger
                if is_chaos and onset != current_onset:
                    current_onset = onset
                    events_triggered = 0 
                    next_chaos_time = 0
                    print(colored("--- NEW CRISIS ONSET DETECTED ---", "red"), flush=True)

        except:
            is_chaos = False
            # Defaults
            RULES["max_bpm"] = 140
            RULES["max_drawdown"] = 10
            RULES["max_latency"] = 2000

        # Timing Logic for Chaos
        should_trigger_critical = False
        
        if is_chaos:
            current_time = time.time()
            time_since_onset = current_time - current_onset
            
            # Phase 1: First 2 Events
            if events_triggered < 2:
                # Event 1: Immediate (after small buffer)
                if events_triggered == 0:
                     if time_since_onset > 0.5:
                         should_trigger_critical = True
                         next_chaos_time = current_time + 5.0 # Schedule next exactly 5s later
                
                # Event 2: Exactly 5 seconds after Event 1
                elif events_triggered == 1:
                     if current_time >= next_chaos_time:
                         should_trigger_critical = True
                         # Schedule Phase 2 start (random 2-15s)
                         next_chaos_time = current_time + random.uniform(2, 15)
            
            # Phase 2: Random Intervals (2s to 15s)
            else:
                if current_time >= next_chaos_time:
                    should_trigger_critical = True
                    # Schedule next random interval
                    delay = random.uniform(2, 15)
                    next_chaos_time = current_time + delay
                    print(colored(f"--- NEXT CRASH IN {delay:.1f}s ---", "yellow"), flush=True)
        
        # Generate Data
        row_fin = generate_finance(force_critical=should_trigger_critical, is_chaos=is_chaos)
        row_hlth = generate_health(force_critical=should_trigger_critical, is_chaos=is_chaos)
        row_dev = generate_dev(force_critical=should_trigger_critical, is_chaos=is_chaos)

        # Write and Print
        if should_trigger_critical or random.random() > 0.1:
            with open(DOMAINS["finance"]["file"], "a") as f:
                f.write(json.dumps(row_fin) + "\n")
            print(f"[FINANCE] {row_fin['symbol']} ${row_fin['price']}", flush=True)

        if should_trigger_critical or random.random() > 0.1:
            with open(DOMAINS["healthcare"]["file"], "a") as f:
                f.write(json.dumps(row_hlth) + "\n")
            color = "red" if row_hlth['status'] == "CRITICAL" else "cyan"
            print(colored(f"[HEALTH] {row_hlth['patient_id']} BPM:{row_hlth['bpm']}", color), flush=True)

        if should_trigger_critical or random.random() > 0.1:
            with open(DOMAINS["developer"]["file"], "a") as f:
                f.write(json.dumps(row_dev) + "\n")
            color = "yellow" if row_dev['level'] in ["ERROR", "FATAL"] else "blue"
            print(colored(f"[DEV] {row_dev['service']} {row_dev['level']}", color), flush=True)

        # Increment Event Counter if critical was triggered
        if should_trigger_critical:
            events_triggered += 1

        # Faster Tick Rate
        time.sleep(random.uniform(0.1, 0.8))
        domain_cycle += 1

if __name__ == "__main__":
    run_simulation()
