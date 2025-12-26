# Deploying Synaptix to Render

Since Synaptix involves both a **FastAPI backend** and a **Background Simulation Engine**, it cannot be hosted on static sites like Netlify or Vercel. We use **Render** because it supports long-running Python processes easily.

I have already configured the project with:
- `start.sh`: A script that runs both the simulator and the server.
- `render.yaml`: Configuration file for auto-deployment.
- `requirements.txt`: List of python dependencies.

## Step 1: Push to GitHub
First, make sure your latest code (with my fixes) is on GitHub.

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

## Step 2: Create Service on Render
1.  Go to [dashboard.render.com](https://dashboard.render.com/).
2.  Click **"New +"** and select **"Web Service"**.
3.  Connect your **GitHub account** and select the `synaptix` repository.

## Step 3: Configure Settings
Render might auto-detect the settings from `render.yaml`, but if not, ensure these values are set:

| Setting | Value |
| :--- | :--- |
| **Name** | `synaptix-platform` (or any unique name) |
| **Region** | Any (e.g., Singapore, Frankfurt) |
| **Runtime** | **Python 3** |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `./start.sh` |
| **Instance Type** | Free (or Starter if you want 24/7 uptime) |

## Step 4: Deploy
- Click **"Create Web Service"**.
- Watch the logs. You should see:
    - `Starting Simulation Engine...`
    - `Starting Synaptix Backend...`
    - `Uvicorn running on http://0.0.0.0:10000`

## Step 5: Verify
Once deployed, Render will give you a URL (e.g., `https://synaptix-platform.onrender.com`).
- Open the URL to see the **Homepage**.
- Click "Launch Dashboard" to see the live **Dashboard**.
- **Note**: On the free tier, the app intercepts "sleeps" after inactivity. It might take 50s to wake up on the first load.
