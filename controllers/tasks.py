import os
import datetime
from JABE import create_app, make_celery
from controllers import bitcoin
from controllers.save_to_db import block_to_db, get_max_height
from controllers.find_previous import find_previous_in_block
from controllers.repair_transactions import repair_transactions
from extensions import redis_store


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

        # update max height
        db_block_height = get_max_height()

    print('all blocks parsed')


@celery.task()
def task_repair_transactions():
    db_block_height = 180000

    blockcount = 350000  #bitcoin.get_blockcount()

    while blockcount > db_block_height:
        db_block_height += 1
        block_hash = bitcoin.get_block_hash(db_block_height)
        block_object, block_height = bitcoin.get_block(block_hash)

        repair_transactions(block_object, block_height)


@celery.task()
def block_checker(block_hash):
    # maybe parser in progress
    parced_now = redis_store.get('parsed_block')
    if parced_now == b'parsing':
        print('Already parsing...')
        return None

    redis_store.set('parsed_block', 'parsing')

    find_block_info()

    redis_store.delete('parsed_block')


@celery.task()
def find_previous(start_block, block_shift):

    db_block_height = int(start_block)
    # assert 0==1

    if block_shift:
        blockcount = db_block_height + int(block_shift)
    else:
        blockcount = get_max_height()

    while blockcount > db_block_height:
        db_block_height += 1
        block_hash = bitcoin.get_block_hash(db_block_height)
        block_object, block_height = bitcoin.get_block(block_hash)
        tr_count = find_previous_in_block(block_object)

        print('previous for {} txs {} - {}'.format(block_height, tr_count,  datetime.datetime.now()))


