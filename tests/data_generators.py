import random

REGIONS = list(range(1, 30))

__all__ = ["create_random_courier", "random_couriers_sample"]


def create_random_courier():
    return {
        "courier_id": random.randint(1, 999999),
        "courier_type": random.choice(["foot", "bike", "car"]),
        "regions": [random.choice(REGIONS) for _ in range(random.randint(1, 4))],
        "working_hours": [random.choice(["11:35-14:05", "09:00-11:00", "09:00-18:00"])]
    }


def create_random_order():
    return {
        "order_id": random.randint(1, 999999),
        "weight": random.choice([0.02, 0.5, 1, 1.5, 10, 15, 20, 30, 49.9]),
        "region": random.choice(REGIONS),
        "delivery_hours": [random.choice(["11:35-14:05", "09:00-11:00", "09:00-18:00"])]
    }


def random_couriers_sample(amount=1):
    return {"data": [create_random_courier() for _ in range(amount)]}


def manual_courier(courier_id: int, courier_type: str, regions: list, working_hours: list):
    return {"data": [
        {
            "courier_id": courier_id,
            "courier_type": courier_type,
            "regions": regions,
            "working_hours": working_hours
        }
    ]}


def manual_order(order_id: int, weight: float, region: int, delivery_hours: list):
    return {"data": [
        {
            "order_id": order_id,
            "weight": weight,
            "region": region,
            "delivery_hours": delivery_hours
        }
    ]}
