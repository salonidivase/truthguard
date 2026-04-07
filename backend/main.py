"""
TruthGuardEnv v1.0 — FastAPI Backend
"""
import base64
import io
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from env.env import TruthGuardEnv, Observation, Action, State
from env.image_extractor import extract_product_from_image
from grader.grader import compute_score
from agents.agents import RandomAgent, RuleBasedAgent, SmartAgent

app = FastAPI(title="TruthGuardEnv API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Global environment instance ─────────────────────────────────────────────

env = TruthGuardEnv()
_current_agent = None
_episode_log: List[Dict] = []


# ─── Request / Response Models ────────────────────────────────────────────────

class ResetRequest(BaseModel):
    seed: int = 42
    difficulty: str = "easy"
    product_data: Optional[Dict[str, Any]] = None


class StepRequest(BaseModel):
    action_type: str
    parameter: str = ""


class AgentStepRequest(BaseModel):
    agent_type: str = "smart"   # random | rulebased | smart


class GraderRequest(BaseModel):
    predicted_harmful: List[str]
    risk_estimate: float
    verdict: str


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.post("/reset", response_model=Dict)
async def reset(req: ResetRequest):
    global _episode_log, _current_agent
    _episode_log = []
    _current_agent = None
    product_data = req.product_data
    if product_data is None:
        product_data = {"difficulty": req.difficulty}
    else:
        product_data["difficulty"] = req.difficulty

    obs = env.reset(seed=req.seed, product_data=product_data)
    _episode_log.append({"step": 0, "action": "RESET", "result": "Episode started", "reward": 0})
    return obs.dict()


@app.post("/step", response_model=Dict)
async def step(req: StepRequest):
    try:
        action = Action(action_type=req.action_type, parameter=req.parameter)
        obs, reward, done, info = env.step(action)
        log_entry = {
            "step": obs.step_num,
            "action": f"{req.action_type}:{req.parameter}" if req.parameter else req.action_type,
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


@app.post("/agent_step", response_model=Dict)
async def agent_step(req: AgentStepRequest):
    """Run one step using the selected agent based on current observation."""
    global _current_agent
    try:
        state = env.state()
        obs = env._make_observation()

        if _current_agent is None or not hasattr(_current_agent, "act"):
            if req.agent_type == "random":
                _current_agent = RandomAgent(seed=state.seed)
            elif req.agent_type == "rulebased":
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
            "action_taken": {"action_type": action.action_type, "parameter": action.parameter},
        }
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/state", response_model=Dict)
async def get_state():
    try:
        state = env.state()
        return state.dict()
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/log", response_model=List)
async def get_log():
    return _episode_log


@app.post("/grade", response_model=Dict)
async def grade(req: GraderRequest):
    try:
        state = env.state()
        true_harmful = [i for i, v in state.harmful_flags.items() if v]
        true_verdict = "UNSAFE" if state.true_risk_score >= 0.5 else "SAFE"
        scores = compute_score(
            predicted_harmful=req.predicted_harmful,
            true_harmful=true_harmful,
            risk_estimate=req.risk_estimate,
            true_risk=state.true_risk_score,
            verdict=req.verdict,
            true_verdict=true_verdict,
        )
        return scores
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


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


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


# ─── Serve React frontend ─────────────────────────────────────────────────────

frontend_build = os.path.join(os.path.dirname(__file__), "..", "frontend", "build")
if os.path.exists(frontend_build):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_build, "static")), name="static")

    @app.get("/{full_path:path}")
    async def serve_react(full_path: str):
        index = os.path.join(frontend_build, "index.html")
        if os.path.exists(index):
            return FileResponse(index)
        return {"error": "Frontend not built"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=7860, reload=False)
