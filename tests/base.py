import os
from flask_testing import TestCase
from models import db
from JABE import create_app


class BaseTestCase(TestCase):
    """ Base Tests """

    def create_app(self):
        env = os.environ.get('JABE_ENV', 'test')
        app = create_app('config.%sConfig' % env.capitalize())
        return app

    def setUp(self):
        app = self.create_app()
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
