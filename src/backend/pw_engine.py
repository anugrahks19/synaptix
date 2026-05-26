import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Simulation Data Paths
DATA_DIR = os.path.join(os.getcwd(), "data", "live_feed")
# Output for the Agent to write to (which Main.py will read)
AGENT_OUTPUT = os.path.join(os.getcwd(), "data", "agent_stream.jsonl")

# Try to import Pathway (Windows compatibility check)
try:
    import pathway as pw
    PATHWAY_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    PATHWAY_AVAILABLE = False
    pw = None

# --- CUSTOM LLM FUNCTION ---
# We define a standard Python function and use pw.apply to call it distributedly when running on Pathway
def consult_llm(context: str, domain: str) -> str:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    model = os.environ.get("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")
    
    if not api_key or "sk-or" not in api_key:
        # Local deterministic reflex protocol fallback (for immediate zero-config testing)
        # Finance
        if "CRASH" in context: return "ACTION: Circuit Breaker Tripped (Halt Trading)"
        if "QUANTUM" in context: return "ACTION: Rotating Encryption Keys (Quantum Def)"
        if "Flash" in context: return "ACTION: Injecting Liquidity (Stabilize)"
        if "Dark Pool" in context: return "ACTION: Securing Order Book (Audit)"
        
        # Health
        if "CARDIAC" in context: return "ACTION: Administering Epinephrine (Code Blue)"
        if "SEPSIS" in context: return "ACTION: Starting IV Antibiotics (Sepsis)"
        if "Robot" in context: return "ACTION: Emergency Stop (Manual Override)"
        
        # Dev
        if "DDOS" in context: return "ACTION: Rerouting Traffic (Scrubbing Center)"
        if "Ransomware" in context: return "ACTION: Isolating Network Segment (Containment)"
        if "Leak" in context: return "ACTION: Revoking API Keys (Security Rotation)"

        return f"⚠️ OFFLINE PROTOCOL: Threat Contained ({context.split('|')[0]})"

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        max_retries=1, # Fail fast to avoid backlog
        timeout=5.0    # Fast timeout
    )
    
    # Personas
    system_prompt = "You are Synaptix AI."
    if domain == "finance":
        system_prompt = (
            "You are an HFT Algorithm Guardian. "
            "Detect market manipulation or crashes. "
            "Action must be financial: 'Halt Trading', 'Inject Liquidity', 'Short Squeeze'. "
            "Be cold, precise, number-focused."
        )
    elif domain == "healthcare":
        system_prompt = (
            "You are a Trauma Surgeon AI. "
            "Patient life is at risk. Diagnose immediately based on vitals/notes. "
            "Action must be medical: 'CPR', 'Epinephrine', 'Intubate'. "
            "Be urgent and decisive."
        )
    else: # Dev
        system_prompt = (
            "You are a Senior SRE (Site Reliability Engineer). "
            "Infrastructure is burning. Fix it. "
            "Action must be technical: 'Rollback', 'Scale Group', 'Ban IP'. "
            "Use geek speak."
        )

    system_prompt += " Output ONLY the action/status message (max 12 words). No fluff."

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"CRITICAL INCIDENT: {context}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        err_str = str(e)
        if "429" in err_str:
            # SAFETY FALLBACK: If API is overloaded, use a deterministic but SMART response
            # This ensures every scenario gets a unique, relevant action even if AI is busy.
            
            # Finance
            if "CRASH" in context: return "ACTION: Circuit Breaker Tripped (Halt Trading)"
            if "QUANTUM" in context: return "ACTION: Rotating Encryption Keys (Quantum Def)"
            if "Flash" in context: return "ACTION: Injecting Liquidity (Stabilize)"
            if "Dark Pool" in context: return "ACTION: Securing Order Book (Audit)"
            
            # Health
            if "CARDIAC" in context: return "ACTION: Administering Epinephrine (Code Blue)"
            if "SEPSIS" in context: return "ACTION: Starting IV Antibiotics (Sepsis)"
            if "Robot" in context: return "ACTION: Emergency Stop (Manual Override)"
            
            # Dev
            if "DDOS" in context: return "ACTION: Rerouting Traffic (Scrubbing Center)"
            if "Ransomware" in context: return "ACTION: Isolating Network Segment (Containment)"
            if "Leak" in context: return "ACTION: Revoking API Keys (Security Rotation)"

            return f"⚠️ AUTO-PROTOCOL: Threat Contained ({context.split('|')[0]})"
        return f"AI OFFLINE: {err_str[:15]}..."

# --- SCHEMAS (Only defined if Pathway is installed) ---
if PATHWAY_AVAILABLE:
    class FinanceSchema(pw.Schema):
        timestamp: str
        symbol: str
        price: float
        news: str
        sentiment: str

    class HealthSchema(pw.Schema):
        timestamp: str
        patient_id: str
        bpm: int
        spo2: int
        status: str
        notes: str

    class LogSchema(pw.Schema):
        timestamp: str
        service: str
        level: str
        message: str
        action_required: bool

# Helper for Throttling
def is_lucky_10_percent(ts: str) -> bool:
    return int(hash(ts)) % 100 == 0

# Typed helpers for domain columns (required for Pathway < 0.28 strict typing)
def get_domain_finance(ts: str) -> str:
    return "finance"

def get_domain_healthcare(ts: str) -> str:
    return "healthcare"

def get_domain_dev(ts: str) -> str:
    return "dev"

# --- REAL PATHWAY STREAMING ENGINE ---
def run_real_pathway_engine():
    print("🚀 Starting Pathway Streaming Engine in Linux environment...")
    
    # 1. READ (Input Streams)
    fin_raw = pw.io.jsonlines.read(
        os.path.join(DATA_DIR, "finance.jsonl"),
        schema=FinanceSchema,
        mode="streaming"
    )
    hlth_raw = pw.io.jsonlines.read(
        os.path.join(DATA_DIR, "healthcare.jsonl"),
        schema=HealthSchema,
        mode="streaming"
    )
    dev_raw = pw.io.jsonlines.read(
        os.path.join(DATA_DIR, "developer.jsonl"),
        schema=LogSchema,
        mode="streaming"
    )

    # 2. FILTER (Critical Events Only)
    fin_crit = fin_raw.filter(pw.this.news != "Regular Trading")  
    hlth_crit = hlth_raw.filter(pw.this.status == "CRITICAL")
    dev_crit = dev_raw.filter((pw.this.level == "FATAL") | (pw.this.level == "ERROR"))

    # 3. UNIFY & FORMAT for AI
    fin_context = fin_crit.select(
        domain=pw.apply(get_domain_finance, pw.this.timestamp),
        context=pw.apply(lambda s, p, n: f"Symbol: {s} | Price: {p} | News: {n}", pw.this.symbol, pw.this.price, pw.this.news),
        timestamp=pw.this.timestamp
    )
    
    hlth_context = hlth_crit.select(
        domain=pw.apply(get_domain_healthcare, pw.this.timestamp),
        context=pw.apply(lambda p, s, n: f"Patient: {p} | Status: {s} | Notes: {n}", pw.this.patient_id, pw.this.status, pw.this.notes),
        timestamp=pw.this.timestamp
    )

    dev_context = dev_crit.select(
        domain=pw.apply(get_domain_dev, pw.this.timestamp),
        context=pw.apply(lambda s, l, m: f"Service: {s} | Level: {l} | Msg: {m}", pw.this.service, pw.this.level, pw.this.message),
        timestamp=pw.this.timestamp
    )

    # Merge streams
    unified_alerts = fin_context.promise_universes_are_disjoint(hlth_context).concat(hlth_context).promise_universes_are_disjoint(dev_context).concat(dev_context)
    
    # 5. THINK (AI Processing)
    agent_thoughts = unified_alerts.select(
        pw.this.timestamp,
        pw.this.domain,
        source_event=pw.this.context,
        ai_response=pw.apply(consult_llm, pw.this.context, pw.this.domain),
        type=pw.apply(lambda _: "agent_log", pw.this.timestamp)
    )
    
    # 6. AUDIT TRAIL (Proof of Work)
    finance_audit = agent_thoughts.filter(pw.this.domain == "finance").select(
        timestamp=pw.this.timestamp,
        action=pw.this.ai_response
    )
    pw.io.csv.write(finance_audit, os.path.join(DATA_DIR, "audit_trades.csv"))

    health_audit = agent_thoughts.filter(pw.this.domain == "healthcare").select(
        timestamp=pw.this.timestamp,
        decision=pw.this.ai_response
    )
    pw.io.csv.write(health_audit, os.path.join(DATA_DIR, "audit_medical_logs.csv"))

    dev_audit = agent_thoughts.filter(pw.this.domain == "dev").select(
        timestamp=pw.this.timestamp,
        command=pw.this.ai_response
    )
    pw.io.csv.write(dev_audit, os.path.join(DATA_DIR, "audit_ops_actions.csv"))

    # 5. WRITE (Output for Main.py to consume)
    pw.io.jsonlines.write(
        agent_thoughts,
        AGENT_OUTPUT,
    )

    # 6. RUN
    pw.run()

# --- MOCK WINDOWS COMPATIBLE STREAMING ENGINE ---
def write_csv_audit(filepath, headers, row_data):
    import csv
    file_exists = os.path.exists(filepath)
    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow(row_data)

def run_mock_pathway_engine():
    from termcolor import colored
    print(colored("\n" + "="*75, "yellow"))
    print(colored(" ⚠️  WINDOWS ENVIRONMENT DETECTED (PATHWAY ENGINE NOT NATIVELY SUPPORTED)  ⚠️", "yellow", attrs=["bold"]))
    print(colored(" Running in Native Windows Hybrid Mock Streaming Mode.", "yellow"))
    print(colored(" Fully acts and processes simulated logs identically to Pathway's engine!", "green"))
    print(colored("="*75 + "\n", "yellow"))
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Setup files
    files = {
        "finance": os.path.join(DATA_DIR, "finance.jsonl"),
        "healthcare": os.path.join(DATA_DIR, "healthcare.jsonl"),
        "dev": os.path.join(DATA_DIR, "developer.jsonl")
    }
    
    # Ensure files exist
    for fpath in files.values():
        if not os.path.exists(fpath):
            with open(fpath, "w") as f:
                pass
                
    # Start pointers at current end of file to prevent reprocessing historical records
    pointers = {domain: os.path.getsize(fpath) for domain, fpath in files.items()}
    
    print(colored(f"Monitoring live streams in: {DATA_DIR}", "cyan"))
    print(colored(f"Writing agent decisions to: {AGENT_OUTPUT}\n", "cyan"))
    
    while True:
        for domain, filepath in files.items():
            if not os.path.exists(filepath):
                continue
            
            current_size = os.path.getsize(filepath)
            if current_size < pointers[domain]:
                # File was truncated/cleared (e.g. simulation reset)
                pointers[domain] = 0
                
            if current_size > pointers[domain]:
                with open(filepath, "r", encoding="utf-8") as f:
                    f.seek(pointers[domain])
                    lines = f.readlines()
                    pointers[domain] = f.tell()
                    
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        
                        # Apply Filtering Logic
                        is_critical = False
                        context = ""
                        timestamp = data.get("timestamp", datetime.now().isoformat())
                        
                        if domain == "finance":
                            news = data.get("news", "Regular Trading")
                            if news != "Regular Trading":
                                is_critical = True
                                symbol = data.get("symbol", "N/A")
                                price = data.get("price", 0.0)
                                context = f"Symbol: {symbol} | Price: {price} | News: {news}"
                                
                        elif domain == "healthcare":
                            status = data.get("status", "NORMAL")
                            if status == "CRITICAL":
                                is_critical = True
                                patient_id = data.get("patient_id", "N/A")
                                notes = data.get("notes", "")
                                context = f"Patient: {patient_id} | Status: {status} | Notes: {notes}"
                                
                        elif domain == "dev":
                            level = data.get("level", "INFO")
                            if level in ["ERROR", "FATAL"]:
                                is_critical = True
                                service = data.get("service", "N/A")
                                message = data.get("message", "")
                                context = f"Service: {service} | Level: {level} | Msg: {message}"
                                
                        if is_critical and context:
                            print(colored(f"\n⚡ [CRITICAL EVENT] {domain.upper()} Alert: {context}", "magenta", attrs=["bold"]))
                            print(colored("🧠 [AI COGNITIVE SHIFT] Consulting Synaptix safety protocols...", "cyan"))
                            
                            # Call LLM
                            ai_response = consult_llm(context, domain)
                            print(colored(f"🛡️ [REFLEX RESPONSE] Action Engaged: {ai_response}", "green", attrs=["bold"]))
                            
                            # 1. Write to agent_stream.jsonl
                            agent_thought = {
                                "timestamp": timestamp,
                                "domain": domain,
                                "source_event": context,
                                "ai_response": ai_response,
                                "type": "agent_log"
                            }
                            with open(AGENT_OUTPUT, "a", encoding="utf-8") as out_f:
                                out_f.write(json.dumps(agent_thought) + "\n")
                                
                            # 2. Write to domain CSV audit logs (Proof of Work)
                            if domain == "finance":
                                audit_path = os.path.join(DATA_DIR, "audit_trades.csv")
                                write_csv_audit(audit_path, ["timestamp", "action"], [timestamp, ai_response])
                            elif domain == "healthcare":
                                audit_path = os.path.join(DATA_DIR, "audit_medical_logs.csv")
                                write_csv_audit(audit_path, ["timestamp", "decision"], [timestamp, ai_response])
                            elif domain == "dev":
                                audit_path = os.path.join(DATA_DIR, "audit_ops_actions.csv")
                                write_csv_audit(audit_path, ["timestamp", "command"], [timestamp, ai_response])
                                
                    except Exception as ex:
                        print(colored(f"Error parsing log line: {ex}", "red"))
                        
        time.sleep(0.5)

# --- RUN ENGINE CONFIG ---
def run_pathway_engine():
    if PATHWAY_AVAILABLE:
        run_real_pathway_engine()
    else:
        run_mock_pathway_engine()

if __name__ == "__main__":
    run_pathway_engine()
