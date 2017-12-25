import datetime
from flask import request, make_response, jsonify
from flask.views import MethodView
from . import bitcoin
from .save_to_db import block_to_db
from extensions import celery


@celery.task()
def block_checker(block):

    block_object, block_height = bitcoin.get_block(block)
    # count = bitcoin.check_address_in_transaction(block_hash)
    block_to_db(block_object, block_height)
    print(block_object)

    return block_height


class BitcoinNodeApi(MethodView):
    """ Bitcoin block notification """

    def post(self, **kwargs):
        block_hash = request.data
        print(block_hash)
        block_checker.delay(block=block_hash.decode("utf-8"))
        return make_response(jsonify('')), 200
