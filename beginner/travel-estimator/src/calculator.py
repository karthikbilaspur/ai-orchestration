"""
Calculator V2 - Round 3 Upgrade
Now supports: traffic factor, waiting charges, round-trip, modes
"""
import math

MODE_MULTIPLIERS = {
    "auto": 1.0,
    "cab": 1.5,  # cab is 50% costlier per km base
    "bike": 0.7,
    "metro": 0.3
}

TRAFFIC_SPEED_FACTOR = {
    "low": 1.2,
    "normal": 1.0,
    "heavy": 0.6
}

def calculate_cost(distance_km: float, rate_per_km: float, mode: str = "auto", round_trip: bool = False, waiting_min: int = 0) -> dict:
    base_rate = rate_per_km * MODE_MULTIPLIERS.get(mode, 1.0)
    dist = distance_km * (2 if round_trip else 1)
    base_cost = dist * base_rate
    waiting_cost = waiting_min * 1.5  # Rs 1.5 per min waiting
    night_charge = 0
    # Optional: add night charge logic later
    
    total = base_cost + waiting_cost + night_charge
    return {
        "base_cost": round(base_cost, 2),
        "waiting_cost": round(waiting_cost, 2),
        "total_cost": round(total, 2),
        "distance_charged": dist,
        "mode": mode,
        "round_trip": round_trip
    }

def calculate_time(distance_km: float, speed_kmph: float, traffic: str = "normal", round_trip: bool = False) -> dict:
    effective_speed = speed_kmph * TRAFFIC_SPEED_FACTOR.get(traffic, 1.0)
    dist = distance_km * (2 if round_trip else 1)
    time_hours = dist / effective_speed if effective_speed else 0
    total_minutes = int(time_hours * 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    
    return {
        "hours_decimal": round(time_hours, 2),
        "hours": hours,
        "minutes": minutes,
        "total_minutes": total_minutes,
        "effective_speed": round(effective_speed, 2),
        "formatted": f"{hours}hr {minutes} mins" if hours > 0 else f"{minutes} mins",
        "traffic": traffic
    }

def estimate_budget(cost_info: dict, buffer_percent: int = 15) -> dict:
    total = cost_info["total_cost"]
    buffer_cost = total * (buffer_percent / 100)
    return {
        "base_cost": total,
        "buffer_percent": buffer_percent,
        "max_budget": round(total + buffer_cost, 2),
        "min_budget": round(total * 0.9, 2)  # 10% lower if shared etc
    }
