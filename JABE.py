from flask import Flask, Blueprint
from models import db
from extensions import rest_api, redis_store

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

    redis_store.init_app(app)
    redis_store.set('parsed_block', '')

    if register_blueprints:
        from controllers.api_controller import UnspentApi, BalanceApi

        unspent_view = UnspentApi.as_view('unspent_view')
        balance_view = BalanceApi.as_view('balance_view')

        blockchain_blueprint = Blueprint('blockchain', __name__)
        # add Rules for API Endpoints
        blockchain_blueprint.add_url_rule(
            '/unspent',
            view_func=unspent_view,
            methods=['GET']
        )
        blockchain_blueprint.add_url_rule(
            '/balance',
            view_func=balance_view,
            methods=['GET']
        )
        app.register_blueprint(blockchain_blueprint, url_prefix='/api/v1')
        rest_api.init_app(app)

    return app


if __name__ == '__main__':
    app = create_app('project.config.ProdConfig')
    app.run()
