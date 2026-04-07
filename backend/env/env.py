"""
TruthGuardEnv v1.0 — OpenEnv-compliant product safety auditing environment.
"""
import random
import copy
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
    action_type: str   # query_ingredient | verify_claim | estimate_risk | final_verdict
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


# ─────────────────────────── Environment ─────────────────────────────

class TruthGuardEnv:
    """OpenEnv-style product safety auditing environment."""

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

    # ── Public API ────────────────────────────────────────────────────

    def reset(self, seed: int = 42, product_data: Optional[Dict] = None) -> Observation:
        self._rng.seed(seed)
        self._difficulty = product_data.get("difficulty", "easy") if product_data else "easy"

        if product_data and product_data.get("ingredients"):
            self._state = self._build_state_from_product(seed, product_data)
        else:
            from tasks.generator import generate_task
            task = generate_task(self._difficulty, seed, self._rng)
            self._state = self._build_state_from_task(seed, task)

        return self._make_observation()

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

    # ── Action Processing ─────────────────────────────────────────────

    def _process_action(self, action: Action) -> Tuple[float, Dict]:
        s = self._state
        reward = 0.0
        info: Dict[str, Any] = {}

        # ── Validity check ──
        if action.action_type not in self.VALID_ACTION_TYPES:
            s.last_action = action.action_type
            s.last_action_result = f"INVALID action '{action.action_type}'"
            reward = -0.05
            info["error"] = "invalid_action"
            return reward, info

        # ── Step penalty (efficiency) ──
        reward -= 0.01

        # ── query_ingredient ──
        if action.action_type == "query_ingredient":
            ing = action.parameter.strip().lower()
            s.last_action = f"query_ingredient:{ing}"
            if ing in s.hidden_ingredients:
                if ing not in s.known_ingredients:
                    s.known_ingredients.append(ing)
                    is_harmful = s.harmful_flags.get(ing, False)
                    s.last_action_result = f"Found: '{ing}' — {'⚠ HARMFUL' if is_harmful else '✓ Safe'}"
                    reward += 0.08 if is_harmful else 0.04
                else:
                    s.last_action_result = f"'{ing}' already known — repetition penalty."
                    reward -= 0.03
            else:
                s.last_action_result = f"Ingredient '{ing}' not found in product."
                reward -= 0.02

        # ── verify_claim ──
        elif action.action_type == "verify_claim":
            claim = action.parameter.strip()
            s.last_action = f"verify_claim:{claim}"
            if claim not in s.label_claims:
                s.last_action_result = f"Claim '{claim}' not on label."
                reward -= 0.02
            elif claim in s.checked_claims:
                s.last_action_result = f"Claim '{claim}' already verified — repetition."
                reward -= 0.03
            else:
                truth = self._get_claim_truth(claim)
                noise_flip = False
                if self._difficulty == "hard":
                    noise_flip = self._rng.random() < 0.25
                result = (not truth) if noise_flip else truth
                s.checked_claims[claim] = result
                s.last_action_result = (
                    f"Claim '{claim}' → {'TRUE' if result else 'FALSE'}"
                    + (" [noisy]" if noise_flip else "")
                )
                reward += 0.06 if not noise_flip else 0.02

        # ── estimate_risk ──
        elif action.action_type == "estimate_risk":
            s.last_action = "estimate_risk"
            harmful_known = sum(1 for i in s.known_ingredients if s.harmful_flags.get(i, False))
            total_known = max(len(s.known_ingredients), 1)
            discovery_ratio = total_known / max(len(s.hidden_ingredients), 1)
            raw_estimate = harmful_known / total_known if total_known else 0.0
            s.risk_estimate = round(min(1.0, raw_estimate * 1.2), 3)
            s.confidence = round(min(1.0, discovery_ratio * 0.9), 3)
            s.last_action_result = (
                f"Risk estimated at {s.risk_estimate:.2f}, confidence {s.confidence:.2f}"
            )
            reward += 0.05

        # ── final_verdict ──
        elif action.action_type == "final_verdict":
            verdict = action.parameter.strip().upper()
            s.last_action = f"final_verdict:{verdict}"
            if verdict not in ("SAFE", "UNSAFE"):
                s.last_action_result = f"Invalid verdict '{verdict}'. Use SAFE or UNSAFE."
                reward -= 0.05
            else:
                actual_unsafe = s.true_risk_score >= 0.5
                predicted_unsafe = verdict == "UNSAFE"
                correct = actual_unsafe == predicted_unsafe
                correctness_score = 1.0 if correct else 0.0
                partial = len(s.known_ingredients) / max(len(s.hidden_ingredients), 1) * 0.3
                final_reward = round(correctness_score * 0.7 + partial, 3)
                reward += final_reward
                s.last_action_result = (
                    f"Verdict: {verdict} — {'✅ CORRECT' if correct else '❌ WRONG'} "
                    f"(true risk={s.true_risk_score:.2f})"
                )
                s.done = True
                info["verdict"] = verdict
                info["correct"] = correct
                info["true_risk"] = s.true_risk_score

        reward = round(max(-1.0, min(1.0, reward)), 4)
        info["reward"] = reward
        return reward, info

    # ── Helpers ───────────────────────────────────────────────────────

    def _get_claim_truth(self, claim: str) -> bool:
        s = self._state
        harmful_count = sum(1 for i in s.hidden_ingredients if s.harmful_flags.get(i, False))
        claim_lower = claim.lower()
        if "organic" in claim_lower:
            return harmful_count == 0
        if "natural" in claim_lower:
            return harmful_count <= 1
        if "safe" in claim_lower or "tested" in claim_lower:
            return s.true_risk_score < 0.4
        if "premium" in claim_lower or "pure" in claim_lower:
            return harmful_count <= 1
        return self._rng.random() > 0.4

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

    def _build_state_from_task(self, seed: int, task: Dict) -> State:
        return State(
            step_num=0,
            hidden_ingredients=task["ingredients"],
            harmful_flags=task["harmful_flags"],
            true_risk_score=task["true_risk_score"],
            known_ingredients=task.get("initial_known", []),
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
            last_action_result="Episode started. Begin auditing.",
        )

    def _build_state_from_product(self, seed: int, product_data: Dict) -> State:
        ingredients = [i.lower().strip() for i in product_data.get("ingredients", [])]
        harmful_keywords = {
            "parabens", "formaldehyde", "lead", "mercury", "asbestos",
            "bpa", "phthalates", "triclosan", "oxybenzone", "sodium lauryl sulfate",
            "propylene glycol", "diethanolamine", "petrolatum", "aluminum",
            "talc", "synthetic fragrance",
        }
        harmful_flags = {ing: any(kw in ing for kw in harmful_keywords) for ing in ingredients}
        harmful_count = sum(harmful_flags.values())
        true_risk = round(min(1.0, harmful_count / max(len(ingredients), 1) * 1.5), 3)
        difficulty = product_data.get("difficulty", "easy")
        initial_known = ingredients if difficulty == "easy" else ingredients[: len(ingredients) // 2]
        return State(
            step_num=0,
            hidden_ingredients=ingredients,
            harmful_flags=harmful_flags,
            true_risk_score=true_risk,
            known_ingredients=initial_known,
            checked_claims={},
            risk_estimate=0.0,
            confidence=0.0,
            done=False,
            total_reward=0.0,
            product_name=product_data.get("product_name", "Unknown Product"),
            product_category=product_data.get("category", "General"),
            label_claims=product_data.get("claims", ["Clinically Tested", "Dermatologist Approved"]),
            difficulty=difficulty,
            seed=seed,
            last_action="",
            last_action_result="Product loaded from image. Begin auditing.",
        )
