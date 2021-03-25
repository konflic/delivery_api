import sqlalchemy

from flask import abort, make_response
from flask_restful import Resource, request
from controller.controllers import add_orders

from models.OrderModel import OrderModel
from pydantic import ValidationError


def validate_orders(orders_data):
    broken = []
    for order in orders_data:
        try:
            OrderModel(**order)
        except ValidationError as e:
            broken.append(order)
    if broken:
        abort(make_response({"validation_error": {"orders": [{"id": o.get("order_id")} for o in broken]}}, 400))
    return orders_data


class Orders(Resource):

    def post(self):
        data = validate_orders(request.json["data"])

        try:
            return add_orders(data), 201
        except sqlalchemy.exc.IntegrityError:
            abort(400, "Params not unique")
