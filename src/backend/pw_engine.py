import pathway as pw
from pathway.stdlib.ml.index import KNNIndex
import os
from dotenv import load_dotenv

load_dotenv()

# Simulation Data Paths
DATA_DIR = "d:/GITHUB/synaptix/data/live_feed"

# define schemas
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

def run_pathway_engine():
    # 1. Input Connectors (Streaming)
    finance_table = pw.io.jsonlines.read(
        os.path.join(DATA_DIR, "finance.jsonl"),
        schema=FinanceSchema,
        mode="streaming"
    )
    
    health_table = pw.io.jsonlines.read(
        os.path.join(DATA_DIR, "healthcare.jsonl"),
        schema=HealthSchema,
        mode="streaming"
    )

    dev_table = pw.io.jsonlines.read(
        os.path.join(DATA_DIR, "developer.jsonl"),
        schema=LogSchema,
        mode="streaming"
    )

    # 2. Real-time Analysis (Simple Filtering/Aggregation)
    # Filter for Critical Health alerts
    critical_health = health_table.filter(health_table.status == "CRITICAL")
    
    # Filter for Dev Errors
    critical_logs = dev_table.filter(dev_table.level == "ERROR")

    # 3. Output - For this hackathon, we write to a 'latest_alerts.jsonl' 
    # that FastAPI can watch, OR we can just print to stdout for debug.
    # In a real app, we'd serve this via pw.io.http.server or push to a DB.
    
    # We will output a unified "Alert Stream" for the UI
    health_alerts = critical_health.select(
        type=pw.apply.lambda_("health"),
        message=pw.this.notes,
        severity=pw.this.status,
        timestamp=pw.this.timestamp
    )

    log_alerts = critical_logs.select(
        type=pw.apply.lambda_("dev"),
        message=pw.this.message,
        severity=pw.this.level,
        timestamp=pw.this.timestamp
    )

    # Union the streams
    all_alerts = health_alerts.concat(log_alerts)

    # Write to a file that FastAPI can read (simulating a DB)
    pw.io.jsonlines.write(all_alerts, "d:/GITHUB/synaptix/data/output_stream.jsonl")

    # Run the pipeline
    pw.run()

if __name__ == "__main__":
    run_pathway_engine()
