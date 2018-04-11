from flask import Flask, Blueprint
from models import db
from extensions import rest_api
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from celery import Celery


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


def create_app(object_name, register_blueprints=True):

    app = Flask(__name__)
    app.config.from_object(object_name)

    db.app = app
    db.init_app(app)

    if register_blueprints:
        from controllers.api_controller import BitcoinNodeApi
        # define the API resources
        block_notify_view = BitcoinNodeApi.as_view('block_notify_view')

        bitcoin_blueprint = Blueprint('bitcoin', __name__)
        # add Rules for API Endpoints
        bitcoin_blueprint.add_url_rule(
            '/btc/block',
            view_func=block_notify_view,
            methods=['POST']
        )

        app.register_blueprint(bitcoin_blueprint, url_prefix='/api/v1')

        rest_api.init_app(app)

    return app


if __name__ == '__main__':
    app = app = create_app('project.config.ProdConfig')
    app.run()
