# -*- coding: utf-8 -*-
# Author: Kyusong Lee
# Date: 8/27/18

import logging

from flask import Flask, jsonify, request
from flask_cors import CORS

from bot.game import Game
from bot.utils import InvalidUsage


class Guard(object):
    def __init__(self):
        self.db_client = None  # Mongo API(Config.graph_db)

    def check(self, api_key):
        """
        :param api_key: a string input
        :return: {"graph_id", "branch":master}, or None if failed
        """
        """
        doc = self.db_client.find_document(Config.graph_db, Config.key_collection, 
                                           "key", api_key)
        if bool(doc) and "graph_id" in doc and "branch" in doc:
            return {"graph_id": doc["graph_id"], "branch": doc["branch"]}
        return None
        """
        return True


class QAConnector(object):
    """
    A connector class that connects a Qubot to various user interface.
    """

    @staticmethod
    def handle_invalid_usage(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    def __init__(self, debug):
        self.app = Flask(__name__)
        self.app.debug = debug
        CORS(self.app)

        # backend interfaces
        self.game = Game()
        self.guard = Guard()
        self.logger = logging.getLogger(__name__)

        # add routes to flask App
        self.app.add_url_rule('/init', view_func=self.bot_init, methods=['POST'])
        self.app.add_url_rule('/next', view_func=self.bot_next, methods=['POST'])
        self.app.register_error_handler(InvalidUsage, self.handle_invalid_usage)

    def bot_init(self):
        """
        :return: bot response
        {"sessionID":"USR_1234", "timeStamp": "yyyy-MM-dd'T'HH-mm-ss.SSS" }
        """
        data = request.get_json()

        if 'sessionID' not in data:
            raise InvalidUsage('Need to enter \'context\' as one of the fields in the JSON data')

        payload = self.game.start(data["sessionID"])
        return jsonify(payload)

    def bot_next(self):
        """
        :return: bot response
        { "sessionID": "USR_1234", "sys": "This word starts with A", "version": "1.0-xxx", "timeStamp": "yyyy-MM-dd'T'HH-mm-ss.SSS", "terminal": false }

        """
        data = request.get_json()
        if 'sessionID' not in data:
            raise InvalidUsage('Need to enter \'context\' as one of the fields in the JSON data')

        payload = self.game.response(data["sessionID"], data['text'])
        # Question for Kyusong - if this is just handling data['text'] wouldn't we need to add more fields to have content for new divs at this point
        return jsonify(payload)
