from flask import Flask, Blueprint
from models import db
from extensions import rest_api, celery
from controllers.api_controller import BitcoinNodeApi, ApiFindPrevious
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session


def create_app(object_name):

    app = Flask(__name__)
    app.config.from_object(object_name)

    db.app = app
    db.init_app(app)
    # init celery
    celery.init_app(app)

    # define the API resources
    block_notify_view = BitcoinNodeApi.as_view('block_notify_view')
    find_previous = ApiFindPrevious.as_view('find_previous')

    bitcoin_blueprint = Blueprint('bitcoin', __name__)
    # add Rules for API Endpoints
    bitcoin_blueprint.add_url_rule(
        '/btc/block',
        view_func=block_notify_view,
        methods=['POST']
    )
    bitcoin_blueprint.add_url_rule(
        '/btc/find-previous',
        view_func=find_previous,
        methods=['GET']
    )

    app.register_blueprint(bitcoin_blueprint, url_prefix='/api/v1')

    rest_api.init_app(app)

    return app


if __name__ == '__main__':
    app = app = create_app('project.config.ProdConfig')
    app.run()
