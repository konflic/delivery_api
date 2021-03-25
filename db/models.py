import arrow

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, func, select, distinct
from sqlalchemy.orm import relationship
from db.database import Base


class Courier(Base):
    __tablename__ = 'couriers'

    id = Column(Integer, primary_key=True)
    courier_id = Column(Integer, nullable=False, unique=True)
    rating = relationship("CourierRating")
    earnings = relationship("CourierEarning")
    hired_on = Column(DateTime, default=func.now())
    courier_type = Column(String, nullable=False)
    max_weight = Column(Float, nullable=False)
    weight_taken = Column(Float, default=0)
    regions = relationship("Region")
    working_hours = relationship("WorkingHour")
    last_delivery = Column(DateTime, default=None)

    def get_regions(self):
        return [region.region_id for region in self.regions]

    def get_working_hours(self):
        return [hours.working_hour for hours in self.working_hours]

    def get_rating(self):
        rate_list = tuple(item.rating for item in self.rating)
        return None if not len(rate_list) else rate_list[0]

    def get_earnings(self):
        return sum(tuple(item.amount for item in self.earnings))

    @property
    def available_weight(self):
        return self.max_weight - self.weight_taken

    def __init__(self, courier_id, courier_type, available_weight):
        self.courier_id = courier_id
        self.courier_type = courier_type
        self.max_weight = available_weight

    def __repr__(self):
        return '<Courier %r>' % (self.courier_id)


class CourierEarning(Base):
    __tablename__ = 'couriers_earnings'

    id = Column(Integer, primary_key=True)
    courier_id = Column(Integer, ForeignKey("couriers.courier_id"))
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    amount = Column(Float, nullable=False)

    def __init__(self, courier_id, order_id, amount):
        self.courier_id = courier_id
        self.order_id = order_id
        self.amount = amount


class CourierRating(Base):
    __tablename__ = 'couriers_rating'

    id = Column(Integer, primary_key=True)
    courier_id = Column(Integer, ForeignKey("couriers.courier_id"), unique=True)
    rating = Column(Float, default=None)
    updated = Column(DateTime, nullable=False)

    @staticmethod
    def courier_rating_exist(courier_id):
        return CourierRating.query.filter(CourierRating.courier_id == courier_id).all()

    def __init__(self, courier_id, rating, updated):
        self.courier_id = courier_id
        self.rating = rating
        self.updated = updated


class AssignedOrder(Base):
    __tablename__ = 'assigned_orders'

    id = Column(Integer, primary_key=True)
    courier_id = Column(Integer, ForeignKey("couriers.courier_id"))
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    assign_time = Column(DateTime, default=arrow.utcnow().datetime)

    def remove(self, order_id):
        self.filter(self.order_id == order_id).delete()

    def __init__(self, courier_id, order_id):
        self.courier_id = courier_id
        self.order_id = order_id


class DeliveredOrder(Base):
    __tablename__ = 'delivered_orders'

    id = Column(Integer, primary_key=True)
    courier_id = Column(Integer, ForeignKey("couriers.courier_id"))
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    region_id = Column(Integer, ForeignKey("regions.region_id"))
    delivered_on = Column(DateTime, nullable=False)
    delivery_time = Column(Integer, nullable=False)

    @staticmethod
    def get_region_avg_delivery_time(region_id):
        return DeliveredOrder.query.with_entities(
            func.avg(DeliveredOrder.delivery_time)
        ).filter(DeliveredOrder.region_id == region_id).one()[0]

    def get_all_regions(self):
        return set(el[0] for el in self.query.values(DeliveredOrder.region_id))

    def get_avg_for_regions(self):
        for region in self.get_all_regions():
            print(DeliveredOrder.get_region_avg_delivery_time(region))

    def __init__(self, courier_id, order_id, delivered_on, delivery_time, region_id):
        self.courier_id = courier_id
        self.order_id = order_id
        self.delivered_on = delivered_on
        self.delivery_time = delivery_time
        self.region_id = region_id


class Region(Base):
    __tablename__ = 'regions'

    id = Column(Integer, primary_key=True)
    courier_id = Column(Integer, ForeignKey("couriers.courier_id"))
    region_id = Column(Integer, nullable=False)

    def __init__(self, courier_id, region_id):
        self.courier_id = courier_id
        self.region_id = region_id


class WorkingHour(Base):
    __tablename__ = 'working_hours'

    id = Column(Integer, primary_key=True)
    courier_id = Column(Integer, ForeignKey("couriers.courier_id"))
    working_hour = Column(Integer, nullable=False)

    def __init__(self, courier_id, working_hour):
        self.courier_id = courier_id
        self.working_hour = working_hour


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, nullable=False, unique=True)
    weight = Column(Float, nullable=False)
    region_id = Column(Integer, nullable=False)
    delivery_hours = relationship("DeliveryHour")
    delivered = Column(Boolean, default=False)
    assigned = Column(Boolean, default=False)

    def set_assigned(self):
        self.assigned = True

    def set_delivered(self):
        self.delivered = True

    def get_delivery_hours(self):
        return [hours.delivery_hour for hours in self.delivery_hours]

    def __init__(self, order_id, weight, region_id):
        self.order_id = order_id
        self.weight = weight
        self.region_id = region_id


class DeliveryHour(Base):
    """Не знаю зачем эта таблица, упустил момент когда она появилась"""
    __tablename__ = 'delivery_hours'

    id = Column(Integer, primary_key=True)
    delivery_hour = Column(String, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.order_id"))

    def __init__(self, order_id, delivery_hour):
        self.order_id = order_id
        self.delivery_hour = delivery_hour
