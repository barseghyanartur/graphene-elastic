# import datetime
#
__title__ = "graphene_elastic.helpers"
__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2019 Artur Barseghyan"
__license__ = "GPL-2.0-only OR LGPL-2.1-or-later"
__all__ = (
    # "DictionaryProxy",
    "to_camel_case",
    "to_pascal_case",
)
#
#
# class DictionaryProxy(object):
#     """Dictionary proxy."""
#
#     def __init__(self, obj):
#         if callable(obj):
#             _obj = obj()
#             self.__mapping = _obj.to_dict()
#             self.__obj = _obj
#         else:
#             self.__mapping = obj.to_dict()
#             self.__obj = obj
#
#     def __getattr__(self, item):
#         if item in self.__mapping:
#             val = self.__mapping.get(item, None)
#             if isinstance(val, datetime.datetime):
#                 val = val.date()
#             return val
#
#         return getattr(self.__obj, item)
#
#     def to_dict(self):
#         """To dict.
#
#         :return:
#         """
#         return self.__mapping


def to_pascal_case(snake_str: str) -> str:
    """Convert snake_case to CapWords.

    :param snake_str:
    :return:
    """
    return snake_str.replace('_', ' ').title().replace(' ', '')


def to_camel_case(snake_str: str) -> str:
    """Convert snake_case to camelCase.

    Capitalize the first letter of each part except the first one
    with the `capitalize` method and join all the parts together.

    Adapted from this response in StackOverflow
    http://stackoverflow.com/a/19053800/1072990

    :param snake_str:
    :return:
    """
    parts = snake_str.split("_")
    return parts[0] + "".join(x.capitalize() if x else "_" for x in parts[1:])
