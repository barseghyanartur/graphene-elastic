# import datetime
#
# __title__ = "graphene_elastic.helpers"
# __author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
# __copyright__ = "2019 Artur Barseghyan"
# __license__ = "GPL-2.0-only OR LGPL-2.1-or-later"
# __all__ = ("DictionaryProxy",)
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
