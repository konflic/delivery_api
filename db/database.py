import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

engine = create_engine('sqlite:///{}'.format(os.getenv("DB_NAME")), convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    from db.models import Courier, AssignedOrder, Region, WorkingHour, Order, DeliveryHour
    Base.metadata.create_all(bind=engine)
    print("Created database: '{}'".format(os.getenv("DB_NAME")))
