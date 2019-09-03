# import uuid
from graphene import (
    # ID,
    Boolean,
    DateTime,
    # Dynamic,
    # Field,
    Float,
    Int,
    # List,
    # NonNull,
    String,
    # Union,
    # is_node,
)

from elasticsearch_dsl import (
    # InnerDoc,
    field as elasticsearch_fields,
)

from .utils import import_single_dispatch, get_field_description

__title__ = "graphene_elastic.converter"
__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2019 Artur Barseghyan"
__license__ = "GPL-2.0-only OR LGPL-2.1-or-later"

singledispatch = import_single_dispatch()


class ElasticsearchConversionError(Exception):
    pass


@singledispatch
def convert_elasticsearch_field(field, registry=None):
    raise ElasticsearchConversionError(
        "Don't know how to convert the Elasticsearch field %s (%s)"
        % (field, field.__class__)
    )


@convert_elasticsearch_field.register(elasticsearch_fields.Text)
@convert_elasticsearch_field.register(elasticsearch_fields.Keyword)
def convert_field_to_string(field, registry=None):
    return String(
        description=get_field_description(field, registry),
        required=field._required,
    )


@convert_elasticsearch_field.register(elasticsearch_fields.Byte)
@convert_elasticsearch_field.register(elasticsearch_fields.Integer)
@convert_elasticsearch_field.register(elasticsearch_fields.Long)
@convert_elasticsearch_field.register(elasticsearch_fields.Short)
def convert_field_to_int(field, registry=None):
    return Int(
        description=get_field_description(field, registry),
        required=field._required,
    )


@convert_elasticsearch_field.register(elasticsearch_fields.Boolean)
def convert_field_to_boolean(field, registry=None):
    return Boolean(
        description=get_field_description(field, registry),
        required=field._required,
    )


@convert_elasticsearch_field.register(elasticsearch_fields.Double)
@convert_elasticsearch_field.register(elasticsearch_fields.HalfFloat)
@convert_elasticsearch_field.register(elasticsearch_fields.Float)
@convert_elasticsearch_field.register(elasticsearch_fields.ScaledFloat)
def convert_field_to_float(field, registry=None):
    return Float(
        description=get_field_description(field, registry),
        required=field._required,
    )


@convert_elasticsearch_field.register(elasticsearch_fields.Date)
def convert_field_to_datetime(field, registry=None):
    return DateTime(
        description=get_field_description(field, registry),
        required=field._required,
    )


# @convert_elasticsearch_field.register(elasticsearch_fields.Nested)
# def convert_nested_field_to_list(field, registry=None):
#     base_type = convert_field_to_jsonstring(field._doc_class)
#
#     if not isinstance(base_type, (List, NonNull)):
#         base_type = type(base_type)
#     return List(
#         base_type,
#         description=get_field_description(field, registry),
#         required=field._required
#     )


# @convert_elasticsearch_field.register(InnerDoc)
# def convert_field_to_inner_doc(field, registry=None):
#     from .types import JSONString
#
#     return JSONString(
#         description=get_field_description(field, registry),
#         required=field._required,
#     )


@convert_elasticsearch_field.register(elasticsearch_fields.Object)
@convert_elasticsearch_field.register(elasticsearch_fields.Nested)
def convert_field_to_jsonstring(field, registry=None):
    from .types import JSONString

    return JSONString(
        description=get_field_description(field, registry),
        required=field._required,
    )
