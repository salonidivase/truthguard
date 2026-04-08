import sys
import os

# ─── Ensure project root is in Python path ───────────────────────────────
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ─── Import SmartAgent safely ─────────────────────────────────────────────
try:
    from backend.agents.agents import SmartAgent
except ModuleNotFoundError as e:
    print("Error importing SmartAgent:", e)
    raise

# ─── Dummy Observation class (Phase 2-safe) ───────────────────────────────
class Observation:
    def __init__(self):
        self.step_num = 0
        self.visible_ingredients = []
        self.label_claims = []
        self.checked_claims = {}  # claim -> True/False
        self.risk_estimate = 0.0
        self.confidence = 0.8  # default safe value

# ─── Example Inference Logic ──────────────────────────────────────────────
def main():
    try:
        # Initialize agent
        agent = SmartAgent()
        agent.reset()

        # Use dummy observation
        obs = Observation()

        # Step through a few actions as demo
        for step in range(1, 15):
            obs.step_num = step
            action = agent.act(obs)
            print(f"Step {step}: Action -> {action.action_type}, Parameter -> {action.parameter}")

    except Exception as e:
        print("Error during inference:", e)
        raise

if __name__ == "__main__":
    main()
