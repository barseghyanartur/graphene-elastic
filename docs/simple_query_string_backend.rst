Simple query string backend
===========================

**Sample query**

.. code-block:: graphql

    query PostsQuery {
      allPostDocuments(
        simpleQueryString:"'White Rabbit' +Alice"
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
