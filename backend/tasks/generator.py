"""
Task generators for TruthGuardEnv — Easy / Medium / Hard.
Each call produces a different product instance.
"""
import random
from typing import Dict, Any

# ─── Ingredient pools ─────────────────────────────────────────────────────────

SAFE_INGREDIENTS = [
    "aloe vera", "vitamin e", "glycerin", "chamomile extract", "shea butter",
    "jojoba oil", "green tea extract", "hyaluronic acid", "niacinamide",
    "zinc oxide", "titanium dioxide", "cetyl alcohol", "beeswax",
    "coconut oil", "argan oil", "rose hip oil", "calendula extract",
    "allantoin", "panthenol", "squalane", "tocopherol", "retinol",
    "salicylic acid", "lactic acid", "citric acid", "ascorbic acid",
]

HARMFUL_INGREDIENTS = [
    "parabens", "formaldehyde", "lead", "mercury", "oxybenzone",
    "bpa", "phthalates", "triclosan", "sodium lauryl sulfate",
    "propylene glycol", "diethanolamine", "petrolatum", "aluminum",
    "talc", "synthetic fragrance", "coal tar", "hydroquinone",
]

PRODUCT_NAMES = [
    "DermaClear Face Wash", "BioGlow Moisturizer", "NaturaPure Sunscreen",
    "HerbalBliss Shampoo", "PureSkin Toner", "EcoLux Body Lotion",
    "FreshGuard Deodorant", "VitaShine Hair Serum", "AquaHeal Eye Cream",
    "BotaniFirm Night Cream", "ClearZen Acne Gel", "LuxeWhite Toothpaste",
    "OmegaBoost Lip Balm", "SilkVeil Foundation", "ZenDerm Cleanser",
]

CATEGORIES = [
    "Skincare", "Haircare", "Sunscreen", "Cosmetics",
    "Oral Care", "Personal Care", "Baby Care", "Anti-aging",
]

CLAIMS_POOL = [
    "Organic Certified", "Dermatologist Tested", "Clinically Safe",
    "Natural Ingredients Only", "Hypoallergenic Formula", "Premium Quality",
    "Paraben Free", "Cruelty Free", "Pure Formula",
]


def generate_task(difficulty: str, seed: int, rng: random.Random) -> Dict[str, Any]:
    if difficulty == "easy":
        return _easy_task(seed, rng)
    elif difficulty == "medium":
        return _medium_task(seed, rng)
    else:
        return _hard_task(seed, rng)


# ─── Easy ─────────────────────────────────────────────────────────────────────

def _easy_task(seed: int, rng: random.Random) -> Dict:
    n_safe = rng.randint(4, 7)
    n_harmful = rng.randint(0, 2)
    safe = rng.sample(SAFE_INGREDIENTS, n_safe)
    harmful = rng.sample(HARMFUL_INGREDIENTS, n_harmful)
    ingredients = safe + harmful
    rng.shuffle(ingredients)
    harmful_flags = {i: (i in harmful) for i in ingredients}
    true_risk = round(n_harmful / max(len(ingredients), 1), 3)
    name = rng.choice(PRODUCT_NAMES)
    category = rng.choice(CATEGORIES)
    claims = rng.sample(CLAIMS_POOL, 3)
    return {
        "ingredients": ingredients,
        "harmful_flags": harmful_flags,
        "true_risk_score": true_risk,
        "initial_known": list(ingredients),   # all revealed at start
        "product_name": name,
        "product_category": category,
        "label_claims": claims,
        "difficulty": "easy",
    }


# ─── Medium ───────────────────────────────────────────────────────────────────

def _medium_task(seed: int, rng: random.Random) -> Dict:
    n_safe = rng.randint(5, 9)
    n_harmful = rng.randint(1, 3)
    safe = rng.sample(SAFE_INGREDIENTS, n_safe)
    harmful = rng.sample(HARMFUL_INGREDIENTS, n_harmful)
    ingredients = safe + harmful
    rng.shuffle(ingredients)
    harmful_flags = {i: (i in harmful) for i in ingredients}
    true_risk = round(n_harmful / max(len(ingredients), 1) * 1.1, 3)
    name = rng.choice(PRODUCT_NAMES)
    category = rng.choice(CATEGORIES)
    claims = rng.sample(CLAIMS_POOL, rng.randint(2, 4))
    # Reveal only half
    reveal_count = max(1, len(ingredients) // 2)
    initial_known = rng.sample(ingredients, reveal_count)
    return {
        "ingredients": ingredients,
        "harmful_flags": harmful_flags,
        "true_risk_score": round(min(true_risk, 1.0), 3),
        "initial_known": initial_known,
        "product_name": name,
        "product_category": category,
        "label_claims": claims,
        "difficulty": "medium",
    }


# ─── Hard ─────────────────────────────────────────────────────────────────────

def _hard_task(seed: int, rng: random.Random) -> Dict:
    n_safe = rng.randint(6, 10)
    n_harmful = rng.randint(2, 5)
    safe = rng.sample(SAFE_INGREDIENTS, min(n_safe, len(SAFE_INGREDIENTS)))
    harmful = rng.sample(HARMFUL_INGREDIENTS, min(n_harmful, len(HARMFUL_INGREDIENTS)))
    ingredients = safe + harmful
    rng.shuffle(ingredients)
    harmful_flags = {i: (i in harmful) for i in ingredients}
    true_risk = round(n_harmful / max(len(ingredients), 1) * 1.3, 3)
    name = rng.choice(PRODUCT_NAMES)
    category = rng.choice(CATEGORIES)
    claims = rng.sample(CLAIMS_POOL, rng.randint(3, 5))
    # Reveal very few
    reveal_count = max(1, len(ingredients) // 4)
    initial_known = rng.sample(ingredients, reveal_count)
    return {
        "ingredients": ingredients,
        "harmful_flags": harmful_flags,
        "true_risk_score": round(min(true_risk, 1.0), 3),
        "initial_known": initial_known,
        "product_name": name,
        "product_category": category,
        "label_claims": claims,
        "difficulty": "hard",
    }
