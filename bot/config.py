class Config(object):
    # whole system
    debug = False

    # APIs
    api_urls = {'similarity': 'http://128.2.211.58:4455/v1/match',
                'newsapi': 'https://newsapi.org/v2/top-headlines?country=us&category=business&apiKey=185190e53e9b46e9bf441bf290c7498d'}

    api_timeout = 1.0

    # db config\
    mongo_accounts = {'dictstories': {"user": "emerg55",
                                    "pwd": "emerg55",
                                    "url": "ds113703.mlab.com",
                                    "port": "13703"
                                    }
                      }
    db_timeout = 3.0
    # redis config
    redis_ip = 'redis-12303.c61.us-east-1-3.ec2.cloud.redislabs.com'
    redis_port = 12303
    redis_password = "S2HMP31BIk0MqRl5gccjNd4ZzVFHdVo5"
    redis_db = 0
    exp_sec = 60 * 10  # expire after inactivity for 10 minutes

    # ml_server
    max_utt_len = 20
