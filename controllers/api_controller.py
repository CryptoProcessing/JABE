import datetime
from flask import request, make_response, jsonify
from flask.views import MethodView
from . import bitcoin
from .save_to_db import block_to_db, get_max_height
from .find_previous import find_previous_in_block
from extensions import celery
from models import Lock


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


class BitcoinNodeApi(MethodView):
    """ Bitcoin block notification """

    def post(self, **kwargs):
        block_hash = request.data
        print(block_hash)
        if not Lock.query.all():
            block_checker()
        else:
            print("Locked")
        return make_response(jsonify('')), 200


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


class ApiFindPrevious(MethodView):
    """ Bitcoin block notification """

    def get(self, **kwargs):
        find_previous()

        return make_response(jsonify('')), 200
