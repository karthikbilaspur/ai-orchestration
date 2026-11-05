
# Calculator Tool - Pure math, no AI here.
# Beginner friendly: simple functions.

def calculate_bill(total_amount, gst_percent, tip_percent, num_people):
    if num_people <= 0:
        raise ValueError("Number of people must be > 0")
    base_amount = total_amount / (1 + gst_percent / 100) if gst_percent > 0 else total_amount
    gst_amount = total_amount - base_amount
    tip_amount = total_amount * (tip_percent / 100)
    final_total = total_amount + tip_amount
    per_person = final_total / num_people
    return {
        "base_amount": round(base_amount, 2),
        "gst_percent": gst_percent,
        "gst_amount": round(gst_amount, 2),
        "total_with_gst": round(total_amount, 2),
        "tip_percent": tip_percent,
        "tip_amount": round(tip_amount, 2),
        "final_total": round(final_total, 2),
        "num_people": num_people,
        "per_person": round(per_person, 2)
    }
