from flask_restful import Api
from flask_celery import Celery

celery = Celery()
rest_api = Api()

