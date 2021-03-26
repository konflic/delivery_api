import arrow

from datetime import datetime
from db.database import db_session
from controller.constants import PAY_COEFFICIENTS, BASE_PAY, WEIGHTS, SECONDS_IN_HOUR
from db.models import Courier, Region, WorkingHour, Order, \
    DeliveryHour, AssignedOrder, DeliveredOrder, CourierRating, \
    CourierEarning


def hire_couriers(couriers: list):
    ids = {"couriers": []}

    for courier in couriers:
        hours = courier["working_hours"]
        regions = courier["regions"]
        courier_id = courier["courier_id"]
        courier_type = courier["courier_type"]

        db_session.add(
            Courier(
                courier_id=courier["courier_id"],
                courier_type=courier_type,
                available_weight=WEIGHTS[courier_type]
            )
        )

        for region_id in regions:
            db_session.add(Region(courier_id=courier_id, region_id=region_id))

        for hour in hours:
            db_session.add(WorkingHour(courier_id=courier_id, working_hour=hour))

        ids["couriers"].append({"id": courier_id})

    db_session.commit()
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
    return Courier.get_courier(courier_id)


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
    assigned_order = AssignedOrder.query.filter(
        AssignedOrder.order_id == order_id and AssignedOrder.courier_id == courier_id
    ).first()

    if assigned_order is None:
        return False
    last_delivery_time = get_courier(courier_id).last_delivery

    # Если курьер ничего не доставлял, то расчёт от назначения заказа
    if last_delivery_time is None:
        delivery_time = delivered_on - assigned_order.assign_time
    else:
        delivery_time = delivered_on - last_delivery_time

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
            amount=BASE_PAY * PAY_COEFFICIENTS[get_courier(courier_id).courier_type]
        )
    )

    get_courier(courier_id).last_delivery = delivered_on

    db_session.commit()
    return True


def assign_orders(courier_id):
    courier_data = get_courier(courier_id)
    if courier_data is None:
        return False

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
    if not courier.working_hours:
        return False
    if not order.region_id in courier.get_regions():
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


def intervals_has_overlap(courier_time: tuple, order_time: tuple):
    # Left overlap
    if courier_time[0] <= order_time[0] <= courier_time[1] and order_time[0] <= courier_time[1] <= order_time[1]:
        return True
    # Right overlap
    elif order_time[0] <= courier_time[0] <= order_time[1]:
        return True
    # Outer overlap
    elif order_time[0] <= courier_time[0] and courier_time[1] <= order_time[1]:
        return True
    # Inner overlap
    elif courier_time[0] <= order_time[0] and courier_time[1] >= order_time[1]:
        return True
    return False


def _make_interval(string_interval, fmt="h:m"):
    return tuple(arrow.get(t, fmt) for t in string_interval.split("-"))


def delivery_time_fits(courier_time, order_hours):
    courier_intervals = tuple(_make_interval(i) for i in courier_time)
    order_intervals = tuple(_make_interval(i) for i in order_hours)

    for courier_interval in courier_intervals:
        for order_interval in order_intervals:
            if intervals_has_overlap(courier_interval, order_interval):
                return True

    return False


def update_courier(courier_id, fields_to_update):
    for field in fields_to_update:
        if field == "regions":
            Region.clear_courier_regions(courier_id=courier_id)
            for region_id in fields_to_update[field]:
                db_session.add(Region(courier_id=courier_id, region_id=region_id))

        if field == "working_hours":
            WorkingHour.clear_courier_working_hours(courier_id=courier_id)
            for w_hour in fields_to_update[field]:
                db_session.add(WorkingHour(courier_id=courier_id, working_hour=w_hour))

        if field == "courier_type":
            get_courier(courier_id).courier_type = fields_to_update[field]

    db_session.commit()
    return get_courier(courier_id)


def update_courier_orders(courier: Courier):
    assigned_orders = AssignedOrder.query.filter(AssignedOrder.courier_id == courier.courier_id).all()

    for order in assigned_orders:
        if not order_fits_courier(courier, get_order(order.order_id)):
            courier.weight_taken = courier.weight_taken - get_order(order_id=order.order_id).weight
            get_order(order.order_id).set_assigned(False)
            AssignedOrder.query.filter(AssignedOrder.order_id == order.order_id).delete()

    db_session.commit()
