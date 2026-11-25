
import numpy as np


def calculate_trip(
    distance,
    mileage,
    price,
    passengers=1,
    round_trip=False,
    toll=0,
    parking=0,
    extra=0
):
    values = [
        distance, mileage, price,
        passengers, toll, parking, extra
    ]

    if any(float(value) < 0 for value in values):
        raise ValueError("Values cannot be negative.")

    if mileage <= 0 or passengers < 1:
        raise ValueError(
            "Mileage and passengers must be positive."
        )

    total_distance = float(distance) * (
        2 if round_trip else 1
    )

    fuel_needed = float(
        np.divide(total_distance, mileage)
    )

    fuel_cost = fuel_needed * float(price)

    total_cost = (
        fuel_cost
        + float(toll)
        + float(parking)
        + float(extra)
    )

    return {
        "total_distance": total_distance,
        "fuel_needed": fuel_needed,
        "fuel_cost": fuel_cost,
        "toll": float(toll),
        "parking": float(parking),
        "extra_cost": float(extra),
        "total_cost": total_cost,
        "per_person_cost": total_cost / int(passengers)
    }


def calculate_budget_distance(
    budget,
    mileage,
    price,
    other_expenses=0
):
    if mileage <= 0 or price <= 0:
        return 0.0

    available_budget = max(
        0.0,
        float(budget) - float(other_expenses)
    )

    distance = np.divide(
        available_budget,
        price
    ) * mileage

    return float(distance)


def compare_vehicle_costs(
    distance,
    mileage_a,
    price_a,
    mileage_b,
    price_b
):
    if min(distance, mileage_a, mileage_b) <= 0:
        raise ValueError(
            "Distance and mileage must be greater than zero."
        )

    cost_a = distance / mileage_a * price_a
    cost_b = distance / mileage_b * price_b

    if cost_a < cost_b:
        message = (
            f"Vehicle A costs ₹{cost_b-cost_a:,.2f} less."
        )

    elif cost_b < cost_a:
        message = (
            f"Vehicle B costs ₹{cost_a-cost_b:,.2f} less."
        )

    else:
        message = "Both vehicles have the same estimated cost."

    return {
        "cost_a": cost_a,
        "cost_b": cost_b,
        "message": message
    }
