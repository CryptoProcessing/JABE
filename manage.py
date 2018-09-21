#!/usr/bin/env python

import os
import unittest
from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand
from controllers.tasks import find_previous, task_repair_transactions, block_checker
from JABE import create_app
from models import db

# default to dev config
env = os.environ.get('JABE_ENV', 'dev')
app = create_app('config.%sConfig' % env.capitalize())

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command("server", Server())
manager.add_command('db', MigrateCommand)


@manager.shell
def make_shell_context():
    return dict(
        app=app,

    )


@manager.option('-s', '--shift', dest='shift', default=None)
@manager.option('-b', '--startblock', dest='start_block', default=None)
def findprevious(start_block, shift):
    print(start_block)
    print('shift {}'.format(shift))
    find_previous.delay(start_block=start_block, block_shift=shift)
    return 1


@manager.command
def startparsing():
    print('start parsing')
    block_checker.delay('first_block')
    return 1


@manager.command
def repairtransactions():
    task_repair_transactions.delay()


@manager.command
def test():
    """Runs the unit tests without test coverage."""
    tests = unittest.TestLoader().discover('tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


if __name__ == "__main__":

    manager.run()
