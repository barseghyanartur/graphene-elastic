Example project
===============

Sample document definition
--------------------------
*search_index/documents/post.py*

See `examples/search_index/documents/post.py
<https://github.com/barseghyanartur/graphene-elastic/blob/master/examples/search_index/documents/post.py>`_
for full example.

.. code-block:: python

    import datetime
    from elasticsearch_dsl import (
        Boolean,
        Date,
        Document,
        InnerDoc,
        Keyword,
        Nested,
        Text,
        Integer,
    )

    class Comment(InnerDoc):

        author = Text(fields={'raw': Keyword()})
        content = Text(analyzer='snowball')
        created_at = Date()

        def age(self):
            return datetime.datetime.now() - self.created_at


    class Post(Document):

        title = Text(
            fields={'raw': Keyword()}
        )
        content = Text()
        created_at = Date()
        published = Boolean()
        category = Text(
            fields={'raw': Keyword()}
        )
        comments = Nested(Comment)
        tags = Text(
            analyzer=html_strip,
            fields={'raw': Keyword(multi=True)},
            multi=True
        )
        num_views = Integer()

        class Index:
            name = 'blog_post'
            settings = {
                'number_of_shards': 1,
                'number_of_replicas': 1,
                'blocks': {'read_only_allow_delete': None},
            }

Sample schema definition
------------------------
ConnectionField is the most flexible and feature rich solution you have. It
uses filter backends which you can tie to your needs the way you want in a
declarative manner.

**schema.py**

.. code-block:: python

    import graphene
    from graphene_elastic import (
        ElasticsearchObjectType,
        ElasticsearchConnectionField,
    )
    from graphene_elastic.filter_backends import (
        FilteringFilterBackend,
        SearchFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
    )
    from graphene_elastic.constants import (
        LOOKUP_FILTER_PREFIX,
        LOOKUP_FILTER_TERM,
        LOOKUP_FILTER_TERMS,
        LOOKUP_FILTER_WILDCARD,
        LOOKUP_QUERY_EXCLUDE,
        LOOKUP_QUERY_IN,
    )

    # Object type definition
    class Post(ElasticsearchObjectType):

        class Meta(object):
            document = PostDocument
            interfaces = (Node,)
            filter_backends = [
                FilteringFilterBackend,
                SearchFilterBackend,
                OrderingFilterBackend,
                DefaultOrderingFilterBackend,
            ]

            # For `FilteringFilterBackend` backend
            filter_fields = {
                'title': {
                    'field': 'title.raw',
                    'lookups': [
                        LOOKUP_FILTER_TERM,
                        LOOKUP_FILTER_TERMS,
                        LOOKUP_FILTER_PREFIX,
                        LOOKUP_FILTER_WILDCARD,
                        LOOKUP_QUERY_IN,
                        LOOKUP_QUERY_EXCLUDE,
                    ],
                    'default_lookup': LOOKUP_FILTER_TERM,
                },
                'category': 'category.raw',
                'tags': 'tags.raw',
                'num_views': 'num_views',
            }

            # For `SearchFilterBackend` backend
            search_fields = {
                'title': {'boost': 4},
                'content': {'boost': 2},
                'category': None,
            }

            # For `OrderingFilterBackend` backend
            ordering_fields = {
                'title': 'title.raw',
                'created_at': 'created_at',
                'num_views': 'num_views',
            }

            # For `DefaultOrderingFilterBackend` backend
            ordering_defaults = (
                '-num_views',
                'title.raw',
            )

    # Query definition
    class Query(graphene.ObjectType):
        all_post_documents = ElasticsearchConnectionField(Post)

    # Schema definition
    schema = graphene.Schema(query=Query)

filter_backends
~~~~~~~~~~~~~~~
The list of filter backends you want to enable on your schema.

The following filter backends are available at the moment:

- FilteringFilterBackend,
- SearchFilterBackend
- OrderingFilterBackend
- DefaultOrderingFilterBackend

``graphene-elastic`` would dynamically transform your definitions into
fields and arguments to use for searching, filtering, ordering, etc.

filter_fields
~~~~~~~~~~~~~
Used by ``FilteringFilterBackend`` backend.

It's ``dict`` with keys representing names of the arguments that would
become available to the GraphQL as input for querying. The values of the
``dict`` would be responsible for precise configuration of the queries.

Let's review the following example:

.. code-block:: python

    'title': {
        'field': 'title.raw',
        'lookups': [
            LOOKUP_FILTER_TERM,
            LOOKUP_FILTER_TERMS,
            LOOKUP_FILTER_PREFIX,
            LOOKUP_FILTER_WILDCARD,
            LOOKUP_QUERY_IN,
            LOOKUP_QUERY_EXCLUDE,
        ],
        'default_lookup': LOOKUP_FILTER_TERM,
    }

**field**

The ``field`` is the corresponding field of the Elasticsearch Document. In the
example below it's ``title.raw``.

.. code-block:: python

    class Post(Document):

        title = Text(
            fields={'raw': Keyword()}
        )

**lookups**

In the given example, the available lookups for the ``title.raw`` would be
limited to ``term``, ``terms``, ``prefix``, ``wildcard``, ``in`` and
``exclude``. The latter two are functional queries, as you often see such
lookups in ORMs (such as Django) while the others are ``Elasticsearch`` native
lookups.

In our query we would then explicitly specify the lookup name (``term`` in the
example below):

.. code-block:: javascript

    query PostsQuery {
      allPostDocuments(filter:{title:{term:"Elasticsearch 7.1 released!"}}) {
        edges {
          node {
            id
            title
            category
            content
            createdAt
            comments
          }
        }
      }
    }

**default_lookup**

But we could also fallback to the ``default_lookup`` (``term`` in the example
below).

Sample query using ``default_lookup``:

.. code-block:: javascript

    query PostsQuery {
      allPostDocuments(filter:{title:{value:"Elasticsearch 7.1 released!"}}) {
        edges {
          node {
            id
            title
            category
            content
            createdAt
            comments
          }
        }
      }
    }

In the block ``{title:{value:"Elasticsearch 7.1 released!"}`` the ``value``
would stand for the ``default_lookup`` value.

search_fields
~~~~~~~~~~~~~
Used by ``SearchFilterBackend`` backend.

ordering_fields
~~~~~~~~~~~~~~~
Used by ``OrderingFilterBackend`` backend.

Similarly to `filter_fields`_, keys of the ``dict`` represent argument names
that would become available to the GraphQL for queries. The value would
be the field name of the corresponding Elasticsearch document.

ordering_defaults
~~~~~~~~~~~~~~~~~
Used by ``DefaultOrderingFilterBackend``.

If no explicit ordering is given (in the GraphQL query), this would
be the fallback - the default ordering. It's expected to be a list or a tuple
with field names to be used as default ordering. For descending ordering, add
``-`` (minus sign) as prefix to the field name.
