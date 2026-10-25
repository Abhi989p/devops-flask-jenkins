# Automated Deployment of Flask Applications using Jenkins and Docker

A beginner-friendly DevOps project demonstrating a complete CI/CD pipeline using **Python Flask**, **Docker**, and **Jenkins**.

---

## Project Structure

```
Devops CBP/
├── app.py            # Flask web application
├── test_app.py       # Pytest test suite
├── requirements.txt  # Python dependencies
├── Dockerfile        # Docker image definition
├── .dockerignore     # Files excluded from Docker build
├── .gitignore        # Files excluded from Git
├── Jenkinsfile       # Jenkins CI/CD pipeline
└── README.md         # This file
```

---

## Tech Stack

| Tool | Role |
|------|------|
| Python 3.11 + Flask | Web application |
| Pytest | Automated testing |
| Docker | Containerisation |
| Jenkins | CI/CD automation |
| Git / GitHub | Version control |

---

## Application Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Homepage — displays app name and version |
| `GET /health` | Returns `{"status": "healthy", "version": "1.0.0"}` |

---

## Local Development (Windows PowerShell)

### Prerequisites
- Python 3.9+ installed and on PATH
- Docker Desktop running (WSL 2 backend)

### 1 — Run tests directly

```powershell
# Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest test_app.py -v
```

Expected output: **6 passed**.

### 2 — Run the app locally (no Docker)

```powershell
.\venv\Scripts\Activate.ps1
python app.py
```

Open <http://localhost:5000> in your browser.

### 3 — Build and run with Docker

```powershell
# Build the image
docker build -t flask-devops-app:latest .

# Run the container
docker run -d --name flask-app -p 5000:5000 flask-devops-app:latest

# Test the health endpoint
Invoke-RestMethod http://localhost:5000/health

# View logs
docker logs flask-app

# Stop and remove
docker stop flask-app
docker rm flask-app
```

---

## Jenkins CI/CD Pipeline

### Pipeline Stages

```
Checkout → Install Dependencies → Run Tests → Build Image → Deploy → Verify
```

| Stage | What it does |
|-------|-------------|
| **Checkout** | Pulls the latest code from GitHub |
| **Install Dependencies** | Creates a Python venv and installs packages |
| **Run Tests** | Runs all 6 pytest tests; fails the build on any error |
| **Build Docker Image** | Builds `flask-devops-app:latest` |
| **Deploy Container** | Stops any old container, starts the new one |
| **Verify Deployment** | Curls `/health` and fails if not HTTP 200 |

### Setting up the Jenkins Pipeline (step-by-step)

> Jenkins is already running at <http://localhost:8080>

#### Step 1 — Push code to GitHub

```powershell
git init
git add .
git commit -m "Initial commit: Flask DevOps project"
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

#### Step 2 — Create a new Pipeline job in Jenkins

1. Open <http://localhost:8080> → **New Item**
2. Enter name: `flask-devops-pipeline`
3. Select **Pipeline** → click **OK**

#### Step 3 — Configure the Pipeline

In the **Pipeline** section at the bottom of the job config page:

- **Definition:** `Pipeline script from SCM`
- **SCM:** `Git`
- **Repository URL:** `https://github.com/<your-username>/<your-repo>.git`
- **Branch:** `*/main`
- **Script Path:** `Jenkinsfile`

Click **Save**.

#### Step 4 — Trigger the pipeline

Click **Build Now** on the left sidebar.  
Watch each stage turn green in the Stage View.

#### GitHub Webhook (optional — for automatic triggers)

If Jenkins is reachable from the internet (or via ngrok):

1. Go to your GitHub repo → **Settings → Webhooks → Add webhook**
2. **Payload URL:** `http://<your-public-jenkins-url>:8080/github-webhook/`
3. **Content type:** `application/json`
4. **Trigger:** `Just the push event`

In Jenkins job config, enable **GitHub hook trigger for GITScm polling** under **Build Triggers**.

> **No internet access?** Use **Build Now** manually — the pipeline is fully functional without webhooks.

---

## Troubleshooting

### `python3: command not found` in Jenkins
The Jenkins container uses `python3`. Ensure the container has Python 3 installed, or change `python3` to `python` in the Jenkinsfile.

```bash
# Check inside Jenkins container
docker exec -it jenkins python3 --version
```

If missing, add to your Jenkins Dockerfile:
```dockerfile
RUN apt-get update && apt-get install -y python3 python3-venv python3-pip
```

### `docker: command not found` in Jenkins
Your custom `my-jenkins-docker` image already includes Docker. Confirm with:
```bash
docker exec -it jenkins docker --version
```

### Port 5000 already in use

```powershell
# Find what is using port 5000
netstat -ano | findstr :5000
# Kill it by PID
taskkill /PID <PID> /F

# Or change HOST_PORT in the Jenkinsfile environment block to e.g. 5001
```

### Health check fails (`host.docker.internal` unreachable)
The Jenkinsfile uses `host.docker.internal` to reach the host from inside the Jenkins container.  
If it fails, find the Docker host gateway IP and replace it:

```bash
docker exec -it jenkins cat /etc/hosts | grep host-gateway
# or
docker network inspect bridge | grep Gateway
```

Then update the Verify stage in `Jenkinsfile`:
```groovy
http://172.17.0.1:${HOST_PORT}/health
```

### Old container still running after re-deploy
The pipeline always runs `docker stop` + `docker rm` before starting a new container, so old instances are automatically removed.

---

## Demonstrating the Full Automated Deployment

1. Make a code change — e.g., update `APP_VERSION = "1.0.1"` in `app.py`
2. Commit and push:
   ```powershell
   git add app.py
   git commit -m "bump version to 1.0.1"
   git push
   ```
3. In Jenkins, click **Build Now** (or wait for the webhook)
4. Watch all 6 stages complete green
5. Open <http://localhost:5000> — the version number updates automatically

---

## Architecture Overview

```
Developer
   │  git push
   ▼
GitHub Repository
   │  webhook / manual trigger
   ▼
Jenkins Pipeline
   ├── checkout code
   ├── pip install + pytest
   ├── docker build
   ├── docker stop old → docker run new
   └── curl /health → ✅
              │
              ▼
   Flask Container (port 5000)
   http://localhost:5000
```
