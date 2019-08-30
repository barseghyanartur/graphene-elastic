Filter lookups
==============

The following lookups are available:

- ``contains``
- ``ends_with`` (or ``endsWith`` for camelCase)
- ``exclude``
- ``exists``
- ``geo_bounding_box`` (or ``geoBoundingBox`` for camelCase)
- ``geo_distance`` (or ``geoDistance`` for camelCase)
- ``geo_polygon`` (or ``geoPolygon`` for camelCase)
- ``gt``
- ``gte``
- ``in``
- ``is_null`` (or ``isNull`` for camelCase)
- ``lt``
- ``lte``
- ``prefix``
- ``range``
- ``starts_with`` (or ``startsWith`` for camelCase)
- ``term``
- ``terms``
- ``wildcard``

Filter lookup contains
----------------------
.. code-block:: javascript

    {
      allPostDocuments(filter:{category:{contains:"tho"}}) {
        edges {
          node {
            category
            title
            content
            numViews
          }
        }
      }
    }

Filter lookup ends_with
-----------------------
.. code-block:: javascript

    {
      allPostDocuments(filter:{category:{endsWith:"thon"}}) {
        edges {
          node {
            category
            title
            content
            numViews
          }
        }
      }
    }

Filter lookup exclude
---------------------
.. code-block:: javascript

For single term:

    {
      allPostDocuments(filter:{category:{exclude:"Python"}}) {
        edges {
          node {
            category
            title
            content
            numViews
          }
        }
      }
    }

Or multiple terms:

.. code-block:: javascript

    {
      allPostDocuments(filter:{category:{exclude:["Python", "Django"]}}) {
        edges {
          node {
            category
            title
            content
            numViews
          }
        }
      }
    }


Filter lookup exists
--------------------
.. code-block:: javascript

    {
      allPostDocuments(filter:{category:{exists:true}}) {
        edges {
          node {
            category
            title
            content
            numViews
          }
        }
      }
    }
