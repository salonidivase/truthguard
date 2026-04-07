"""
TruthGuardEnv — Baseline Evaluation Script
Runs all agents × all difficulties × multiple episodes.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import random
from env.env import TruthGuardEnv, Action
from agents.agents import RandomAgent, RuleBasedAgent, SmartAgent
from grader.grader import compute_score

DIFFICULTIES = ["easy", "medium", "hard"]
AGENT_CLASSES = {
    "RandomAgent": RandomAgent,
    "RuleBasedAgent": RuleBasedAgent,
    "SmartAgent": SmartAgent,
}
N_EPISODES = 10
BASE_SEED = 2024
MAX_STEPS = 20


def run_episode(env, agent, difficulty, seed):
    product_data = {"difficulty": difficulty}
    obs = env.reset(seed=seed, product_data=product_data)
    agent.reset()
    total_reward = 0.0
    verdict = "SAFE"

    for _ in range(MAX_STEPS):
        if obs.done:
            break
        action = agent.act(obs)
        obs, reward, done, info = env.step(action)
        total_reward += reward
        if "verdict" in info:
            verdict = info["verdict"]
        if done:
            break

    # Grader
    state = env.state()
    predicted_harmful = [
        i for i in obs.visible_ingredients
        if any(kw in i for kw in [
            "parabens", "formaldehyde", "lead", "mercury", "oxybenzone",
            "bpa", "phthalates", "triclosan", "sodium lauryl sulfate",
            "propylene glycol", "diethanolamine", "petrolatum", "aluminum",
            "talc", "synthetic fragrance", "coal tar", "hydroquinone",
        ])
    ]
    true_harmful = [i for i, v in state.harmful_flags.items() if v]
    true_verdict = "UNSAFE" if state.true_risk_score >= 0.5 else "SAFE"
    scores = compute_score(
        predicted_harmful=predicted_harmful,
        true_harmful=true_harmful,
        risk_estimate=obs.risk_estimate,
        true_risk=state.true_risk_score,
        verdict=verdict,
        true_verdict=true_verdict,
    )
    return scores["final_score"]


def main():
    print("=" * 60)
    print("  TruthGuardEnv v1.0 — Baseline Evaluation")
    print("=" * 60)
    env = TruthGuardEnv()

    results = {}
    for agent_name, AgentClass in AGENT_CLASSES.items():
        results[agent_name] = {}
        for diff in DIFFICULTIES:
            scores = []
            for ep in range(N_EPISODES):
                seed = BASE_SEED + ep * 7
                agent = AgentClass(seed=seed)
                score = run_episode(env, agent, diff, seed)
                scores.append(score)
            avg = round(sum(scores) / len(scores), 4)
            results[agent_name][diff] = avg

    print(f"\n{'Agent':<18} {'Easy':>8} {'Medium':>10} {'Hard':>8}")
    print("-" * 46)
    for agent_name, diffs in results.items():
        e = diffs["easy"]
        m = diffs["medium"]
        h = diffs["hard"]
        print(f"{agent_name:<18} {e:>8.4f} {m:>10.4f} {h:>8.4f}")

    print("\n── Summary (avg across difficulties) ──")
    for agent_name, diffs in results.items():
        avg = sum(diffs.values()) / 3
        print(f"  {agent_name}: {avg:.4f}")

    print("\n✅ Baseline evaluation complete.")
    return results


if __name__ == "__main__":
    main()
