Suggesters
==========
**Sample type definition:**

.. code-block:: python

    from graphene import Node
    from graphene_elastic import ElasticsearchObjectType
    from graphene_elastic.filter_backends import SuggesterFilterBackend

    class Post(ElasticsearchObjectType):

        class Meta:

            document = PostDocument
            interfaces = (Node,)
            filter_backends = [
                # ...
                SuggesterFilterBackend,  # Important
                # ...
            ]

            # ...

            # For `SuggestFilterBackend` backend
            suggester_fields = {
                'title_suggest': {
                    'field': 'title.suggest',
                    'default_suggester': SUGGESTER_COMPLETION,
                    'options': {
                        'size': 20,
                        'skip_duplicates': True,
                    },
                },
                'title_suggest_context': {
                    'field': 'title.suggest_context',
                    'suggesters': [
                        SUGGESTER_COMPLETION,
                    ],
                    'default_suggester': SUGGESTER_COMPLETION,
                    # We want to be able to filter the completion filter
                    # results on the following params: tag, state and publisher.
                    # We also want to provide the size value.
                    # See the "https://www.elastic.co/guide/en/elasticsearch/
                    # reference/6.1/suggester-context.html" for the reference.
                    'completion_options': {
                        'category_filters': {
                            'title_tag': 'tag',
                            'title_state': 'state',
                            'title_publisher': 'publisher',
                        },
                    },
                    'options': {
                        'size': 20,
                    },
                },
                'publisher_suggest': 'publisher.suggest',
                'tag_suggest': 'tags.suggest',
            }

            # ...

**Sample query:**

.. code-block:: javascript

    query {
      allPostDocuments(
            suggest:{titleSuggest:{completion:"Ar"}}
        ) {
        edges {
          node {
            titleSuggest
          }
          cursor
        }
      }
    }

**Sample response:**

.. code-block:: javascript

    {
      "data": {
        "allPostDocuments": {
          "edges": [
            {
              "node": {
                "title": "PM decide.",
                "content": "Cut dog young only. Whole natural state Republican year.\nFinancial oil current sea. Mind large similar probably lawyer since. Son control fire remember.",
                "highlight": {
                  "title": [
                    "PM <b>decide</b>."
                  ],
                  "content": [
                    "Mind large similar probably lawyer <em>since</em>."
                  ]
                }
              },
              "cursor": "YXJyYXljb25uZWN0aW9uOjA="
            },
            {
              "node": {
                "title": "Many add.",
                "content": "Read almost consumer perform water. Really protect push send body wind. Training point since involve public last let new.",
                "highlight": {
                  "content": [
                    "Training point <em>since</em> involve public last let new."
                  ]
                }
              },
              "cursor": "YXJyYXljb25uZWN0aW9uOjE="
            }
        }
      }
    }
