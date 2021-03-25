import arrow

from flask_restful import Resource, request
from controller.controllers import complete_order


class OrderComplete(Resource):

    def post(self):
        data = request.json

        courier_id = data['courier_id']
        order_id = data['order_id']
        delivered_on = arrow.get(data['complete_time']).datetime.utcnow()

        order_completed = complete_order(
            courier_id=courier_id,
            order_id=order_id,
            delivered_on=delivered_on
        )

        if not order_completed:
            return {}, 400
        else:
            return {'order_id': order_id}
