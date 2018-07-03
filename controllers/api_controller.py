from flask import request, make_response, jsonify
from flask.views import MethodView
from models import TxOut, Address


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


class BalanceApi(MethodView):

    def json_balance(self, balance, tx_count):
        return {
                'final_balance': balance,
                'n_tx': tx_count
            }

    def get(self, **kwargs):
        query_string = request.args
        address = query_string.get('address')

        address_obj = Address()

        balance, tx_count = address_obj.get_balance(address=address)

        return make_response(jsonify({address: self.json_balance(balance, tx_count)})), 200
