# -*- coding: utf-8 -*-
# Author: Kyusong Lee
# Date: 8/27/18

from bot.server import QAConnector

connector = QAConnector(debug=False)
application = connector.app

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5001)
