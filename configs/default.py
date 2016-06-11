import os, sys

config = {
    'MODE': 'development',
    #'DB_PATH': os.path.join(os.path.dirname(__file__),'../db')
    'MONGO_DSN': 'mongodb://localhost:27017',
    'DB_NAME': 'church'
}

