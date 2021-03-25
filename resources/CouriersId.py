from flask_restful import Resource

from controllers import get_courier

from models.OrderModel import OrderModel


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

    def patch(self, data):
        return {'hello': data}
