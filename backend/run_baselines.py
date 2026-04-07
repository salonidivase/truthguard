"""
TruthGuardEnv Baseline Evaluation
Runs all agents × all tasks × multiple episodes with fixed seed.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from env.env import TruthGuardEnv, Action
from agents.agents import get_agent
from tasks.tasks import get_task
from grader.grader import grade

SEED = 42
N_EPISODES = 10
DIFFICULTIES = ["easy", "medium", "hard"]
AGENT_TYPES = ["random", "rule_based", "smart"]
MAX_STEPS = 20


def run_episode(env, agent, difficulty, seed):
    """Run one episode and return grade."""
    task_data = get_task(difficulty, seed=seed)
    product_data = {
        "name": task_data["name"],
        "category": task_data["category"],
        "ingredients": task_data["ingredients"],
        "label_claims": task_data["label_claims"],
        "difficulty": task_data["difficulty"],
        "noise_level": task_data["noise_level"],
    }

    obs = env.reset(seed=seed, product_data=product_data)
    agent.reset()
    trajectory = []
    step = 0

    while not obs.done and step < MAX_STEPS:
        action_str = agent.act(obs)
        action = Action(action=action_str)
        obs, reward, done, info = env.step(action)
        trajectory.append({"action": action_str, "reward": reward})
        step += 1

    state = env.state()
    if not state.done:
        # Force verdict
        action = Action(action="final_verdict:UNSAFE" if obs.risk_estimate > 0.5 else "final_verdict:SAFE")
        obs, reward, done, info = env.step(action)
        trajectory.append({"action": action.action, "reward": reward})
        state = env.state()

    return grade(state, trajectory)


def main():
    env = TruthGuardEnv()

    print("=" * 60)
    print("TruthGuardEnv v1.0 - Baseline Evaluation")
    print("=" * 60)
    print(f"Seed: {SEED} | Episodes: {N_EPISODES} | Max Steps: {MAX_STEPS}")
    print()

    results = {}

    for agent_type in AGENT_TYPES:
        results[agent_type] = {}
        agent = get_agent(agent_type, seed=SEED)
        print(f"Agent: {agent_type.upper()}")
        print("-" * 40)

        for difficulty in DIFFICULTIES:
            scores = []
            f1s = []
            cals = []
            accs = []

            for ep in range(N_EPISODES):
                ep_seed = SEED + ep * 100
                grades = run_episode(env, agent, difficulty, ep_seed)
                scores.append(grades["final_score"])
                f1s.append(grades["issue_f1"])
                cals.append(grades["risk_calibration"])
                accs.append(grades["verdict_accuracy"])

            avg_score = sum(scores) / len(scores)
            avg_f1 = sum(f1s) / len(f1s)
            avg_cal = sum(cals) / len(cals)
            avg_acc = sum(accs) / len(accs)

            results[agent_type][difficulty] = {
                "final_score": round(avg_score, 4),
                "issue_f1": round(avg_f1, 4),
                "risk_calibration": round(avg_cal, 4),
                "verdict_accuracy": round(avg_acc, 4),
            }

            print(f"  {difficulty.capitalize():8s}: Score={avg_score:.3f}  "
                  f"F1={avg_f1:.3f}  Cal={avg_cal:.3f}  Acc={avg_acc:.3f}")

        print()

    # Summary table
    print("=" * 60)
    print("SUMMARY TABLE")
    print("=" * 60)
    print(f"{'Agent':<15} {'Easy':>8} {'Medium':>8} {'Hard':>8} {'Avg':>8}")
    print("-" * 45)

    for agent_type in AGENT_TYPES:
        scores = [results[agent_type][d]["final_score"] for d in DIFFICULTIES]
        avg = sum(scores) / len(scores)
        print(f"{agent_type:<15} {scores[0]:>8.3f} {scores[1]:>8.3f} {scores[2]:>8.3f} {avg:>8.3f}")

    print()
    print("Key: Score = 0.5*F1 + 0.3*Calibration + 0.2*Accuracy")
    print("=" * 60)
    return results


if __name__ == "__main__":
    main()
