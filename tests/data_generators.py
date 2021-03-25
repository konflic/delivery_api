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


def random_couriers_sample(amount=1):
    return {"data": [create_random_courier() for _ in range(amount)]}
