"""
TruthGuardEnv Agents — Random, RuleBased, Smart.
All depend on observations and adapt step-by-step.
"""
import random
from typing import List, Optional
import sys
import os

# ─── Ensure project root is in Python path ───────────────────────────────
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# ─── Import Observation and Action safely ───────────────────────────────
try:
    from env.env import Observation, Action
except ModuleNotFoundError as e:
    print("Error importing env module:", e)
    raise

# ─── Ingredient vocabulary (known to agents) ──────────────────────────────

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

# ─── Base Agent ───────────────────────────────────────────────────────────────

class BaseAgent:
    def __init__(self, seed: int = 42):
        self._rng = random.Random(seed)

    def act(self, obs: Observation) -> Action:
        raise NotImplementedError

    def reset(self):
        pass

# ─── Random Agent ─────────────────────────────────────────────────────────────

class RandomAgent(BaseAgent):
    """Picks random valid actions based purely on observation."""

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

# ─── Rule-Based Agent ─────────────────────────────────────────────────────────

class RuleBasedAgent(BaseAgent):
    """Uses heuristic rules: query harmful candidates first, then decide."""

    def __init__(self, seed: int = 42):
        super().__init__(seed)
        self._queried: set = set()
        self._verified: set = set()
        self._harmful_found: List[str] = []

    def reset(self):
        self._queried = set()
        self._verified = set()
        self._harmful_found = []

    def act(self, obs: Observation) -> Action:
        # Update belief from observation
        for ing in obs.visible_ingredients:
            self._queried.add(ing)
            if ing in HARMFUL_SET:
                if ing not in self._harmful_found:
                    self._harmful_found.append(ing)

        # Phase 1: query all harmful candidates not yet checked
        unqueried_harmful = [i for i in HARMFUL_SET if i not in self._queried]
        if unqueried_harmful and obs.step_num < 8:
            target = unqueried_harmful[0]
            self._queried.add(target)
            return Action(action_type="query_ingredient", parameter=target)

        # Phase 2: verify remaining claims
        unchecked = [c for c in obs.label_claims if c not in obs.checked_claims]
        if unchecked and obs.step_num < 12:
            claim = unchecked[0]
            self._verified.add(claim)
            return Action(action_type="verify_claim", parameter=claim)

        # Phase 3: estimate risk
        if obs.step_num == 12 or (not unchecked and obs.step_num >= 8):
            if obs.risk_estimate == 0.0:
                return Action(action_type="estimate_risk", parameter="")

        # Phase 4: verdict
        harmful_count = len(self._harmful_found)
        verdict = "UNSAFE" if harmful_count >= 1 or obs.risk_estimate >= 0.3 else "SAFE"
        return Action(action_type="final_verdict", parameter=verdict)

# ─── Smart Agent ──────────────────────────────────────────────────────────────

class SmartAgent(BaseAgent):
    """
    Multi-phase Bayesian-style agent with:
    - prioritized harmful querying
    - claim-consistency checking
    - dynamic risk threshold
    - adaptive confidence stopping
    """

    def __init__(self, seed: int = 42):
        super().__init__(seed)
        self._queried: set = set()
        self._harmful_found: List[str] = []
        self._claim_conflicts: int = 0
        self._phase: str = "explore"
        self._risk_estimated: bool = False
        self._estimate_count: int = 0

    def reset(self):
        self._queried = set()
        self._harmful_found = []
        self._claim_conflicts = 0
        self._phase = "explore"
        self._risk_estimated = False
        self._estimate_count = 0

    def act(self, obs: Observation) -> Action:
        # Sync belief with observation
        for ing in obs.visible_ingredients:
            self._queried.add(ing)
            if ing in HARMFUL_SET and ing not in self._harmful_found:
                self._harmful_found.append(ing)

        # Detect claim conflicts
        false_claims = [c for c, v in obs.checked_claims.items() if not v]
        self._claim_conflicts = len(false_claims)

        # Dynamic phase transitions
        confidence_ok = obs.confidence >= 0.7
        enough_steps = obs.step_num >= 6

        # Phase: explore
        if self._phase == "explore":
            # Query the most dangerous unknown ingredients first
            priority_targets = self._prioritized_unqueried(obs)
            if priority_targets:
                target = priority_targets[0]
                self._queried.add(target)
                return Action(action_type="query_ingredient", parameter=target)

            # Transition if enough data
            if enough_steps or confidence_ok:
                self._phase = "verify"

        # Phase: verify
        if self._phase == "verify":
            unchecked = [c for c in obs.label_claims if c not in obs.checked_claims]
            if unchecked:
                suspicious = [c for c in unchecked if any(
                    kw in c.lower() for kw in ["organic", "natural", "safe", "pure"]
                )]
                target_claim = suspicious[0] if suspicious else unchecked[0]
                return Action(action_type="verify_claim", parameter=target_claim)

            self._phase = "assess"

        # Phase: assess
        if self._phase == "assess":
            if not self._risk_estimated:
                self._risk_estimated = True
                self._estimate_count += 1
                return Action(action_type="estimate_risk", parameter="")

            if len(self._harmful_found) > self._estimate_count and self._estimate_count < 3:
                self._estimate_count += 1
                return Action(action_type="estimate_risk", parameter="")

            self._phase = "decide"

        # Phase: decide
        verdict = self._compute_verdict(obs)
        return Action(action_type="final_verdict", parameter=verdict)

    def _prioritized_unqueried(self, obs: Observation) -> List[str]:
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
