import os

from flask_restful import Resource, request
from db.database import init_db

class Status(Resource):

    def get(self):
        return {"status": "Что-то работает..."}

    def delete(self):
        """Сброс бд для тестирования"""
        data = request.json
        if data.get("reinit") == 1:
            os.remove("application.db")
            init_db()
        return {"status": "database recreated"}
