# -*- coding: utf-8 -*-

from werkzeug.routing import BaseConverter
import json
import bson
import bson.json_util


class BSONJSONEncoder(json.JSONEncoder):
    def default(self, o):
        try:
            return bson.json_util.default(o)
        except Exception as e:
            return super(BSONJSONEncoder, self).default(o)


class BSONJSONDecoder(json.JSONDecoder):
    """ Do nothing custom json decoder """

    def __init__(self, *args, **kargs):
        _ = kargs.pop('object_hook', None)
        super(BSONJSONDecoder, self).__init__(object_hook=bson.json_util.object_hook, *args, **kargs)


class ObjectIdConverter(BaseConverter):
    def to_python(self, value):
        return bson.ObjectId(value)

    def to_url(self, value):
        return BaseConverter.to_url(value['$oid'])
