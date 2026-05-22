# Synaptix: The Agent That Never Sleeps 👁️

**A hackathon-ready streaming agentic AI platform** combining Pathway's zero-batching streaming engine, OpenRouter (Gemini) cognitive anomaly detection, and a high-fidelity WebSocket-driven real-time reactor dashboard.

[![Hackathon Track](https://img.shields.io/badge/Track-Agentic%20AI%20with%20Live%20Data-blueviolet?style=for-the-badge)](https://github.com/anugrahks19/synaptix)
[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge)](https://python.org)
[![Engine](https://img.shields.io/badge/Streaming-Pathway-green?style=for-the-badge)](https://pathway.com)
[![License](https://img.shields.io/badge/License-MIT-orange?style=for-the-badge)](https://opensource.org/licenses/MIT)

---

## 🎯 Overview

Most AI models are fossilized—frozen in the state of their last training run. Traditional RAG systems suffer from **"Context Evaporation"** and require periodic batch indexing jobs that take minutes to sync.

**Synaptix is Kinetic.** It doesn't just lookup data; it **lives** inside the live data stream. By leveraging **Pathway's Streaming Engine**, it achieves **0-Batching** and **<50ms processing latency** to analyze live data, detect anomalies, consult AI, and execute safety overrides in real-time.

```mermaid
graph TD
    %% Generators
    subgraph Simulation ["1. Entropy Generators (sim_engine.py)"]
        G_Fin["📈 Finance Generator"]
        G_Hlth["🏥 Healthcare Generator"]
        G_Dev["💻 DevOps Generator"]
    end

    %% Storage Streams
    subgraph Streams ["2. Continuous Streams (data/live_feed/)"]
        S_Fin[("finance.jsonl")]
        S_Hlth[("healthcare.jsonl")]
        S_Dev[("developer.jsonl")]
    end

    %% Pathway Processing
    subgraph PathwayEngine ["3. Pathway Cognitive Cortex (pw_engine.py)"]
        P_Read["pw.io.jsonlines.read(..., mode='streaming')"]
        P_Filter["Anomaly & Threshold Filter"]
        P_Merge["disjoint.concat() (Unified Stream)"]
        P_AI["consult_llm() UDF (OpenRouter Gemini)"]
    end

    %% Actions & Interface
    subgraph Actions ["4. React & Audit Layer"]
        A_Audit[("audit_*.csv Logs")]
        A_Stream[("agent_stream.jsonl")]
        A_UI["FastAPI WebSocket Server (main.py)"]
        UI_Dash["💎 Premium Glassmorphic Dashboard"]
    end

    %% Connections
    G_Fin --> S_Fin
    G_Hlth --> S_Hlth
    G_Dev --> S_Dev

    S_Fin --> P_Read
    S_Hlth --> P_Read
    S_Dev --> P_Read

    P_Read --> P_Filter
    P_Filter --> P_Merge
    P_Merge --> P_AI

    P_AI --> A_Audit
    P_AI --> A_Stream
    A_Stream --> A_UI
    A_UI <-->|WebSocket| UI_Dash

    %% Custom Trigger
    UI_Dash <-->|POST /trigger-event| A_UI
    A_UI -->|Direct JSON Inject| S_Fin & S_Hlth & S_Dev
```

### Key Features

- **⚡ Pathway 0-Batching Engine**: Monitors stream files continuously. When a single byte hits the disk, Pathway processes it instantly, dropping latency from minutes to **milliseconds**.
- **🧠 Cognitive Anomaly Detection**: Moves beyond brittle static rules. The agent understands context (e.g., *"The stock dropped 50% but it's a planned stock split - do not panic"*).
- **🛡️ Fail-Safe Safety Cortex**:Wraps the AI in an intelligent fallback system. If the LLM experiences network timeouts or API rate-limiting (429), it instantly triggers deterministic, pre-approved **"Reflex Actions"** (e.g., circuit breaker, IV administration, network isolation).
- **🎭 Polymorphic Architecture**: One brain, three domains. Seamlessly shifts between **Finance Mode** (ticks & market volatility), **Healthcare Mode** (patient ICU vitals), and **DevOps Mode** (SLA breaches & infrastructure logs).
- **🕹️ Live Control Room**: Customize alert thresholds (BPM, latency limits, drawdown percentage) or manually inject custom Black Swan events (Flash Crash, Cardiac Arrest, DDoS attack) to test system reflexes.
- **💎 Premium Glassmorphic UI**: High-impact modern styling with frosted glass, harmony HSL palettes, real-time WebSocket charts, dynamic metrics, and rich animations.

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** (For local execution)
- **Docker & Docker Compose** (Recommended - handles Linux dependencies seamlessly)
- **WSL (Windows Subsystem for Linux)** (If running Pathway locally on Windows without Docker)

---

### Method 1: Docker (Easiest & Fastest) 🐳

This is the recommended route because Pathway requires a Linux environment. Docker handles this configuration automatically.

1. **Install and start** [Docker Desktop](https://www.docker.com/products/docker-desktop/).
2. **Configure Environment Variables**:
   ```bash
   cp .env.example .env
   # Add your OpenRouter API key to the .env file
   ```
3. **Run the startup batch script** (or run `docker-compose up --build`):
   ```bash
   run_docker.bat
   ```
4. **Access the application**:
   - Dashboard: **[http://localhost:8000](http://localhost:8000)**

---

### Method 2: Manual Local Mode (For Developers) 💻

If you want to view every isolated log stream, you can run the services manually in separate terminal windows.

#### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 2: Configure Environment Variables
```bash
cp .env.example .env
# Edit .env and enter your OPENROUTER_API_KEY
```

#### Step 3: Run the Triad (3 Terminals)

| Terminal | Module | Command | Environment | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Terminal A** | **Simulation** | `python src/generators/sim_engine.py` | Local Host | Generates continuous streams |
| **Terminal B** | **API Server** | `python src/backend/main.py` | Local Host | Hosts FastAPI and WebSockets |
| **Terminal C** | **Pathway Engine** | `python3 src/backend/pw_engine.py` | **WSL/Linux (Required)** | High-speed cognitive processing |

#### Step 4: Open application
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

---

## 🔐 Environment & Security Config

Configure your local environment by creating a `.env` file from the provided example:

```env
# OpenRouter API Key for Synaptix Agentic AI
# Get yours at https://openrouter.ai/keys
OPENROUTER_API_KEY=your_openrouter_api_key_here

# OpenRouter Model to use
# Default is Google Gemini 2.0 Flash Experimental (Free tier)
OPENROUTER_MODEL=google/gemini-2.0-flash-exp:free
```

> [!WARNING]
> Never commit your real `.env` file to source control. The repository is pre-configured with a `.gitignore` to prevent secret leaks of all `.env*` files except `.env.example`.

---

## 🎨 Technology Stack

### Backend & Streaming
- **Pathway**: High-throughput, streaming ETL, and event-driven data engine.
- **FastAPI**: Modern, fast (high-performance) web framework for building APIs.
- **OpenAI Python SDK**: For interfacing with OpenRouter API.
- **Uvicorn**: Lightning-fast ASGI web server implementation.
- **Pydantic & Dotenv**: Data parsing, strict validation, and environment loading.

### Frontend
- **Vanilla JavaScript**: Pure ES Modules, zero heavy frameworks, native WebSockets.
- **Chart.js**: Dynamic, real-time responsive data visualization.
- **CSS Custom Properties**: Sleek glassmorphism theme with custom animations.
- **Google Fonts**: Inter & Outfit typography.

---

## 📊 Cognitive Safety Cortex & Fallback Protocols

What happens when the LLM is overloaded, rate-limited, or goes offline? A critical system cannot simply freeze.

Synaptix is built with an **Enterprise-Grade Safety Cortex** wrapping the AI UDF. When the API returns a `429 Too Many Requests` or fails, the engine seamlessly triggers deterministic **"Reflex Actions"**:

| Domain | Event | Anomaly Indicator | Deterministic Reflex Action |
|:---|:---|:---|:---|
| **Finance** | `CRASH` | Volatility > 10% | `Circuit Breaker Tripped (Halt Trading)` |
| **Finance** | `Flash` | Immediate drawdown | `Injecting Liquidity (Stabilize)` |
| **Healthcare** | `CARDIAC` | Patient BPM = 0 | `Administering Epinephrine (Code Blue)` |
| **Healthcare** | `SEPSIS` | Temp Spike / vitals drop | `Starting IV Antibiotics (Sepsis Protocol)` |
| **DevOps** | `DDOS` | Traffic spike > 50M RPS | `Rerouting Traffic (Scrubbing Center)` |
| **DevOps** | `Ransomware` | File encryption flag | `Isolating Network Segment (Containment)` |

This hybrid system combines the cognitive reasoning of LLMs with the reliability of industrial-grade automatons.

---

## 🗂️ Project Structure

```
synaptix/
├── data/
│   ├── live_feed/              # RAW streaming inputs (JSONL format)
│   │   ├── developer.jsonl
│   │   ├── finance.jsonl
│   │   └── healthcare.jsonl
│   ├── sim_config.json         # Real-time dashboard rules & status configuration
│   └── agent_stream.jsonl      # Pathway AI output read by FastAPI WebSockets
│
├── src/
│   ├── backend/
│   │   ├── main.py             # FastAPI WebSocket gateway, static directories
│   │   └── pw_engine.py        # Pathway streaming engine and LLM agent reasoning
│   │
│   ├── generators/
│   │   └── sim_engine.py       # Multi-domain synthetic data simulation
│   │
│   └── frontend/
│       ├── index.html          # Gateway portal
│       ├── dashboard.html      # Glassmorphic WebSocket analytics console
│       ├── network.html        # Cognitive neural graph simulator
│       ├── forensics.html      # Anomaly logs & historical auditor
│       ├── app.js              # Native WebSocket controller and chart updating
│       └── style.css           # Custom glassmorphic styling system
│
├── Dockerfile                  # Multi-service image configuration
├── docker-compose.yml          # Container configuration for server, pathway, simulation
├── run_docker.bat              # One-click Windows runner
├── run_brain_wsl.sh            # WSL automated Pathway activator
├── requirements.txt            # Python dependencies
└── .gitignore                  # Security-first ignore lists
```

---

## 🏆 Audit Trails & Verifiability

We don't just act; we **log immutably**.

Every cognitive decision made by the Synaptix agent is recorded directly into physical, append-only audit files in the `data/live_feed/` directory:
- 📈 Financial trades audit: `audit_trades.csv`
- 🏥 Medical emergency operations: `audit_medical_logs.csv`
- 💻 Server actions logs: `audit_ops_actions.csv`

This guarantees complete traceability and provides an audit trail showing the exact timestamp, event details, and subsequent AI action taken.

---

**Made with ❤️ using Pathway & FastAPI**
