import datetime
import json

from elasticsearch_dsl import InnerDoc, Document, AttrDict, AttrList
from graphene.types.json import JSONString as OriginalJSONString

__title__ = 'graphene_elastic.types.json_string'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2019 Artur Barseghyan'
__license__ = 'GPL-2.0-only OR LGPL-2.1-or-later'
__all__ = (
    'JSONString',
    'to_serializable',
)


def to_serializable(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
    elif isinstance(o, (InnerDoc, Document)):
        return o.to_dict()
    elif isinstance(o, AttrList):
        return [to_serializable(_l) for _l in o._l_]
    elif isinstance(o, AttrDict):
        return o.to_dict()
    elif isinstance(o, list):
        return [to_serializable(_l) for _l in o]

    return o


class JSONString(OriginalJSONString):
    @staticmethod
    def serialize(dt):
        # return to_serializable(dt)
        return json.loads(json.dumps(dt, default=to_serializable))
