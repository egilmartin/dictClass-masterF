import cPickle as pkl

import redis

from bot.config import Config
from bot.utils import InvalidUsage


class RedisAPI(object):
    def __init__(self, exp_sec=None):
        self.client = redis.StrictRedis(host=Config.redis_ip,
                                        port=Config.redis_port,
                                        db=Config.redis_db,
                                        password=Config.redis_password)
        if exp_sec is None:
            self.exp_sec = Config.exp_sec
        else:
            self.exp_sec = exp_sec

    def set(self, key, value):
        """
        :param key:
        :param value:
        :return:
        """
        if type(value) is str:
            return self.client.set(key, value, ex=self.exp_sec)
        else:
            try:
                encoding = pkl.dumps(value)
            except Exception as e:
                raise InvalidUsage("Server Cache Error", status_code=500)
            return self.client.set(key, encoding, ex=self.exp_sec)

    def refresh(self, key):
        """

        :param key:
        :return:
        """
        self.client.expire(key, self.exp_sec)

    def get(self, key, use_pkl=True):
        """

        :param key:
        :param use_pkl:
        :return:
        """
        value = self.client.get(key)
        if use_pkl:
            try:
                return pkl.loads(value)
            except Exception as e:
                raise InvalidUsage("Server Cache Error", status_code=500)
        else:
            return value

    def exists(self, key):
        """

        :param key:
        :return:
        """
        return self.client.exists(key)

    def delete(self, key):
        """
        :param key:
        :return:
        """
        self.client.delete(key)
