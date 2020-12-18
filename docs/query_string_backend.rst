Query string backend
====================

**Sample query**

.. code-block:: graphql

    query PostsQuery {
      allPostDocuments(
        queryString:"(White Rabbit) AND Alice"
      ) {
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
