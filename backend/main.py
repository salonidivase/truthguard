"""
TruthGuardEnv v1.1 — FIXED FastAPI Backend (Evaluation Safe)
"""
import base64
import io
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional, Dict, Any, List

from env.env import TruthGuardEnv, Action
from env.image_extractor import extract_product_from_image
from grader.grader import compute_score
from agents.agents import RandomAgent, RuleBasedAgent, SmartAgent

app = FastAPI(title="TruthGuardEnv API", version="1.1.0")

# ─── CORS ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── GLOBALS ──────────────────────────────────────────
env = TruthGuardEnv()
_current_agent = None
_episode_log: List[Dict] = []

# ─────────────────────────────────────────────────────
# ✅ RESET (FIXED — ACCEPTS EMPTY BODY)
# ─────────────────────────────────────────────────────
@app.post("/reset", response_model=Dict)
async def reset(req: Optional[dict] = Body(default=None)):
    global _episode_log, _current_agent

    _episode_log = []
    _current_agent = None

    if req is None:
        req = {}

    seed = req.get("seed", 42)
    difficulty = req.get("difficulty", "easy")
    product_data = req.get("product_data", None)

    if product_data is None:
        product_data = {"difficulty": difficulty}
    else:
        product_data["difficulty"] = difficulty

    obs = env.reset(seed=seed, product_data=product_data)

    _episode_log.append({
        "step": 0,
        "action": "RESET",
        "result": "Episode started",
        "reward": 0
    })

    return obs.dict()

# ─────────────────────────────────────────────────────
# STEP
# ─────────────────────────────────────────────────────
@app.post("/step", response_model=Dict)
async def step(req: Optional[dict] = Body(default=None)):
    try:
        if req is None:
            raise HTTPException(status_code=400, detail="Action required")

        action_type = req.get("action_type")
        parameter = req.get("parameter", "")

        action = Action(action_type=action_type, parameter=parameter)
        obs, reward, done, info = env.step(action)

        log_entry = {
            "step": obs.step_num,
            "action": f"{action_type}:{parameter}" if parameter else action_type,
            "result": obs.last_action_result,
            "reward": reward,
        }

        _episode_log.append(log_entry)

        return {
            "observation": obs.dict(),
            "reward": reward,
            "done": done,
            "info": info,
        }

    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ─────────────────────────────────────────────────────
# ✅ AGENT STEP (FIXED)
# ─────────────────────────────────────────────────────
@app.post("/agent_step", response_model=Dict)
async def agent_step(req: Optional[dict] = Body(default=None)):
    global _current_agent

    try:
        if req is None:
            req = {}

        agent_type = req.get("agent_type", "smart")

        state = env.state()
        obs = env._make_observation()

        # initialize agent
        if _current_agent is None or not hasattr(_current_agent, "act"):
            if agent_type == "random":
                _current_agent = RandomAgent(seed=state.seed)
            elif agent_type == "rulebased":
                _current_agent = RuleBasedAgent(seed=state.seed)
            else:
                _current_agent = SmartAgent(seed=state.seed)

        action = _current_agent.act(obs)
        step_obs, reward, done, info = env.step(action)

        log_entry = {
            "step": step_obs.step_num,
            "action": f"{action.action_type}:{action.parameter}" if action.parameter else action.action_type,
            "result": step_obs.last_action_result,
            "reward": reward,
        }

        _episode_log.append(log_entry)

        return {
            "observation": step_obs.dict(),
            "reward": reward,
            "done": done,
            "info": info,
            "action_taken": {
                "action_type": action.action_type,
                "parameter": action.parameter
            },
        }

    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ─────────────────────────────────────────────────────
# STATE
# ─────────────────────────────────────────────────────
@app.get("/state", response_model=Dict)
async def get_state():
    try:
        return env.state().dict()
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ─────────────────────────────────────────────────────
# LOG
# ─────────────────────────────────────────────────────
@app.get("/log", response_model=List)
async def get_log():
    return _episode_log

# ─────────────────────────────────────────────────────
# GRADE (FIXED SAFE INPUT)
# ─────────────────────────────────────────────────────
@app.post("/grade", response_model=Dict)
async def grade(req: Optional[dict] = Body(default=None)):
    try:
        if req is None:
            raise HTTPException(status_code=400, detail="Grader input required")

        state = env.state()

        true_harmful = [i for i, v in state.harmful_flags.items() if v]
        true_verdict = "UNSAFE" if state.true_risk_score >= 0.5 else "SAFE"

        scores = compute_score(
            predicted_harmful=req.get("predicted_harmful", []),
            risk_estimate=req.get("risk_estimate", 0.0),
            verdict=req.get("verdict", "SAFE"),
            true_harmful=true_harmful,
            true_risk=state.true_risk_score,
            true_verdict=true_verdict,
        )

        return scores

    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ─────────────────────────────────────────────────────
# IMAGE UPLOAD
# ─────────────────────────────────────────────────────
@app.post("/upload_image", response_model=Dict)
async def upload_image(
    file: UploadFile = File(...),
    difficulty: str = Form("medium"),
):
    try:
        contents = await file.read()
        b64 = base64.b64encode(contents).decode("utf-8")

        product_data = extract_product_from_image(
            filename=file.filename or "upload.jpg",
            image_b64=b64,
            difficulty=difficulty,
        )

        return {"success": True, "product_data": product_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─────────────────────────────────────────────────────
# HEALTH
# ─────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.1.0"}

# ─────────────────────────────────────────────────────
# FRONTEND SERVE
# ─────────────────────────────────────────────────────
frontend_build = os.path.join(os.path.dirname(__file__), "..", "frontend", "build")

if os.path.exists(frontend_build):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_build, "static")), name="static")

    @app.get("/{full_path:path}")
    async def serve_react(full_path: str):
        index = os.path.join(frontend_build, "index.html")
        if os.path.exists(index):
            return FileResponse(index)
        return {"error": "Frontend not built"}

# ─────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=7860)
