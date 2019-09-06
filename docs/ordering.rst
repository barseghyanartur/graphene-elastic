Ordering
========
Possible choices are ``ASC`` and ``DESC``.

.. code-block:: javascript

    query {
      allPostDocuments(
            filter:{category:{term:"Photography"}},
            ordering:{title:ASC}
        ) {
        edges {
          node {
            category
            title
            content
            numViews
            tags
          }
        }
      }
    }

Multiple values are allowed:

.. code-block:: javascript

    query {
      allPostDocuments(
            filter:{category:{term:"Photography"}},
            ordering:{numViews:DESC, createdAt:ASC}
        ) {
        edges {
          node {
            category
            title
            content
            numViews
            tags
          }
        }
      }
    }
