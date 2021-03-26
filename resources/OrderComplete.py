import arrow

from flask import abort, make_response
from flask_restful import Resource, request
from pydantic import ValidationError

from controller.controllers import complete_order
from models.OrderModel import OrderCompleteModel


def validate_complete_data(complete_data: dict):
    try:
        OrderCompleteModel(**complete_data)
    except ValidationError as e:
        abort(make_response(e.errors(), 400))
    return complete_data


class OrderComplete(Resource):

    def post(self):
        data = validate_complete_data(request.json)

        courier_id = data['courier_id']
        order_id = data['order_id']
        delivered_on = arrow.get(data['complete_time']).datetime.utcnow()

        order_completed = complete_order(
            courier_id=courier_id,
            order_id=order_id,
            delivered_on=delivered_on
        )

        if not order_completed:
            return {"error": "El problema..."}, 400
        else:
            return {'order_id': order_id}
