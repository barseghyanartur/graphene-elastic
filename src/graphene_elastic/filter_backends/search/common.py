import operator
from copy import copy, deepcopy
from collections import ChainMap

import graphene
from graphene.types.field import source_resolver
import six

from elasticsearch_dsl.query import Q
from stringcase import pascalcase as to_pascal_case

from ..base import BaseBackend
from ...constants import (
    DYNAMIC_CLASS_NAME_PREFIX,
    ALL,
    FIELD,
    VALUE,
    BOOST,
)

__title__ = "graphene_elastic.filter_backends.search.common"
__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2019-2020 Artur Barseghyan"
__license__ = "GPL-2.0-only OR LGPL-2.1-or-later"
__all__ = ("SearchFilterBackend",)


class SearchFilterBackend(BaseBackend):
    """Search filter backend."""

    prefix = "search"
    has_query_fields = True

    @property
    def search_fields(self):
        """Search filter fields."""
        search_fields = getattr(
            self.connection_field.type._meta.node._meta,
            "filter_backend_options",
            {},
        ).get("search_fields", {})
        return deepcopy(search_fields)

    @property
    def search_nested_fields(self):
        """Search nested filter fields."""
        search_nested_fields = getattr(
            self.connection_field.type._meta.node._meta,
            "filter_backend_options",
            {},
        ).get("search_nested_fields", {})
        return deepcopy(search_nested_fields)

    @property
    def search_args_mapping(self):
        return {field: field for field, value in self.search_fields.items()}

    @property
    def nested_search_args_mapping(self):
        return {
            field: field for field, value in self.search_nested_fields.items()
        }

    def field_belongs_to(self, field_name):
        """Check if given filter field belongs to the backend.

        :param field_name:
        :return:
        """
        return (
            field_name in self.search_fields
            or field_name in self.search_nested_fields
        )

    def get_backend_default_query_fields_params(self):
        """Get backend default filter params.

        :rtype: dict
        :return:
        """
        return {ALL: graphene.String()}

    def get_search_nested_fields_tree(self, start=None, value=None):
        """
        We got a prepared nested fields ,

        {
            'country': {
                'path': 'country',
                'fields': [
                    {
                        'name': {'boost': 2}
                    }
                ]
            },
            'city': {
                'path': 'country.city',
                'fields': [
                    {
                        'name': {'boost': 2}
                    }
                ]
            }
        }

        Then we should turn it to

        {
            'country': {
                'name': {},   # {} or None represents no more leaves downside.
                'city': {
                    'name': {}
                }
            }
        }


        """
        source = self.search_nested_fields
        path_field_mapping = {
            option["path"]: field for field, option in source.items()
        }
        tree = {}

        for field, option in source.items():
            if start and not option["path"].startswith(start):
                continue

            splited_path = option["path"].split(".")
            inserted = False
            node = {}
            for f in option.get("fields", []):
                if isinstance(f, dict):
                    node.update({list(f.keys())[0]: deepcopy(value)})
                elif isinstance(f, six.string_types):
                    node.update({f: deepcopy(value)})

            # Find sub path item and insert it inside this node
            for _path, _field in path_field_mapping.items():
                _splited_path = _path.split(".")
                if (
                    _path.startswith(option["path"])
                    and len(_splited_path) - len(splited_path) == 1
                    and _field in tree
                ):
                    node.update({_field: tree.pop(_field)})

            # Find item which contains this node and put this node inside it.
            for _path, _field in path_field_mapping.items():
                _splited_path = _path.split(".")
                if (
                    option["path"].startswith(_path)
                    and len(splited_path) - len(_splited_path) > 0
                ):
                    # Note: because we don't sure whether whole path was built over, we should traverse the tree
                    # and find the proper place to put this node inside it.
                    t = tree
                    for __splited in splited_path[:-1]:
                        if __splited in t:
                            t = t[__splited]

                    if t != tree:
                        t.update({field: node})
                        inserted = True
                        break

            if not inserted:  # no other node can take this node.
                tree.update({field: node})

        return tree

    def get_field_type(self, field_name, field_value, base_field_type):
        """Get field type.

        :return:

        TODO: required
        """

        nested_input_count = 0

        def get_graphene_argument_type(name, params):
            nonlocal nested_input_count
            nested_input_count += 1
            return graphene.Argument(
                type(
                    "{}{}{}{}{}".format(
                        DYNAMIC_CLASS_NAME_PREFIX,
                        to_pascal_case(self.prefix),
                        self.connection_field.type.__name__,
                        to_pascal_case(name),
                        str(nested_input_count),
                    ),
                    (graphene.InputObjectType,),
                    params,
                )
            )

        def dfs(root, root_field_type):
            ret = {}

            for name, node in root.items():
                if isinstance(node, dict):
                    params = self.get_backend_default_query_fields_params()
                    params.update(
                        dfs(node, root_field_type._meta.fields.get(name))
                    )
                    ret.update({name: get_graphene_argument_type(name, params)})
                elif not node:
                    if hasattr(root_field_type, "_meta"):
                        fields = root_field_type._meta.fields
                    else:
                        fields = root_field_type._type._of_type._meta.fields
                    print(name, fields.get(name))
                    params = {
                        VALUE: fields.get(name),
                        BOOST: graphene.Int(),
                    }
                    ret.update({name: get_graphene_argument_type(name, params)})

            return ret

        if field_name in self.search_fields:
            params = {
                VALUE: base_field_type,  # Value to search on. Required.
                BOOST: graphene.Int(),  # Boost the given field with. Optional.
            }
            return get_graphene_argument_type(field_name, params)

        elif field_name in self.search_nested_fields:
            params = self.get_backend_default_query_fields_params()
            tree = self.get_search_nested_fields_tree().get(field_name)
            params.update(dfs(tree, base_field_type))

            return get_graphene_argument_type(field_name, params)

    def prepare_search_fields(self):
        """Prepare search fields.

        Possible structures:

            search_fields = {
                'title': {'boost': 4, 'field': 'title.raw'},
                'content': {'boost': 2},
                'category': None,
                'comments': None
            }

        We shall finally have:

            search_fields = {
                'title': {
                    'field': 'title.raw',
                    'boost': 4
                },
                'content': {
                    'field': 'content',
                    'boost': 2
                },
                'category': {
                    'field': 'category'
                }
            }

        Sample query would be:

            {
              allPostDocuments(search:{query:"Another"}) {
                pageInfo {
                  startCursor
                  endCursor
                  hasNextPage
                  hasPreviousPage
                }
                edges {
                  cursor
                  node {
                    category
                    title
                    content
                    numViews
                  }
                }
              }
            }


        :return: Filtering options.
        :rtype: dict
        """
        filter_args = dict(self.args).get(self.prefix)
        if not filter_args:
            return {}

        filter_fields = {}

        # {'query': '', 'title': {'query': '', 'boost': 1}}

        for field, _ in self.search_args_mapping.items():
            filter_fields.update({field: {}})
            options = self.search_fields.get(field)
            # For constructions like 'category': 'category.raw' we shall
            # have the following:
            #
            if options is None or isinstance(options, six.string_types):
                filter_fields.update({field: {"field": options or field}})
            elif "field" not in options:
                filter_fields.update({field: options})
                filter_fields[field]["field"] = field
            else:
                filter_fields.update({field: options})

        return filter_fields

    def prepare_search_nested_fields(self):
        """Prepare search fields.

        Possible structures:

        Type1
            search_nested_fields = {
                'comments': {
                    'path'; 'comments',
                    'fields': [
                        {'author': {'boost': 4}},
                        {'tag': {'boost': 2}},
                    ]
                }
            }
        Type2
            search_nested_fields = {
                'comments: {
                    'path'; 'comments',
                    'fields': ['author', 'tag']
                }
            }

        We shall finally have:

            search_nested_fields = {
                'comments': {
                    'path': 'comments',
                    'fields': {
                        {'author': {'boost': 4}},
                        {'tag': {'boost': 2}}
                    }
                }
            }

        Sample query would be:

            {
              allPostDocuments(search:{query:"Another"}) {
                pageInfo {
                  startCursor
                  endCursor
                  hasNextPage
                  hasPreviousPage
                }
                edges {
                  cursor
                  node {
                    category
                    title
                    content
                    numViews
                  }
                }
              }
            }


        :return: Filtering options.
        :rtype: dict
        """
        filter_args = dict(self.args).get(self.prefix)
        if not filter_args:
            return {}

        filter_fields = {}
        search_nested_fields = self.search_nested_fields
        # {'query': '', 'title': {'query': '', 'boost': 1}}
        for field, _ in self.nested_search_args_mapping.items():
            filter_fields.update({field: {}})
            options = deepcopy(search_nested_fields.get(field, {}))
            if "fields" not in options:
                options["fields"] = []

            fields = []
            for _field in options["fields"]:
                if isinstance(_field, six.string_types):
                    fields.append({_field: {"field": _field}})
                elif isinstance(_field, dict):
                    fields.append(_field)
            options["fields"] = fields
            filter_fields.update({field: options})

        return filter_fields

    def get_all_query_params(self):
        filter_args = dict(self.args).get(self.prefix)
        if not filter_args:
            return {}
        return filter_args

    def construct_search(self):
        """Construct search.

        We have to deal with two types of structures:

        Type 1:

        >>> search_fields = (
        >>>     'title',
        >>>     'description',
        >>>     'summary',
        >>> )

        Type 2:

        >>> search_fields = {
        >>>     'title': {'field': 'title', 'boost': 2},
        >>>     'description': None,
        >>>     'summary': None,
        >>> }

        In GraphQL shall be:

            query {
              allPostDocuments(search:{
                    query:"Another",
                    title:{value:"Another"}
                    summary:{value:"Another"}
                }) {
                pageInfo {
                  startCursor
                  endCursor
                  hasNextPage
                  hasPreviousPage
                }
                edges {
                  cursor
                  node {
                    category
                    title
                    content
                    numViews
                  }
                }
              }
            }

        Or simply:

            query {
              allPostDocuments(search:{query:"education technology"}) {
                pageInfo {
                  startCursor
                  endCursor
                  hasNextPage
                  hasPreviousPage
                }
                edges {
                  cursor
                  node {
                    category
                    title
                    content
                    numViews
                  }
                }
              }
            }

        :return: Updated queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        all_query_params = self.get_all_query_params()
        search_fields = self.prepare_search_fields()
        _queries = []
        for search_field, value in all_query_params.items():
            if search_field == ALL:
                for (
                    field_name_param,
                    field_name,
                ) in self.search_args_mapping.items():
                    field_options = copy(search_fields[field_name])
                    field = field_options.pop("field", field_name)

                    if isinstance(value, dict):
                        # For constructions like:
                        # {'title': {'value': 'Produce', 'boost': 1}}
                        _query = value.pop(VALUE)
                        _field_options = copy(value)
                        value = _query
                        field_options.update(_field_options)
                    field_kwargs = {field: {"query": value}}
                    if field_options:
                        field_kwargs[field].update(field_options)
                    # The match query
                    _queries.append(Q("match", **field_kwargs))
            elif search_field in search_fields:
                field_options = copy(search_fields[search_field])
                field = field_options.pop("field", search_field)

                if isinstance(value, dict):
                    # For constructions like:
                    # {'title': {'value': 'Produce', 'boost': 1}}
                    _query = value.pop(VALUE)
                    _field_options = copy(value)
                    value = _query
                    field_options.update(_field_options)
                field_kwargs = {field: {"query": value}}
                if field_options:
                    field_kwargs[field].update(field_options)
                # The match query
                _queries.append(Q("match", **field_kwargs))

        return _queries

    def construct_nested_search(self):
        """Construct nested search.

        We have to deal with two types of structures:

        Type 1:

        >>> search_nested_fields = {
        >>>     'country': {
        >>>         'path': 'country',
        >>>         'fields': ['name'],
        >>>     },
        >>>     'city': {
        >>>         'path': 'country.city',
        >>>         'fields': ['name'],
        >>>     },
        >>> }

        Type 2:

        >>> search_nested_fields = {
        >>>     'country': {
        >>>         'path': 'country',
        >>>         'fields': [{'name': {'boost': 2}}]
        >>>     },
        >>>     'city': {
        >>>         'path': 'country.city',
        >>>         'fields': [{'name': {'boost': 2}}]
        >>>     },
        >>> }


        field_kwargs = {field: search_term}

        queries.append(Q("match", **field_kwargs))

        __queries.append(
            Q(
                "nested",
                path=path,
                query=six.moves.reduce(operator.or_, queries),
            )
        )

        :return: Updated queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        if (
            not hasattr(self, "search_nested_fields")
            or not self.search_nested_fields
        ):
            return []

        search_fields = self.prepare_search_nested_fields()
        all_query_params = {
            search_field: search_terms
            for search_field, search_terms in self.get_all_query_params().items()
            if search_field in search_fields
        }

        def recursive_construct_search(
            query_params, current_search=None, searched_path=None
        ):
            _queries = []
            for search_field, search_terms in query_params.items():
                if search_field in search_fields:
                    # another nested field
                    r = recursive_construct_search(
                        search_terms,
                        current_search=search_field,
                        searched_path=search_fields[search_field]["path"],
                    )
                    _queries.append(
                        Q(
                            "nested",
                            path=search_fields[search_field]["path"],
                            query=six.moves.reduce(operator.or_, r),
                        )
                    )
                elif search_field == ALL:
                    # query all fields downside
                    search_terms = self.get_search_nested_fields_tree(
                        start=searched_path, value={VALUE: search_terms}
                    )
                    r = recursive_construct_search(
                        search_terms[current_search],
                        current_search=current_search,
                        searched_path=searched_path,
                    )
                    _queries.append(
                        Q(
                            "nested",
                            path=search_fields[current_search]["path"],
                            query=six.moves.reduce(operator.or_, r),
                        )
                    )
                else:
                    # normal field in a nested field
                    path = search_fields[current_search]["path"]
                    field_option = deepcopy(
                        next(
                            field[search_field]
                            for field in search_fields[current_search]["fields"]
                            if list(field.keys())[0] == search_field
                        )
                    )
                    field = "{}.{}".format(path, field_option.pop("field"))
                    query = search_terms.pop(VALUE)
                    field_kwargs = {field: {"query": query}}
                    if field_option:
                        field_kwargs[field].update(field_option)

                    _queries.append(Q("match", **field_kwargs))
            return _queries

        queries = recursive_construct_search(all_query_params, None)
        return queries

    def filter(self, queryset):
        """Filter.

        :param queryset:
        :return:
        """
        _queries = []

        _search = self.construct_search()
        if _search:
            _queries.extend(_search)

        _nested_search = self.construct_nested_search()
        if _nested_search:
            _queries.extend(_nested_search)

        if _queries:
            queryset = queryset.query("bool", should=_queries)

        print(queryset.to_dict())
        return queryset
