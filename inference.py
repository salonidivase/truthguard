import requests

BASE_URL = "http://localhost:7860"

def reset():
    try:
        res = requests.post(f"{BASE_URL}/reset", json={})
        return res.json()
    except Exception as e:
        return {"error": str(e)}

def step(action_type, parameter=""):
    try:
        res = requests.post(
            f"{BASE_URL}/step",
            json={"action_type": action_type, "parameter": parameter},
        )
        return res.json()
    except Exception as e:
        return {"error": str(e)}

def agent_step(agent_type="smart"):
    try:
        res = requests.post(
            f"{BASE_URL}/agent_step",
            json={"agent_type": agent_type},
        )
        return res.json()
    except Exception as e:
        return {"error": str(e)}

def get_state():
    try:
        res = requests.get(f"{BASE_URL}/state")
        return res.json()
    except Exception as e:
        return {"error": str(e)}

def grade(predicted_harmful, risk_estimate, verdict):
    try:
        res = requests.post(
            f"{BASE_URL}/grade",
            json={
                "predicted_harmful": predicted_harmful,
                "risk_estimate": risk_estimate,
                "verdict": verdict,
            },
        )
        return res.json()
    except Exception as e:
        return {"error": str(e)}
