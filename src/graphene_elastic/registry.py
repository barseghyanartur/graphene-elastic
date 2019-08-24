__title__ = "graphene_elastic.registry"
__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2019 Artur Barseghyan"
__license__ = "GPL-2.0-only OR LGPL-2.1-or-later"
__all__ = (
    "Registry",
    "registry",
    "get_global_registry",
    "reset_global_registry",
)


class Registry(object):
    def __init__(self):
        self._registry = {}
        self._field_registry = {}

    def register(self, cls):
        from .types import ElasticsearchObjectType

        assert issubclass(
            cls, ElasticsearchObjectType
        ), 'Only ElasticsearchObjectType can be registered, ' \
           'received "{}"'.format(
            cls.__name__
        )
        assert (
            cls._meta.registry == self
        ), "Registry for a document have to match."
        self._registry[cls._meta.document] = cls

        # Rescan all fields
        for document, cls in self._registry.items():
            cls.rescan_fields()

    def get_type_for_document(self, document):
        return self._registry.get(document)

    def register_converted_field(self, field, converted):
        self._field_registry[field] = converted

    def get_converted_field(self, field):
        return self._field_registry.get(field)


registry = None


def get_global_registry():
    global registry
    if not registry:
        registry = Registry()
    return registry


def reset_global_registry():
    global registry
    registry = None
