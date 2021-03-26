import sqlalchemy

from flask import abort, make_response
from flask_restful import Resource, request
from controller.controllers import hire_couriers
from pydantic import ValidationError

from models.CourierModel import CourierModel


def validate_couriers(couriers_data):
    broken = []
    for courier in couriers_data:
        try:
            CourierModel(**courier)
        except ValidationError as e:
            broken.append({"id": courier["courier_id"], "errors": e.errors()})
    if broken:
        abort(make_response({"validation_error": {"couriers": broken}}, 400))
    return couriers_data


class Couriers(Resource):

    def post(self):
        data = validate_couriers(request.json["data"])

        try:
            return hire_couriers(data), 201
        except sqlalchemy.exc.IntegrityError:
            abort(make_response({"validation_error": "Params not unique"}, 400))
