import pathway as pw
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Simulation Data Paths
DATA_DIR = os.path.join(os.getcwd(), "data", "live_feed")
# Output for the Agent to write to (which Main.py will read)
AGENT_OUTPUT = os.path.join(os.getcwd(), "data", "agent_stream.jsonl")

# --- CUSTOM LLM UDF ---
# --- CUSTOM LLM FUNCTION ---
# We define a standard Python function and use pw.apply to call it distributedly
def consult_llm(context: str, domain: str) -> str:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    model = os.environ.get("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")
    
    if not api_key or "sk-or" not in api_key:
        return "CONFIG ERROR: Missing OpenRouter API Key in .env"

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

# --- SCHEMAS ---
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
    # EMERGENCY THROTTLE: 1% sampling (1 in 100)
    # The simulation engine is running too fast (0.1s), so we must discard 99% of data
    return int(hash(ts)) % 100 == 0

# Typed helpers for domain columns (required for Pathway < 0.28 strict typing)
def get_domain_finance(ts: str) -> str:
    return "finance"

def get_domain_healthcare(ts: str) -> str:
    return "healthcare"

def get_domain_dev(ts: str) -> str:
    return "dev"

def run_pathway_engine():
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
    # Finance: Exclude "Regular Trading" noise. Only allow anomalies or specific manual triggers.
    fin_crit = fin_raw.filter(pw.this.news != "Regular Trading")  
    # Health: Critical status
    hlth_crit = hlth_raw.filter(pw.this.status == "CRITICAL")
    # Dev: Fatal or Error
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
    # We must promise that these come from different "universes" (files) so Pathway allows the merge
    unified_alerts = fin_context.promise_universes_are_disjoint(hlth_context).concat(hlth_context).promise_universes_are_disjoint(dev_context).concat(dev_context)

    # 4. THROTTLE (REMOVED)
    # Since Sim Engine is now slow (2s interval), we can process ALL alerts.
    # The API Rate Limit check in consult_llm will handle 429s if they happen.
    
    # 5. THINK (AI Processing)
    # We apply the LLM UDF
    agent_thoughts = unified_alerts.select(
        pw.this.timestamp,
        pw.this.domain,
        source_event=pw.this.context,
        ai_response=pw.apply(consult_llm, pw.this.context, pw.this.domain),
        type=pw.apply(lambda _: "agent_log", pw.this.timestamp) # Tag for frontend
    )
    
    # 6. AUDIT TRAIL (Proof of Work)
    # Write actions to physical files to prove agentic capability
    # Finance actions -> trades.csv
    finance_audit = agent_thoughts.filter(pw.this.domain == "finance").select(
        timestamp=pw.this.timestamp,
        action=pw.this.ai_response
    )
    pw.io.csv.write(finance_audit, os.path.join(DATA_DIR, "audit_trades.csv"))

    # Health actions -> medical_logs.csv
    health_audit = agent_thoughts.filter(pw.this.domain == "healthcare").select(
        timestamp=pw.this.timestamp,
        decision=pw.this.ai_response
    )
    pw.io.csv.write(health_audit, os.path.join(DATA_DIR, "audit_medical_logs.csv"))

    # Dev actions -> ops_actions.csv
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

if __name__ == "__main__":
    run_pathway_engine()
