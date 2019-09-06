from __future__ import unicode_literals

import inspect
from collections import OrderedDict

import elasticsearch_dsl
from elasticsearch_dsl import field as elasticsearch_fields

from graphene import Node
# from graphene.utils.trim_docstring import trim_docstring

__title__ = "graphene_elastic.converter"
__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2019 Artur Barseghyan"
__license__ = "GPL-2.0-only OR LGPL-2.1-or-later"
__all__ = (
    "get_document_fields",
    "get_field_description",
    "get_node_from_global_id",
    "get_type_for_document",
    "import_single_dispatch",
    "is_valid_elasticsearch_document",
)


def get_document_fields(document, excluding=None):
    excluding = excluding or []
    attributes = {"_id": elasticsearch_fields.Keyword()}
    for (
        attr_name,
        attr,
    ) in document._doc_type.mapping.properties.properties._d_.items():
        if attr_name in excluding:
            continue
        attributes[attr_name] = attr
    return OrderedDict(sorted(attributes.items()))


def is_valid_elasticsearch_document(document):
    return inspect.isclass(document) and (
        issubclass(document, elasticsearch_dsl.Document)
        or issubclass(document, elasticsearch_dsl.InnerDoc)
    )


def import_single_dispatch():
    try:
        from functools import singledispatch
    except ImportError:
        singledispatch = None

    if not singledispatch:
        try:
            from singledispatch import singledispatch
        except ImportError:
            pass

    if not singledispatch:
        raise Exception(
            "It seems your python version does not include "
            "functools.singledispatch. Please install the 'singledispatch' "
            "package. More information here: "
            "https://pypi.python.org/pypi/singledispatch"
        )

    return singledispatch


# noqa
def get_type_for_document(schema, document):
    types = schema.types.values()
    for _type in types:
        type_document = hasattr(_type, "_meta") and getattr(
            _type._meta, "document", None
        )
        if document == type_document:
            return _type


def get_field_description(field, registry=None):
    """
    Common metadata includes verbose_name and help_text.

    http://docs.mongoengine.org/apireference.html#fields
    """
    parts = []
    # if hasattr(field, 'document_type'):
    #     doc = trim_docstring(field.document_type.__doc__)
    #     if doc:
    #         parts.append(doc)
    # if hasattr(field, 'verbose_name'):
    #     parts.append(field.verbose_name.title())
    # if hasattr(field, 'help_text'):
    #     parts.append(field.help_text)

    # Adding string repr for doc-type. Name would stand for
    if hasattr(field, "name"):
        parts.append(field.name)

    # if field.db_field != field.name:
    #     name_format = "(%s)" if parts else "%s"
    #     parts.append(name_format % field.db_field)

    return "\n".join(parts)


def get_node_from_global_id(node, info, global_id):
    try:
        for interface in node._meta.interfaces:
            if issubclass(interface, Node):
                return interface.get_node_from_global_id(info, global_id)
    except AttributeError:
        return Node.get_node_from_global_id(info, global_id)
