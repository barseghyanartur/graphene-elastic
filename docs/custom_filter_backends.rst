Custom filter backends
======================
Filter backends can:

- Add new ``graphene`` input types to the (query) schema.
- Allow you to request additional information by adding new ``graphene``
  fields to the schema.
- Alter current queryset.
- Alter slice, add additional information next to ``pageInfo`` and ``edges``,
  such as ``facets``, for example.

Let's learn by example on the ``SourceFilterBackend`` which allows us
to apply ``source`` query to the current search queryset.

.. code-block:: python

    import enum
    import graphene

    from graphen_elastic.filter_backends.base import BaseBackend
    from graphen_elastic.constants import DYNAMIC_CLASS_NAME_PREFIX

    class SourceFilterBackend(BaseBackend):
        """Source filter backend."""

        prefix = 'source'  # Name of the GraphQL query filter
        has_query_fields = True  # Indicates whether backend has own filtering fields

        # The ``source_fields`` is the config options that we set on the
        # ``Post`` object type. In this case - absolutely optional.
        @property
        def source_fields(self):
            """Source filter fields."""
            return getattr(
                self.connection_field.type._meta.node._meta,
                'filter_backend_options',
                {}
            ).get('source_fields', {})

        # This is where we dynamically create GraphQL filter fields for this
        # backend.
        def get_backend_filtering_fields(self, items, is_filterable_func, get_type_func):
            """Construct backend fields.

            :param items:
            :param is_filterable_func:
            :param get_type_func:
            :return:
            """
            _keys = list(
                self.connection_field.type._meta.node._meta.fields.keys()
            )
            _keys.remove('_id')
            params = zip(_keys, _keys)
            return {
                self.prefix: graphene.Argument(
                    graphene.List(
                        graphene.Enum.from_enum(
                            enum.Enum(
                                "{}{}{}BackendEnum".format(
                                    DYNAMIC_CLASS_NAME_PREFIX,
                                    self.prefix.title(),
                                    self.connection_field.type.__name__
                                ),
                                params
                            )
                        )
                    )
                )
            }

        # Some data normalisation.
        def prepare_source_fields(self):
            """Prepare source fields.

            Possible structures:

                source_fields = ["title"]

            Or:

                search_fields = ["title", "author.*"]

            Or:

                source = {
                    "includes": ["title", "author.*"],
                    "excludes": [ "*.description" ]
                }

            :return: Filtering options.
            :rtype: dict
            """
            source_args = dict(self.args).get(self.prefix, [])

            source_fields = dict(self.source_fields)

            if source_args:
                return source_args
            return source_fields

        # This is where the queryset is being altered.
        def filter(self, queryset):
            """Filter.

            :param queryset:
            :return:
            """
            source_fields = self.prepare_source_fields()

            if source_fields:
                queryset = queryset.source(source_fields)

            return queryset
