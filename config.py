
class Config(object):
    SECRET_KEY = 'e21fa0fa3e0d28505c5d1b795495b2ee08420c71d036a9e2dee04cd0818ba70e'

    CELERY_BROKER_URL = 'redis://localhost:6379/0'


class ProdConfig(Config):
    MYSQL = {
        'user': 'jabe',
        'pw': 'jabe',
        'db': 'jabe_db',
        'host': 'localhost',
        'port': '3306',
    }
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % MYSQL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 299
    SQLALCHEMY_POOL_TIMEOUT = 20

class DevConfig(Config):
    DEBUG = False
    MYSQL = {
        'user': 'jabe',
        'pw': 'jabe',
        'db': 'jabe',
        'host': 'localhost',
        'port': '3306',
    }
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % MYSQL
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    DEBUG = True
    MYSQL = {
        'user': 'jabe',
        'pw': 'jabe',
        'db': 'jabe_test',
        'host': 'localhost',
        'port': '3306',
    }
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % MYSQL
    SQLALCHEMY_TRACK_MODIFICATIONS = False


