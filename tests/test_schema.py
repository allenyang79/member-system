# -*- coding: utf-8 -*-
import os
import sys
import unittest

from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

import json

from app.schema import schema


class SchemaTestCase(unittest.TestCase):

    def create_db(self, name):
        db_path = os.path.join(os.path.dirname(__file__),'db/%s.json' % name)
        setattr(self, '%s_db' % name, TinyDB(db_path, storage=CachingMiddleware(JSONStorage)))
        return getattr(self, '%s_db' % name)

    def remove_db(self, name):
        db_path = os.path.join(os.path.dirname(__file__),'db/%s.json' % name)
        if os.path.isfile(db_path):
            os.remove(db_path)

    def setUp(self):
        self.create_db('user')

    def tearDown(self):
        self.remove_db('user')

    #def test_schema(self):
    #    print "test_schema"
    #    query = '''
    #        query SayHello {
    #          hello
    #          ping(to:"peter")
    #        }
    #    '''
    #    result = schema.execute(query)
    #    print json.dumps(result.data)

    def test_create_person(self):
        query = '''
            mutation myFirstMutation {
                createPerson(name:"Peter", gender: male) {
                    ok
                    message
                    result {
                        name
                        gender
                    }

                }
            }
        '''
        result = schema.execute(query)
        if result.errors:
            print result.errors
        else:
            print json.dumps(result.data, indent=2)


    def test_update_person(self):
        query = '''
            query {
                findPerson {
                    name
                    gender
                }
            }
        '''
        result = schema.execute(query)
        if result.errors:
            print result.errors
        else:
            print json.dumps(result.data, indent=2)

    def test_list_person(self):
        pass

    def test_find_person(self):
        pass

    def test_link_person(self):
        pass

    def test_update_persons_group(self):
        pass


    def test_create_group(self):
        pass

    def test_update_group(self):
        pass

    def test_list_group(self):
        pass



