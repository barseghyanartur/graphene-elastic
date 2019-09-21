Faceted search
==============
In order to have faceted search, you should use ``FacetedSearchFilterBackend``.

.. code-block:: python

    from elasticsearch_dsl import DateHistogramFacet, RangeFacet
    from graphene import Node
    from graphene_elastic import ElasticsearchObjectType
    from graphene_elastic.filter_backends import (
        FacetedSearchFilterBackend,
        # ...
    )

    from search_index.documents import Post as PostDocument

    class Post(ElasticsearchObjectType):

        class Meta:

            document = PostDocument
            interfaces = (Node,)
            filter_backends = [
                # ...
                FacetedSearchFilterBackend,
                # ...
            ]

            # For `FacetedSearchFilterBackend` backend
            faceted_search_fields = {
                'category': 'category.raw',
                'category_global': {
                    'field': 'category.raw',
                    'global': True,
                },
                'tags': {
                    'field': 'tags.raw',
                    'enabled': True,  # Will appear in the list by default
                    'global': True,
                },
                'created_at': {
                    'field': 'created_at',
                    'facet': DateHistogramFacet,
                    'options': {
                        'interval': 'year',
                    }
                },
                'num_views_count': {
                    'field': 'num_views',
                    'facet': RangeFacet,
                    'options': {
                        'ranges': [
                            ("<10", (None, 10)),
                            ("11-20", (11, 20)),
                            ("20-50", (20, 50)),
                            (">50", (50, None)),
                        ]
                    }
                },
            }

Sample GraphQL query:

.. code-block:: javascript

    query {
      allPostDocuments(
            search:{title:{value:"alice"}}
            facets:[category]
      ) {
        facets
        edges {
          node {
            id
            title
            highlight
          }
        }

      }
    }

Sample response:

.. code-block:: javascript

    {
      "data": {
        "allPostDocuments": {
          "facets": {
            "_filter_tags": {
              "doc_count": 9,
              "tags": {
                "doc_count_error_upper_bound": 0,
                "sum_other_doc_count": 0,
                "buckets": [
                  {
                    "key": "photography",
                    "doc_count": 7
                  },
                  {
                    "key": "art",
                    "doc_count": 6
                  },
                  {
                    "key": "article",
                    "doc_count": 5
                  },
                  {
                    "key": "black and white",
                    "doc_count": 5
                  },
                  {
                    "key": "package",
                    "doc_count": 5
                  },
                  {
                    "key": "models",
                    "doc_count": 4
                  },
                  {
                    "key": "programming",
                    "doc_count": 4
                  }
                ]
              }
            },
            "_filter_category": {
              "doc_count": 9,
              "category": {
                "doc_count_error_upper_bound": 0,
                "sum_other_doc_count": 0,
                "buckets": [
                  {
                    "key": "Python",
                    "doc_count": 3
                  },
                  {
                    "key": "Model Photography",
                    "doc_count": 2
                  },
                  {
                    "key": "Django",
                    "doc_count": 1
                  },
                  {
                    "key": "Elastic",
                    "doc_count": 1
                  },
                  {
                    "key": "Machine Learning",
                    "doc_count": 1
                  },
                  {
                    "key": "MongoDB",
                    "doc_count": 1
                  }
                ]
              }
            }
          },
          "edges": [
            {
              "node": {
                "id": "UG9zdDpBVWNwVm0wQklwZ2dXbVlJTndOVA==",
                "title": "better Alice must",
                "highlight": {
                  "title": [
                    "better <b>Alice</b> must"
                  ]
                }
              }
            },
            ...
          ]
        }
      }
    }

Note, that ``category`` appeared in the result because we explicitly requested
so and the ``tags`` are there because they have been enabled by default.
