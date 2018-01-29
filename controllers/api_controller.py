from flask import request, make_response, jsonify
from flask.views import MethodView
from models import Lock
from tasks import block_checker, find_previous


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


class ApiFindPrevious(MethodView):
    """ Bitcoin block notification """

    def get(self, **kwargs):
        find_previous.delay()

        return make_response(jsonify('')), 200
