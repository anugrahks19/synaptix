# Synaptix Run Guide 🚀

This project is a complex simulation involving a Data generator, an AI Pathway Brain, and a FastAPI Server.
You can run it in **3 ways**.

---

## ✅ Option 1: Docker (Recommended - Easiest)
This is the fastest way to get everything running with a single click.

1. **Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)**.
2. **Double-click `run_docker.bat`** (or run `docker-compose up --build`).
3. Open **[http://localhost:8000](http://localhost:8000)**.

*This automatically handles the Linux requirement for the AI Brain.*

---

## 💻 Option 2: Local Manual Mode (Hacker Style)
If you prefer to see every log stream separately, use this method.
**Requirement**: The AI Brain (`pw_engine.py`) **MUST** run on Linux (WSL on Windows).

**Step 1: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 2: Launch the Triad (3 Terminals)**
You need 3 separate terminal windows running at the same time:

| Terminal | Process | Command | Application |
| :--- | :--- | :--- | :--- |
| **Terminal A** | **Simulation** | `python src/generators/sim_engine.py` | Generates fake data |
| **Terminal B** | **Server** | `python src/backend/main.py` | Hosting the Web UI |
| **Terminal C** | **AI Brain** | `python3 src/backend/pw_engine.py` | **MUST BE IN WSL/LINUX** |

> **Note**: For Terminal C, if you are on Windows, open a WSL Ubuntu terminal, navigate to the folder, and run the command there.

**Step 3: Access**
Open **[http://localhost:8000](http://localhost:8000)**.

---

## ☁️ Option 3: Cloud (Render Deployment)
If you want to host this online so anyone can access it without running code locally.

1. **Fork the Repo**.
2. **Sign up for [Render](https://render.com/)**.
3. **Create a "Web Service"** and connect your repo.
4. **Select "Docker" Runtime**.
5. Add your `OPENROUTER_API_KEY` in the Environment Variables.
6. The site will be live at your generic Render URL (e.g., `https://synaptix.onrender.com`).

**Fallback**: If the website is down or you cannot host it, always revert to **Option 1 (Docker)** locally.
