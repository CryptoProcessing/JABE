import os
from controllers.tasks import block_checker
from JABE import create_app, make_celery


env = os.environ.get('JABE_ENV', 'prod')
celery = make_celery(create_app('config.%sConfig' % env.capitalize(), register_blueprints=False))

