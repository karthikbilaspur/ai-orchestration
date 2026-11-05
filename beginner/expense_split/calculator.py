
"""
Tool Layer: Pure Python Calculator
This is what LLM calls. No AI here, just exact math.
"""

def calculate_bill(total_amount: float, gst_percent: float, tip_percent: float, num_people: int, gst_inclusive: bool = True):
    if num_people <= 0:
        num_people = 1
    if total_amount <= 0:
        raise ValueError("Total amount must be > 0")

    if gst_inclusive and gst_percent > 0:
        base_amount = total_amount / (1 + gst_percent / 100)
        gst_amount = total_amount - base_amount
        subtotal = total_amount
    else:
        base_amount = total_amount
        gst_amount = base_amount * (gst_percent / 100)
        subtotal = base_amount + gst_amount

    tip_amount = subtotal * (tip_percent / 100)
    final_total = subtotal + tip_amount
    per_person = final_total / num_people

    return {
        "base_amount": round(base_amount, 2),
        "gst_amount": round(gst_amount, 2),
        "subtotal": round(subtotal, 2),
        "tip_amount": round(tip_amount, 2),
        "final_total": round(final_total, 2),
        "per_person": round(per_person, 2)
    }

if __name__ == "__main__":
    print(calculate_bill(3480, 18, 10, 4, True))
