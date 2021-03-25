import arrow

from datetime import datetime
from db.database import db_session
from db.models import Courier, Region, WorkingHour, Order, DeliveryHour, AssignedOrder, DeliveredOrder, CourierRating, \
    CourierEarning

weights = {
    "foot": 10,
    "bike": 15,
    "car": 50
}

pays = {
    "foot": 2,
    "bike": 5,
    "car": 9
}

BASE_PAY = 500
SECONDS_IN_HOUR = 60 * 60


def hire_couriers(couriers: list):
    ids = {"couriers": []}

    for courier in couriers:
        hours = courier["working_hours"]
        regions = courier["regions"]
        courier_id = courier["courier_id"]
        courier_type = courier["courier_type"]

        db_session.add(Courier(courier_id=courier["courier_id"], courier_type=courier_type,
                               available_weight=weights[courier_type]))

        for region_id in regions:
            db_session.add(Region(courier_id=courier_id, region_id=region_id))

        for hour in hours:
            db_session.add(WorkingHour(courier_id=courier_id, working_hour=hour))

        db_session.commit()
        ids["couriers"].append({"id": courier_id})

    return ids


def add_orders(orders: list):
    ids = {"orders": []}

    for order in orders:
        order_id = order["order_id"]
        weight = order["weight"]
        delivery_hours = order["delivery_hours"]
        region_id = order["region"]

        db_session.add(Order(order_id=order_id, weight=weight, region_id=region_id))

        for delivery_hour in delivery_hours:
            db_session.add(DeliveryHour(order_id=order_id, delivery_hour=delivery_hour))

        ids["orders"].append({"id": order_id})
        db_session.commit()

    return ids


def get_courier(courier_id) -> Courier:
    return Courier.query.filter(Courier.courier_id == courier_id).first()


def get_order(order_id) -> Order:
    return Order.query.filter(Order.order_id == order_id).first()


def get_not_assigned_orders():
    return Order.query.filter(Order.assigned == False).all()


def calculate_courier_rating():
    regions = DeliveredOrder.get_all_regions()

    count_regions = len(regions)
    total_avg = 0

    for region in regions:
        total_avg += DeliveredOrder.get_region_avg_delivery_time(region)

    if not total_avg:
        return None

    return round((SECONDS_IN_HOUR - min(total_avg / count_regions, SECONDS_IN_HOUR)) / (SECONDS_IN_HOUR) * 5, 2)


def update_courier_rating(courier_id, new_rating):
    if CourierRating.courier_rating_exist(courier_id):
        db_session.query(CourierRating) \
            .filter(CourierRating.courier_id == courier_id) \
            .update({CourierRating.rating: new_rating})
    else:
        db_session.add(
            CourierRating(
                courier_id=courier_id,
                rating=new_rating,
                updated=arrow.utcnow().datetime
            )
        )
    db_session.commit()


def complete_order(courier_id, order_id, delivered_on: datetime):
    """Царь-метод завершения заказа"""
    assigned_order = AssignedOrder.query.filter(AssignedOrder.order_id == order_id).first()

    if assigned_order is None:
        return False

    delivery_time = delivered_on - assigned_order.assign_time

    db_session.add(
        DeliveredOrder(
            courier_id,
            order_id,
            region_id=get_order(order_id).region_id,
            delivered_on=delivered_on,
            delivery_time=int(delivery_time.total_seconds())
        )
    )

    get_order(order_id).set_delivered()
    db_session.delete(assigned_order)

    update_courier_rating(courier_id, calculate_courier_rating())

    db_session.add(
        CourierEarning(
            courier_id=courier_id,
            order_id=order_id,
            amount=BASE_PAY * pays[get_courier(courier_id).courier_type]
        )
    )

    get_courier(courier_id).last_delivery = delivered_on

    db_session.commit()
    return True


def assign_orders(courier_id):
    courier_data = get_courier(courier_id)
    available_orders = get_not_assigned_orders()
    assigned = []

    for order in available_orders:
        if order_fits_courier(courier_data, order):
            order_id = assign_order(courier_data, order)
            assigned.append({"id": order_id})

    result = {"orders": assigned}
    if assigned:
        result["assign_time"] = arrow.utcnow().for_json()

    return result


def order_fits_courier(courier: Courier, order: Order):
    if not order.region_id in courier.get_regions():
        return False
    if not order.delivery_hours not in courier.get_working_hours():
        return False
    if courier.available_weight < order.weight:
        return False
    if not delivery_time_fits(courier.get_working_hours(), order.get_delivery_hours()):
        return False
    return True


def assign_order(courier: Courier, order: Order):
    db_session.add(
        AssignedOrder(
            courier_id=courier.courier_id,
            order_id=order.order_id
        )
    )

    courier.weight_taken += order.weight

    order.set_assigned()
    db_session.commit()

    return order.order_id


def _make_interval(string_interval, fmt="h:m"):
    return tuple(arrow.get(t, fmt) for t in string_interval.split("-"))


def delivery_time_fits(courier_time, order_hours):
    courier_intervals = tuple(_make_interval(i) for i in courier_time)
    order_intervals = tuple(_make_interval(i) for i in order_hours)
    for courier_interval in courier_intervals:
        for order_interval in order_intervals:
            if courier_interval[0] <= order_interval[0] and courier_interval[1] >= order_interval[0]:
                return True
    return False
