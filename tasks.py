import os
import datetime
from flask import current_app
from JABE import create_app, make_celery
from controllers import bitcoin
from controllers.save_to_db import block_to_db, get_max_height
from controllers.find_previous import find_previous_in_block
from models import Lock


env = os.environ.get('JABE_ENV', 'dev')
celery = make_celery(create_app('config.%sConfig' % env.capitalize(), register_blueprints=False))


def find_block_info():

    db_block_height = get_max_height()

    blockcount = bitcoin.get_blockcount()

    while blockcount > db_block_height:
        db_block_height += 1
        block_hash = bitcoin.get_block_hash(db_block_height)
        block_object, block_height = bitcoin.get_block(block_hash)
        tr_count = block_to_db(block_object, block_height)

        print(block_height, tr_count,  datetime.datetime.now())


@celery.task()
def block_checker():
    lock = Lock(lock=True)
    lock.save()

    find_block_info()

    Lock.query.delete()


@celery.task()
def find_previous():

    db_block_height = 280000
    # assert 0==1
    blockcount_in_db = get_max_height()

    while blockcount_in_db > db_block_height:
        db_block_height += 1
        block_hash = bitcoin.get_block_hash(db_block_height)
        block_object, block_height = bitcoin.get_block(block_hash)
        tr_count = find_previous_in_block(block_object)

        print('previous for {} txs {} - {}'.format(block_height, tr_count,  datetime.datetime.now()))


