from flask import request, make_response, jsonify
from flask.views import MethodView
from models import Lock, TxOut
from controllers.tasks import block_checker


class BitcoinNodeApi(MethodView):
    """ Bitcoin block notification """

    def post(self, **kwargs):
        block_hash = request.data
        print(block_hash)
        if not Lock.query.all():
            block_checker.delay()
        else:
            print("Locked")
        return make_response(jsonify('')), 200


class UnspentApi(MethodView):

    def json_unspent(self, unspent):
        return {'unspent_outputs': [
            {
                'value': int(u.coin_value),
                'script': u.script,
                'tx_output_n': u.position,
                'tx_hash_big_endian': u.transaction.hash
            } for u in unspent]}

    def get(self, **kwargs):
        query_string = request.args
        address = query_string.get('address')

        tx_outs = TxOut()
        unspents = tx_outs.get_unspents(address=address)

        return make_response(jsonify(self.json_unspent(unspents))), 200
