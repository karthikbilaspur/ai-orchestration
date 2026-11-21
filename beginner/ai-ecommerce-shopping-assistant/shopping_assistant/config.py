"""Central settings for the shopping assistant.

Beginner tip: if you want to tweak the behaviour of the demo (how many
products are compared, how strongly ratings count, which currency symbol is
shown...) this is the only file you need to touch.
"""

CURRENCY = "$"

# How many products Product Research hands to the Comparison agent at most.
MAX_SHORTLIST = 4
# How many of those the Comparison agent puts in the side-by-side table.
COMPARE_TOP_N = 3

# If nothing fits the budget we retry with the budget stretched by 20 %.
BUDGET_RELAX_FACTOR = 1.20

# How the Recommendation agent weighs each ingredient of the final score.
# (Weights that do not apply to a request are dropped and the rest re-scaled.)
SCORE_WEIGHTS = {
    "fit": 0.35,       # how many of the shopper's stated needs the product matches
    "quality": 0.25,   # customer rating
    "value": 0.20,     # cheapest price on the shortlist / this price (cheapest = 1.0)
    "priority": 0.20,  # how well it does on the specs the shopper cares about most
}

DISCLAIMER = (
    "Demo only: this assistant never buys anything, adds items to a cart or "
    "takes payment. Prices and specs come from a made-up local sample catalog."
)


def money(amount: float) -> str:
    """Format a price, e.g. 1099 -> '$1,099'."""
    return f"{CURRENCY}{amount:,.0f}"
