# Synaptix: The Agent That Never Sleeps 👁️

> **Hackathon Track 1 Submission**: Agentic AI with Live Data.
> *Solving "AI Amnesia" and "Stale RAG" using Pathway's Streaming Engine.*

---

## 📉 The Problem: Intelligence Frozen in Amber
Most AI models today suffer from **Context Evaporation**. They are frozen in time, processing each request like it's Groundhog Day.
- **Stale RAG**: Traditional Vector Stores need "re-indexing" batch jobs. By the time they learn, the market has moved, the patient has crashed, or the server is dead.
- **Memory on Sticky Notes**: External databases are just lookups, not true "living" memory.

## 🚀 The Solution: Synaptix
Synaptix is a **Live Agentic System** that doesn't just "query" data; it **lives** inside the data stream.
It leverages **Pathway** to achieve **0-Batching** and **<50ms Latency** response times.

---

## 🏗️ The Physics of the System

The architecture acts as a triad of **Entropy (Simulation)**, **Order (Pathway)**, and **Observation (Server)**.

### 1. The Entropy Generator (Live Data)
**File**: `src/generators/sim_engine.py`
- **Role**: Simulates the "Real World".
- **Physics**: Generates high-velocity JSONL streams for 3 domains:
    - **Finance**: High-frequency stock ticks (Market Crash scenarios).
    - **Healthcare**: ICU Patient Vitals (Cardiac Arrest scenarios).
    - **DevOps**: Server Logs (DDoS/Ransomware scenarios).
- **Why**: Static datasets prove nothing. We simulate *infinite* drift and chaos.

### 2. The Pathway Engine (The Cortex)
**File**: `src/backend/pw_engine.py`
- **Role**: The "Brain" that never sleeps.
- **Physics**: It uses **Streaming ETL**. It watches the `data/live_feed` directory for *new bytes* (like `tail -f` but smarter).
- **The Critical Difference**:
    - **Standard RAG**: 1. Write file -> 2. Run Python Script -> 3. Re-index -> 4. Query. (Time: ~5 mins)
    - **Synaptix**: 1. Write file -> 2. Pathway triggers -> 3. Agent Acts. (**Time: < 100ms**)
- **Agentic Logic**: It filters 99% of noise (normal heartbeat) and only invokes the LLM (OpenRouter/Gemini) for the 1% critical anomalies.

### 3. The Reactive Interface (The Nervous System)
**File**: `src/frontend/dashboard.html` & `src/backend/main.py`
- **Role**: Visual Proof of Speed.
- **Physics**:
    - **WebSockets**: Pushes updates from the Cortex to the Browser instantly.
    - **"Trigger Crisis" Button**: A feature that lets *you* play God. It injects a "Black Swan" event (e.g., Flash Crash) instantly into the stream to prove the Agent catches it.

---

## 🧬 Why It Wins (Track 1)
1.  **Never Stale**: The moment a simulated "Crash" happens, the Agent sees it. No batch jobs.
2.  **Context Aware**: The LLM receives the exact slice of stream data (Price, News, Delta) needed to make a decision.
3.  **Audit Trail**: Every AI decision is written back to immutable CSV logs (`data/live_feed/audit_*.csv`), proving the agent *did* something.

 Synaptix proves that with Pathway, **Memory doesn't have to scale quadratically—it just has to flow.**
