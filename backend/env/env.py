"""
TruthGuardEnv v1.1 — Fixed & OpenEnv-compliant environment
"""
import random
import time
from typing import Optional, Dict, Any, List, Tuple
from pydantic import BaseModel


# ─────────────────────────── Typed Models ────────────────────────────

class Observation(BaseModel):
    step_num: int
    visible_ingredients: List[str]
    checked_claims: Dict[str, bool]
    risk_estimate: float
    confidence: float
    last_action: str
    last_action_result: str
    done: bool
    product_name: str
    product_category: str
    label_claims: List[str]


class Action(BaseModel):
    action_type: str
    parameter: str = ""


class State(BaseModel):
    step_num: int
    hidden_ingredients: List[str]
    harmful_flags: Dict[str, bool]
    true_risk_score: float
    known_ingredients: List[str]
    checked_claims: Dict[str, bool]
    risk_estimate: float
    confidence: float
    done: bool
    total_reward: float
    product_name: str
    product_category: str
    label_claims: List[str]
    difficulty: str
    seed: int

    # ✅ Required fields (fix)
    last_action: str = ""
    last_action_result: str = ""


# ─────────────────────────── Environment ─────────────────────────────

class TruthGuardEnv:

    VALID_ACTION_TYPES = {
        "query_ingredient",
        "verify_claim",
        "estimate_risk",
        "final_verdict",
    }

    def __init__(self):
        self._rng = random.Random()
        self._state: Optional[State] = None
        self._difficulty: str = "easy"

    # ── RESET ─────────────────────────────────────────────────────────

    def reset(self, seed: int = 42, product_data: Optional[Dict] = None) -> Observation:
        # 🔥 TRUE RANDOMNESS FIX
        real_seed = seed + int(time.time() * 1000) % 100000
        self._rng.seed(real_seed)

        self._difficulty = product_data.get("difficulty", "easy") if product_data else "easy"

        if product_data and product_data.get("ingredients"):
            self._state = self._build_state_from_product(real_seed, product_data)
        else:
            from tasks.generator import generate_task
            task = generate_task(self._difficulty, real_seed, self._rng)
            self._state = self._build_state_from_task(real_seed, task)

        return self._make_observation()

    # ── STEP ──────────────────────────────────────────────────────────

    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict]:
        if self._state is None:
            raise RuntimeError("Call reset() before step().")

        if self._state.done:
            return self._make_observation(), 0.0, True, {"info": "Episode already done."}

        self._state.step_num += 1
        reward, info = self._process_action(action)
        self._state.total_reward += reward

        obs = self._make_observation()
        return obs, reward, self._state.done, info

    def state(self) -> State:
        if self._state is None:
            raise RuntimeError("Call reset() first.")
        return self._state

    # ── ACTION LOGIC ──────────────────────────────────────────────────

    def _process_action(self, action: Action) -> Tuple[float, Dict]:
        s = self._state
        reward = 0.0
        info: Dict[str, Any] = {}

        if action.action_type not in self.VALID_ACTION_TYPES:
            s.last_action = action.action_type
            s.last_action_result = f"INVALID action '{action.action_type}'"
            return -0.05, {"error": "invalid_action"}

        reward -= 0.01

        if action.action_type == "query_ingredient":
            ing = action.parameter.strip().lower()
            s.last_action = f"query_ingredient:{ing}"

            if ing in s.hidden_ingredients:
                if ing not in s.known_ingredients:
                    s.known_ingredients.append(ing)
                    is_harmful = s.harmful_flags.get(ing, False)
                    s.last_action_result = f"{ing} → {'HARMFUL' if is_harmful else 'SAFE'}"
                    reward += 0.08 if is_harmful else 0.04
                else:
                    s.last_action_result = f"{ing} already known"
                    reward -= 0.03
            else:
                s.last_action_result = f"{ing} not found"
                reward -= 0.02

        elif action.action_type == "verify_claim":
            claim = action.parameter.strip()
            s.last_action = f"verify_claim:{claim}"

            if claim not in s.label_claims:
                s.last_action_result = "Claim not found"
                reward -= 0.02
            elif claim in s.checked_claims:
                s.last_action_result = "Already checked"
                reward -= 0.03
            else:
                truth = self._get_claim_truth(claim)
                s.checked_claims[claim] = truth
                s.last_action_result = f"{claim} → {'TRUE' if truth else 'FALSE'}"
                reward += 0.06

        elif action.action_type == "estimate_risk":
            s.last_action = "estimate_risk"

            harmful_known = sum(
                1 for i in s.known_ingredients if s.harmful_flags.get(i, False)
            )
            total_known = max(len(s.known_ingredients), 1)

            s.risk_estimate = round(harmful_known / total_known, 3)
            s.confidence = round(
                len(s.known_ingredients) / max(len(s.hidden_ingredients), 1), 3
            )

            s.last_action_result = f"Risk {s.risk_estimate}, Confidence {s.confidence}"
            reward += 0.05

        elif action.action_type == "final_verdict":
            verdict = action.parameter.strip().upper()
            s.last_action = f"final_verdict:{verdict}"

            actual = s.true_risk_score >= 0.5
            predicted = verdict == "UNSAFE"

            correct = actual == predicted
            s.last_action_result = f"{verdict} → {'CORRECT' if correct else 'WRONG'}"

            reward += 1.0 if correct else -0.5
            s.done = True

        return round(reward, 4), info

    # ── OBSERVATION ───────────────────────────────────────────────────

    def _make_observation(self) -> Observation:
        s = self._state
        return Observation(
            step_num=s.step_num,
            visible_ingredients=list(s.known_ingredients),
            checked_claims=dict(s.checked_claims),
            risk_estimate=s.risk_estimate,
            confidence=s.confidence,
            last_action=s.last_action,
            last_action_result=s.last_action_result,
            done=s.done,
            product_name=s.product_name,
            product_category=s.product_category,
            label_claims=list(s.label_claims),
        )

    # ── HELPERS ───────────────────────────────────────────────────────

    def _get_claim_truth(self, claim: str) -> bool:
        s = self._state
        harmful_count = sum(
            1 for i in s.hidden_ingredients if s.harmful_flags.get(i, False)
        )
        return harmful_count == 0

    def _build_state_from_task(self, seed: int, task: Dict) -> State:
        return State(
            step_num=0,
            hidden_ingredients=task["ingredients"],
            harmful_flags=task["harmful_flags"],
            true_risk_score=task["true_risk_score"],

            # 🔥 FIX: show initial ingredients
            known_ingredients=task["ingredients"][:2],

            checked_claims={},
            risk_estimate=0.0,
            confidence=0.0,
            done=False,
            total_reward=0.0,
            product_name=task["product_name"],
            product_category=task["product_category"],
            label_claims=task["label_claims"],
            difficulty=self._difficulty,
            seed=seed,
            last_action="",
            last_action_result="Episode started"
        )

    def _build_state_from_product(self, seed: int, product_data: Dict) -> State:
        ingredients = [i.lower() for i in product_data.get("ingredients", [])]

        harmful_keywords = {"parabens","lead","mercury","bpa","phthalates"}
        harmful_flags = {
            i: any(k in i for k in harmful_keywords)
            for i in ingredients
        }

        return State(
            step_num=0,
            hidden_ingredients=ingredients,
            harmful_flags=harmful_flags,
            true_risk_score=0.5,

            # 🔥 FIX: show initial ingredients
            known_ingredients=ingredients[:2],

            checked_claims={},
            risk_estimate=0.0,
            confidence=0.0,
            done=False,
            total_reward=0.0,
            product_name=product_data.get("product_name", "Unknown"),
            product_category=product_data.get("category", "General"),
            label_claims=product_data.get("claims", []),
            difficulty=self._difficulty,
            seed=seed,
            last_action="",
            last_action_result="Loaded from image"
        )
