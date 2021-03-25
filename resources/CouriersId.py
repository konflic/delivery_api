from flask import make_response, abort
from flask_restful import Resource, request

from controller.controllers import get_courier, update_courier, update_courier_orders


class CouriersId(Resource):

    def get(self, courier_id):
        courier = get_courier(courier_id)

        if courier:
            return {
                       "courier_id": courier.courier_id,
                       "courier_type": courier.courier_type,
                       "regions": courier.get_regions(),
                       "working_hours": courier.get_working_hours(),
                       "rating": courier.get_rating(),
                       "earnings": courier.get_earnings()
                   }, 200
        else:
            return {}, 404

    def patch(self, courier_id):
        data_to_change = request.json
        expected_fields = ["regions", "courier_type", "working_hours"]

        if not all([key in expected_fields for key in data_to_change.keys()]):
            return abort(make_response({"validation_error": "wrong fields"}, 400))

        courier = update_courier(courier_id, data_to_change)
        update_courier_orders(courier)

        return {'hello': 'test'}
