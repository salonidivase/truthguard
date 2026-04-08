"""
TruthGuardEnv Agents — Random, RuleBased, Smart.
Phase 2-safe: dummy Observation/Action, full SmartAgent logic.
"""
import random
from typing import List

# ─── Dummy Observation & Action (Phase 2-safe) ─────────────────────────────
class Observation:
    def __init__(self):
        self.step_num = 0
        self.visible_ingredients = []
        self.label_claims = []
        self.checked_claims = {}  # claim -> True/False
        self.risk_estimate = 0.0
        self.confidence = 0.8  # default safe value

class Action:
    def __init__(self, action_type="", parameter=""):
        self.action_type = action_type
        self.parameter = parameter

# ─── Ingredient vocabulary ───────────────────────────────────────────────
KNOWN_INGREDIENTS = [
    "aloe vera", "vitamin e", "glycerin", "chamomile extract", "shea butter",
    "jojoba oil", "green tea extract", "hyaluronic acid", "niacinamide",
    "zinc oxide", "titanium dioxide", "cetyl alcohol", "beeswax",
    "coconut oil", "argan oil", "rose hip oil", "calendula extract",
    "allantoin", "panthenol", "squalane", "tocopherol", "retinol",
    "salicylic acid", "lactic acid", "citric acid", "ascorbic acid",
    "parabens", "formaldehyde", "lead", "mercury", "oxybenzone",
    "bpa", "phthalates", "triclosan", "sodium lauryl sulfate",
    "propylene glycol", "diethanolamine", "petrolatum", "aluminum",
    "talc", "synthetic fragrance", "coal tar", "hydroquinone",
]

HARMFUL_SET = {
    "parabens", "formaldehyde", "lead", "mercury", "oxybenzone",
    "bpa", "phthalates", "triclosan", "sodium lauryl sulfate",
    "propylene glycol", "diethanolamine", "petrolatum", "aluminum",
    "talc", "synthetic fragrance", "coal tar", "hydroquinone",
}

# ─── Base Agent ─────────────────────────────────────────────────────────────
class BaseAgent:
    def __init__(self, seed: int = 42):
        self._rng = random.Random(seed)

    def act(self, obs: Observation) -> Action:
        raise NotImplementedError

    def reset(self):
        pass

# ─── Random Agent ───────────────────────────────────────────────────────────
class RandomAgent(BaseAgent):
    def act(self, obs: Observation) -> Action:
        if obs.step_num > 12:
            verdict = self._rng.choice(["SAFE", "UNSAFE"])
            return Action(action_type="final_verdict", parameter=verdict)
        roll = self._rng.random()
        if roll < 0.35:
            ing = self._rng.choice(KNOWN_INGREDIENTS)
            return Action(action_type="query_ingredient", parameter=ing)
        elif roll < 0.55 and obs.label_claims:
            claim = self._rng.choice(obs.label_claims)
            return Action(action_type="verify_claim", parameter=claim)
        elif roll < 0.7:
            return Action(action_type="estimate_risk", parameter="")
        else:
            verdict = self._rng.choice(["SAFE", "UNSAFE"])
            return Action(action_type="final_verdict", parameter=verdict)

# ─── Rule-Based Agent ───────────────────────────────────────────────────────
class RuleBasedAgent(BaseAgent):
    def __init__(self, seed: int = 42):
        super().__init__(seed)
        self._queried = set()
        self._verified = set()
        self._harmful_found = []

    def reset(self):
        self._queried = set()
        self._verified = set()
        self._harmful_found = []

    def act(self, obs: Observation) -> Action:
        for ing in obs.visible_ingredients:
            self._queried.add(ing)
            if ing in HARMFUL_SET and ing not in self._harmful_found:
                self._harmful_found.append(ing)

        unqueried_harmful = [i for i in HARMFUL_SET if i not in self._queried]
        if unqueried_harmful and obs.step_num < 8:
            target = unqueried_harmful[0]
            self._queried.add(target)
            return Action(action_type="query_ingredient", parameter=target)

        unchecked = [c for c in obs.label_claims if c not in obs.checked_claims]
        if unchecked and obs.step_num < 12:
            claim = unchecked[0]
            self._verified.add(claim)
            return Action(action_type="verify_claim", parameter=claim)

        if obs.step_num == 12 or (not unchecked and obs.step_num >= 8):
            if obs.risk_estimate == 0.0:
                return Action(action_type="estimate_risk", parameter="")

        verdict = "UNSAFE" if self._harmful_found or obs.risk_estimate >= 0.3 else "SAFE"
        return Action(action_type="final_verdict", parameter=verdict)

# ─── Smart Agent ───────────────────────────────────────────────────────────
class SmartAgent(BaseAgent):
    def __init__(self, seed: int = 42):
        super().__init__(seed)
        self._queried = set()
        self._harmful_found = []
        self._claim_conflicts = 0
        self._phase = "explore"
        self._risk_estimated = False
        self._estimate_count = 0

    def reset(self):
        self._queried = set()
        self._harmful_found = []
        self._claim_conflicts = 0
        self._phase = "explore"
        self._risk_estimated = False
        self._estimate_count = 0

    def act(self, obs: Observation) -> Action:
        for ing in obs.visible_ingredients:
            self._queried.add(ing)
            if ing in HARMFUL_SET and ing not in self._harmful_found:
                self._harmful_found.append(ing)

        false_claims = [c for c, v in obs.checked_claims.items() if not v]
        self._claim_conflicts = len(false_claims)

        confidence_ok = obs.confidence >= 0.7
        enough_steps = obs.step_num >= 6

        if self._phase == "explore":
            priority_targets = self._prioritized_unqueried()
            if priority_targets:
                target = priority_targets[0]
                self._queried.add(target)
                return Action(action_type="query_ingredient", parameter=target)
            if enough_steps or confidence_ok:
                self._phase = "verify"

        if self._phase == "verify":
            unchecked = [c for c in obs.label_claims if c not in obs.checked_claims]
            if unchecked:
                suspicious = [c for c in unchecked if any(
                    kw in c.lower() for kw in ["organic", "natural", "safe", "pure"]
                )]
                target_claim = suspicious[0] if suspicious else unchecked[0]
                return Action(action_type="verify_claim", parameter=target_claim)
            self._phase = "assess"

        if self._phase == "assess":
            if not self._risk_estimated:
                self._risk_estimated = True
                self._estimate_count += 1
                return Action(action_type="estimate_risk", parameter="")
            if len(self._harmful_found) > self._estimate_count and self._estimate_count < 3:
                self._estimate_count += 1
                return Action(action_type="estimate_risk", parameter="")
            self._phase = "decide"

        verdict = self._compute_verdict(obs)
        return Action(action_type="final_verdict", parameter=verdict)

    def _prioritized_unqueried(self) -> List[str]:
        all_vocab = list(HARMFUL_SET) + [i for i in KNOWN_INGREDIENTS if i not in HARMFUL_SET]
        not_queried = [i for i in all_vocab if i not in self._queried]
        harmful_first = [i for i in not_queried if i in HARMFUL_SET]
        safe_remaining = [i for i in not_queried if i not in HARMFUL_SET]
        return harmful_first[:6] + safe_remaining[:3]

    def _compute_verdict(self, obs: Observation) -> str:
        harmful_score = len(self._harmful_found) * 0.25
        risk_score = obs.risk_estimate
        conflict_score = self._claim_conflicts * 0.1
        confidence_penalty = (1.0 - obs.confidence) * 0.1
        composite = harmful_score + risk_score + conflict_score + confidence_penalty
        threshold = 0.35 if len(self._harmful_found) > 0 else 0.5
        return "UNSAFE" if composite >= threshold else "SAFE"
