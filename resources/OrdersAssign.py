from flask_restful import Resource, request
from controllers import assign_orders


class OrdersAssign(Resource):

    def post(self):
        courier_id = request.json["courier_id"]
        result_of_assignment = assign_orders(courier_id)
        return result_of_assignment, 200
