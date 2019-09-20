import graphene
import elasticsearch_dsl

from collections import OrderedDict
from graphene.relay import Connection, Node
from graphene.types.objecttype import ObjectType, ObjectTypeOptions
from graphene.types.utils import yank_fields_from_attrs

# from ..fields import ElasticsearchConnectionField
from ..converter import convert_elasticsearch_field
from ..registry import Registry, get_global_registry
from ..utils import (
    get_document_fields,
    is_valid_elasticsearch_document,
)

__title__ = 'graphene_elastic.types.elastic_types'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2019 Artur Barseghyan'
__license__ = 'GPL-2.0-only OR LGPL-2.1-or-later'
__all__ = (
    'construct_fields',
    'construct_self_referenced_fields',
    'ElasticsearchObjectTypeOptions',
    'ElasticsearchObjectType',
)


def construct_fields(document, registry, only_fields, exclude_fields):
    """
    Args:
        document (elasticsearch_dsl.Document):
        registry (graphene_elastic.registry.Registry):
        only_fields ([str]):
        exclude_fields ([str]):

    Returns:
        (OrderedDict, OrderedDict): converted fields and self reference fields.

    """
    _document_fields = get_document_fields(document)
    fields = OrderedDict()
    self_referenced = OrderedDict()
    for name, field in _document_fields.items():
        is_not_in_only = only_fields and name not in only_fields
        is_excluded = name in exclude_fields
        if is_not_in_only or is_excluded:
            # We skip this field if we specify only_fields and is not
            # in there. Or when we exclude this field in exclude_fields
            continue

        # TODO: Finish this once ``List`` is supported (in Elasticsearch
        # it's `multi=True`).
        if field._multi:
            if not (hasattr(field, '_doc_class') or hasattr(field, 'fields')):
                continue

            if hasattr(field, 'fields'):
                for sub_field_name, sub_field in field.fields._d_.items():

                    # Take care of list of self-reference.
                    document_type_obj = sub_field.__class__

                    if document_type_obj == document \
                            or isinstance(document_type_obj, document):
                        self_referenced[name] = field
                        continue
            else:   # if hasattr(field, '_doc_class')
                document_type_obj = field._doc_class

                if document_type_obj == document \
                        or isinstance(document_type_obj, document):
                    self_referenced[name] = field
                    continue

        converted = convert_elasticsearch_field(field, registry)
        if not converted:
            continue
        fields[name] = converted

    return fields, self_referenced


def construct_self_referenced_fields(self_referenced, registry):
    fields = OrderedDict()
    for name, field in self_referenced.items():
        converted = convert_elasticsearch_field(field, registry)
        if not converted:
            continue
        fields[name] = converted

    return fields


def construct_backend_fields(backends, connection):
    """Construct backend fields.

    :param backends:
    :param connection:
    :return:
    """
    backend_fields = OrderedDict()
    for backend_cls in backends:
        backend = backend_cls(connection)
        backend_fields.update(backend.get_backend_document_fields())

    return backend_fields


class ElasticsearchObjectTypeOptions(ObjectTypeOptions):

    document = None  # type: Document
    registry = None  # type: Registry
    connection = None  # type: Type[Connection]
    # filter_backends = []
    # filter_backend_options = {}


class ElasticsearchObjectType(ObjectType):

    @classmethod
    def __init_subclass_with_meta__(cls,
                                    document=None,
                                    registry=None,
                                    skip_registry=False,
                                    only_fields=(),
                                    exclude_fields=(),
                                    connection=None,
                                    connection_class=None,
                                    use_connection=None,
                                    connection_field_class=None,
                                    interfaces=(),
                                    _meta=None,
                                    **options):

        assert is_valid_elasticsearch_document(document), (
            'The attribute document in {}.Meta must be a valid '
            'Elasticsearch-dsl Document. Received "{}" instead.'
        ).format(cls.__name__, type(document))
        if not registry:
            registry = get_global_registry()

        assert isinstance(registry, Registry), (
            'The attribute registry in {}.Meta needs to be an instance of '
            'Registry, received "{}".'
        ).format(cls.__name__, registry)
        converted_fields, self_referenced = construct_fields(
            document, registry, only_fields, exclude_fields
        )
        document_fields = yank_fields_from_attrs(
            converted_fields,
            _as=graphene.Field
        )
        if use_connection is None and interfaces:
            use_connection = any(
                (issubclass(interface, Node) for interface in interfaces)
            )

        if use_connection and not connection:
            # We create the connection automatically
            if not connection_class:
                connection_class = Connection

            connection = connection_class.create_type(
                '{}Connection'.format(cls.__name__), node=cls)

        if connection is not None:
            assert issubclass(connection, Connection), (
                'The attribute connection in {}.Meta must be of type '
                'Connection. Received "{}" instead.'
            ).format(cls.__name__, type(connection))

        if connection_field_class is not None:
            assert issubclass(
                connection_field_class,
                graphene.ConnectionField
            ), (
                'The attribute connection_field_class in {}.Meta must be of '
                'type graphene.ConnectionField. Received "{}" instead.'
            ).format(cls.__name__, type(connection_field_class))
        else:
            from ..fields import ElasticsearchConnectionField
            connection_field_class = ElasticsearchConnectionField

        if _meta:
            assert isinstance(_meta, ElasticsearchObjectTypeOptions), (
                '_meta must be an instance of ElasticsearchObjectTypeOptions, '
                'received {}'
            ).format(_meta.__class__)
        else:
            _meta = ElasticsearchObjectTypeOptions(cls)

        backend_fields = construct_backend_fields(
            backends=options.get('filter_backends', []),
            connection=connection
        )
        document_fields.update(backend_fields)

        _meta.document = document
        _meta.registry = registry
        _meta.fields = document_fields
        _meta.filter_backends = options.get('filter_backends', [])
        _meta.filter_backend_options = dict(options)
        _meta.connection = connection
        _meta.connection_field_class = connection_field_class
        # Save them for later
        _meta.only_fields = only_fields
        _meta.exclude_fields = exclude_fields

        super(ElasticsearchObjectType, cls).__init_subclass_with_meta__(
            _meta=_meta, interfaces=interfaces, **options
        )
        if not skip_registry:
            registry.register(cls)
            # Notes: Take care list of self-reference fields.
            converted_fields = construct_self_referenced_fields(
                self_referenced,
                registry
            )
            if converted_fields:
                document_fields = yank_fields_from_attrs(
                    converted_fields,
                    _as=graphene.Field
                )
                cls._meta.fields.update(document_fields)
                registry.register(cls)

    @classmethod
    def rescan_fields(cls):
        """Attempts to rescan fields and will insert any not converted
        initially."""

        converted_fields, self_referenced = construct_fields(
            cls._meta.document, cls._meta.registry,
            cls._meta.only_fields, cls._meta.exclude_fields
        )

        document_fields = yank_fields_from_attrs(
            converted_fields,
            _as=graphene.Field
        )

        # The initial scan should take precedence
        for field in document_fields:
            if field not in cls._meta.fields:
                cls._meta.fields.update({field: document_fields[field]})
        # Self-referenced fields can't change between scans!

    @classmethod
    def is_type_of(cls, root, info):
        if isinstance(root, cls):
            return True

        if not is_valid_elasticsearch_document(type(root)):
            raise Exception((
                'Received incompatible instance "{}".'
            ).format(root))
        return isinstance(root, cls._meta.document)

    @classmethod
    def get_node(cls, info, id):
        return cls._meta.document.get(id)

    @property
    def id(self):
        return self.meta.id

    def resolve_id(self, info):
        return self.meta.id
