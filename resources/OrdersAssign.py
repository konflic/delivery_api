from flask import abort
from flask_restful import Resource, request
from controller.controllers import assign_orders


class OrdersAssign(Resource):

    def post(self):
        courier_id = request.json["courier_id"]
        result_of_assignment = assign_orders(courier_id)

        if not result_of_assignment:
            abort(400)

        return result_of_assignment, 200
