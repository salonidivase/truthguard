"""
Image-to-product extraction (no external APIs, deterministic).
Simulates OCR via filename/hash-based mapping.
"""
import hashlib
import base64
from typing import Dict, Any, Optional

# ─── Product database (simulated OCR results) ─────────────────────────────────

PRODUCT_DATABASE = [
    {
        "product_name": "DermaClear Organic Face Wash",
        "category": "Skincare",
        "ingredients": [
            "aloe vera", "glycerin", "chamomile extract", "parabens",
            "vitamin e", "citric acid", "sodium lauryl sulfate"
        ],
        "claims": ["Organic Certified", "Dermatologist Tested", "Natural Ingredients Only"],
        "difficulty": "medium",
    },
    {
        "product_name": "BioGlow Premium Moisturizer",
        "category": "Skincare",
        "ingredients": [
            "hyaluronic acid", "niacinamide", "shea butter", "jojoba oil",
            "formaldehyde", "synthetic fragrance", "retinol", "panthenol"
        ],
        "claims": ["Clinically Safe", "Pure Formula", "Hypoallergenic Formula"],
        "difficulty": "hard",
    },
    {
        "product_name": "NaturaPure SPF50 Sunscreen",
        "category": "Sunscreen",
        "ingredients": [
            "zinc oxide", "titanium dioxide", "aloe vera", "vitamin e",
            "oxybenzone", "glycerin", "beeswax"
        ],
        "claims": ["Natural Ingredients Only", "Dermatologist Tested", "Premium Quality"],
        "difficulty": "medium",
    },
    {
        "product_name": "HerbalBliss Shampoo",
        "category": "Haircare",
        "ingredients": [
            "green tea extract", "argan oil", "coconut oil", "panthenol",
            "allantoin", "citric acid"
        ],
        "claims": ["Organic Certified", "Paraben Free", "Cruelty Free"],
        "difficulty": "easy",
    },
    {
        "product_name": "AquaHeal Eye Cream",
        "category": "Anti-aging",
        "ingredients": [
            "retinol", "hyaluronic acid", "rose hip oil", "tocopherol",
            "lead", "mercury", "petrolatum", "squalane"
        ],
        "claims": ["Clinically Safe", "Premium Quality", "Pure Formula", "Dermatologist Tested"],
        "difficulty": "hard",
    },
    {
        "product_name": "EcoLux Body Lotion",
        "category": "Personal Care",
        "ingredients": [
            "shea butter", "coconut oil", "glycerin", "calendula extract",
            "vitamin e", "lactic acid"
        ],
        "claims": ["Organic Certified", "Natural Ingredients Only", "Cruelty Free"],
        "difficulty": "easy",
    },
    {
        "product_name": "ClearZen Acne Treatment Gel",
        "category": "Skincare",
        "ingredients": [
            "salicylic acid", "niacinamide", "aloe vera", "phthalates",
            "triclosan", "zinc oxide", "allantoin", "propylene glycol"
        ],
        "claims": ["Clinically Safe", "Dermatologist Tested", "Hypoallergenic Formula"],
        "difficulty": "hard",
    },
    {
        "product_name": "VitaShine Hair Serum",
        "category": "Haircare",
        "ingredients": [
            "argan oil", "vitamin e", "panthenol", "squalane",
            "cetyl alcohol", "tocopherol"
        ],
        "claims": ["Natural Ingredients Only", "Premium Quality", "Paraben Free"],
        "difficulty": "easy",
    },
]


def extract_product_from_image(
    filename: str,
    image_b64: Optional[str] = None,
    difficulty: str = "medium",
) -> Dict[str, Any]:
    """
    Deterministic product extraction from image.
    Uses filename hash to select a product from the database.

    Returns product_data dict compatible with env.reset().
    """
    try:
        # Hash filename + first 64 chars of b64 for determinism
        hash_input = filename.lower()
        if image_b64:
            hash_input += image_b64[:64]

        digest = hashlib.md5(hash_input.encode()).hexdigest()
        idx = int(digest[:4], 16) % len(PRODUCT_DATABASE)
        product = dict(PRODUCT_DATABASE[idx])
        product["difficulty"] = difficulty
        product["source"] = "image_extraction"
        product["extracted_from"] = filename
        return product

    except Exception as e:
        # Fallback product
        return {
            "product_name": "Unknown Product Sample",
            "category": "General",
            "ingredients": ["aloe vera", "glycerin", "parabens", "vitamin e"],
            "claims": ["Clinically Safe", "Natural Ingredients Only"],
            "difficulty": difficulty,
            "source": "fallback",
            "error": str(e),
        }
