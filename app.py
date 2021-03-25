import os

from flask import Flask
from flask_restful import Api

from resources import Orders
from resources import Couriers
from resources import CouriersId
from resources import OrdersAssign
from resources import OrdersComplete
from resources import Status

from db.database import db_session
from db.database import init_db

app = Flask(__name__)
api = Api(app)

init_db()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


api.add_resource(Couriers, '/couriers')
api.add_resource(CouriersId, '/couriers/<int:courier_id>')
api.add_resource(Orders, '/orders')
api.add_resource(OrdersAssign, '/orders/assign')
api.add_resource(OrdersComplete, '/orders/complete')
api.add_resource(Status, '/status')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=os.getenv("PORT", 5000), debug=True)  # TODO: Разобраться с дебагом
