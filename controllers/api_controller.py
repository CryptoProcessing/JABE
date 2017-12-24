import datetime
from flask import request, make_response, jsonify
from flask.views import MethodView
from. import bitcoin


def block_checker(block):

    block_object, block_height = bitcoin.get_block(block)
    # count = bitcoin.check_address_in_transaction(block_hash)
    print(block_object)


    return block_height


class BitcoinNodeApi(MethodView):
    """ Bitcoin block notification """

    def post(self, **kwargs):
        block_hash = request.data
        print(block_hash)
        block_checker(block=block_hash.decode("utf-8"))
        return make_response(jsonify('')), 200
