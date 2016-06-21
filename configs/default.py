import os, sys

config = {
    'MODE': 'development',
    #'DB_PATH': os.path.join(os.path.dirname(__file__),'../db')
    'DB_HOST': 'localhost',
    'DB_PORT': 27017,
    'DB_NAME': 'church',

    'JWT_SECRET': '1&2,s@#sa;jd9',
    'JWT_EXPIRE': 86400
}



