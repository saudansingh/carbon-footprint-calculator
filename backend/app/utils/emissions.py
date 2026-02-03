from datetime import datetime, date
from typing import Dict, Tuple

# Emission factors (kg CO2e per unit)
# Transport: factors per km
CAR_PETROL_PER_KM = 0.12
FLIGHT_SHORT_HAUL_PER_KM = 0.255
# The following commonly used factors are provided with clear labelling.
# Source reference for typical values: UK DEFRA published factors (~2023 ranges)
BUS_PER_KM = 0.089
TRAIN_PER_KM = 0.041

# Energy
ELECTRICITY_PER_KWH = 0.5

# Food per meal
BEEF_MEAL_KG = 6.0
VEG_MEAL_KG = 1.5


TRANSPORT_TYPES = {"car", "flight", "bus", "train"}
FOOD_TYPES = {"beef_meal", "vegetarian_meal"}
ENERGY_TYPES = {"electricity"}


def categorize(activity_type: str) -> str:
    if activity_type in TRANSPORT_TYPES:
        return "transport"
    if activity_type in FOOD_TYPES:
        return "food"
    if activity_type in ENERGY_TYPES:
        return "energy"
    return "other"


def parse_date_str(d: str) -> date:
    return datetime.strptime(d, "%Y-%m-%d").date()


def compute_emission_kg(activity: Dict) -> Tuple[float, Dict]:
    """
    Compute emission and return (kg, normalized_data)
    activity fields expected:
    - type: one of 'car','flight','bus','train','electricity','beef_meal','vegetarian_meal'
    - date: YYYY-MM-DD
    - depending on type:
        distance_km for transport
        kwh for electricity
        quantity for meals (default 1)
    """
    a_type = activity.get("type")
    data = activity.get("data", {})

    if a_type == "car":
        km = float(data.get("distance_km", 0))
        return km * CAR_PETROL_PER_KM, {"distance_km": km}
    if a_type == "flight":
        km = float(data.get("distance_km", 0))
        return km * FLIGHT_SHORT_HAUL_PER_KM, {"distance_km": km}
    if a_type == "bus":
        km = float(data.get("distance_km", 0))
        return km * BUS_PER_KM, {"distance_km": km}
    if a_type == "train":
        km = float(data.get("distance_km", 0))
        return km * TRAIN_PER_KM, {"distance_km": km}
    if a_type == "electricity":
        kwh = float(data.get("kwh", 0))
        return kwh * ELECTRICITY_PER_KWH, {"kwh": kwh}
    if a_type == "beef_meal":
        qty = float(data.get("quantity", 1))
        return qty * BEEF_MEAL_KG, {"quantity": qty}
    if a_type == "vegetarian_meal":
        qty = float(data.get("quantity", 1))
        return qty * VEG_MEAL_KG, {"quantity": qty}

    return 0.0, data
