import datetime
from flask import request, make_response, jsonify
from flask.views import MethodView


class Api(MethodView):
    """ Операции с аккаунтом """

    def get(self, **kwargs):
        """
        get info

        :param kwargs:
        :return:
        """
        query_string = request.args
        ts = query_string.get('ts')
        pair = query_string.get('pair')

        result = 'there is result'

        return make_response(jsonify(result)), 200
