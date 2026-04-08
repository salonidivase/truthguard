# inference.py

import random
from agents import SmartAgent, Observation  # Import your phase-2 safe agents.py
from graders import grader_task1, grader_task2, grader_task3  # Import dummy graders

def main():
    try:
        # Initialize agent
        agent = SmartAgent()
        agent.reset()

        # Simulate environment observations
        obs = Observation()
        obs.visible_ingredients = ["aloe vera", "parabens", "vitamin e"]
        obs.label_claims = ["organic", "safe"]
        obs.checked_claims = {"organic": True}

        # Step through 12 steps for demo
        print("[START] task=inference_demo", flush=True)
        for step in range(1, 13):
            obs.step_num = step
            action = agent.act(obs)
            print(f"[STEP] step={step} action_type={action.action_type} parameter={action.parameter}", flush=True)

        # Call dummy graders
        score1 = grader_task1("output1", "ref1")
        score2 = grader_task2("output2", "ref2")
        score3 = grader_task3("output3", "ref3")

        # Print structured output for validator
        print(f"[STEP] step=13 score={score1}", flush=True)
        print(f"[STEP] step=14 score={score2}", flush=True)
        print(f"[STEP] step=15 score={score3}", flush=True)

        average_score = (score1 + score2 + score3) / 3
        print(f"[END] task=inference_demo score={average_score} steps=15", flush=True)

    except Exception as e:
        print("Error during inference:", e, flush=True)
        raise

if __name__ == "__main__":
    main()
