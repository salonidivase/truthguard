# TruthGuardEnv v1.0 — AI Product Safety Auditor

A real-world RL simulation where an AI agent audits product safety under uncertainty.

## Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm start
```

Visit: http://localhost:3000 (frontend) | http://localhost:7860 (API)

## Docker
```bash
docker build -t truthguard .
docker run -p 7860:7860 truthguard
```

## Run Baselines
```bash
cd backend
python run_baselines.py
```

## API Endpoints
- `POST /reset` — Start new episode
- `POST /step` — Manual step
- `POST /agent_step` — Agent step
- `GET /state` — Full environment state
- `POST /upload_image` — Extract product from image
- `POST /grade` — Compute grader score
