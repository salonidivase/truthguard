import os
import sys
import json
import requests

# ─── Ensure project root is in Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ─── Import agent
try:
    from backend.agents.agents import SmartAgent
except ModuleNotFoundError as e:
    print("Error importing SmartAgent:", e, flush=True)
    raise

# ─── Phase 2-safe Observation / Action
class Observation:
    def __init__(self):
        self.step_num = 0
        self.visible_ingredients = []
        self.label_claims = []
        self.checked_claims = {}
        self.risk_estimate = 0.0
        self.confidence = 0.8

class Action:
    def __init__(self, action_type="", parameter=""):
        self.action_type = action_type
        self.parameter = parameter

# ─── LiteLLM request wrapper using only requests
def llm_call(prompt):
    try:
        url = os.environ["API_BASE_URL"] + "/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {os.environ['API_KEY']}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}]
        }
        resp = requests.post(url, headers=headers, data=json.dumps(data))
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"LLM call failed: {e}"

# ─── Main inference
def main():
    print("[START] task=truthguard_inference", flush=True)

    agent = SmartAgent()
    agent.reset()
    obs = Observation()

    for step in range(1, 15):
        obs.step_num = step
        action = agent.act(obs)

        print(f"[STEP] step={step} action={action.action_type} parameter={action.parameter}", flush=True)

        if action.action_type in ["query_ingredient", "verify_claim"]:
            output = llm_call(f"Analyze ingredient or claim safety: {action.parameter}")
            print(f"[STEP] step={step} llm_output={output}", flush=True)

    final_action = agent.act(obs)
    print(f"[END] task=truthguard_inference score={final_action.parameter} steps={step}", flush=True)

if __name__ == "__main__":
    main()
