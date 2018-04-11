from flask import request, make_response, jsonify
from flask.views import MethodView
from models import Lock
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
