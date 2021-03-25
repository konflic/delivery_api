import sqlalchemy

from flask import abort, make_response, Response
from flask_restful import Resource, request
from controllers import hire_couriers
from pydantic import ValidationError

from models.CourierModel import CourierModel


def validate_couriers(couriers_data):
    broken = []
    for courier in couriers_data:
        try:
            r = CourierModel(**courier)
            print(r)
        except ValidationError as e:
            broken.append(courier)
    if broken:
        abort(make_response({"validation_error": {"couriers": [{"id": c["courier_id"]} for c in broken]}}, 400))
    return couriers_data


class Couriers(Resource):

    def post(self):
        data = validate_couriers(request.json["data"])

        try:
            return hire_couriers(data), 201
        except sqlalchemy.exc.IntegrityError:
            abort(400, "Params not unique")
