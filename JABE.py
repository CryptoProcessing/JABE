from flask import Flask, Blueprint
# from models import db
from extensions import rest_api
from controllers.api_controller import Api


def create_app(object_name):

    app = Flask(__name__)
    app.config.from_object(object_name)

    # db.app = app
    # db.init_app(app)

    auth_blueprint = Blueprint('auth', __name__)

    # define the API resources
    pricelast_view = Api.as_view('last_price')

    # add Rules for API Endpoints
    auth_blueprint.add_url_rule(
        '/hello',
        view_func=pricelast_view,
        methods=['GET']
    )

    app.register_blueprint(auth_blueprint, url_prefix='/api/v1')

    rest_api.init_app(app)

    return app


if __name__ == '__main__':
    app = app = create_app('project.config.ProdConfig')
    app.run()
