"""
Phase 2-safe Inference for TruthGuardEnv
Uses SmartAgent + LiteLLM API via injected environment variables.
Structured output included for validator.
"""
import os
import sys

# ─── Ensure project root is in Python path ───────────────────────────────
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ─── Import agent ───────────────────────────────────────────────────────
try:
    from backend.agents.agents import SmartAgent
except ModuleNotFoundError as e:
    print("Error importing SmartAgent:", e, flush=True)
    raise

# ─── Phase 2-safe dummy Observation/Action ──────────────────────────────
class Observation:
    def __init__(self):
        self.step_num = 0
        self.visible_ingredients = []
        self.label_claims = []
        self.checked_claims = {}  # claim -> True/False
        self.risk_estimate = 0.0
        self.confidence = 0.8

class Action:
    def __init__(self, action_type="", parameter=""):
        self.action_type = action_type
        self.parameter = parameter

# ─── Initialize LiteLLM client ─────────────────────────────────────────
from openai import OpenAI

client = OpenAI(
    base_url=os.environ["API_BASE_URL"],
    api_key=os.environ["API_KEY"]
)

# ─── Main inference routine ─────────────────────────────────────────────
def main():
    print("[START] task=truthguard_inference", flush=True)

    agent = SmartAgent()
    agent.reset()
    obs = Observation()

    for step in range(1, 15):
        obs.step_num = step
        action = agent.act(obs)

        # Print action info for validator
        print(f"[STEP] step={step} action={action.action_type} parameter={action.parameter}", flush=True)

        # Make LLM call only for actions needing judgment
        if action.action_type in ["query_ingredient", "verify_claim"]:
            prompt = f"Analyze ingredient or claim safety: {action.parameter}"
            try:
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                llm_output = resp.choices[0].message.content
                print(f"[STEP] step={step} llm_output={llm_output}", flush=True)
            except Exception as e:
                print(f"[STEP] step={step} llm_error={e}", flush=True)

    # Final verdict from agent
    final_action = agent.act(obs)
    print(f"[END] task=truthguard_inference score={final_action.parameter} steps={step}", flush=True)

if __name__ == "__main__":
    main()
