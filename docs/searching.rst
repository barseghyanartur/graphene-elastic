Search
======
Search in all fields:

.. code-block:: javascript

    query {
      allPostDocuments(
        search:{query:"Release Box"}
      ) {
        edges {
          node {
            category
            title
            content
          }
        }
      }
    }

Search in specific fields:

.. code-block:: javascript

    query {
      allPostDocuments(
        search:{
            title:{value:"Release", boost:2},
            content:{value:"Box"}
        }
      ) {
        edges {
          node {
            category
            title
            content
          }
        }
      }
    }
