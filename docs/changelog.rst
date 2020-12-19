Release history and notes
=========================
`Sequence based identifiers
<http://en.wikipedia.org/wiki/Software_versioning#Sequence-based_identifiers>`_
are used for versioning (schema follows below):

.. code-block:: text

    major.minor[.revision]

- It's always safe to upgrade within the same minor version (for example, from
  0.3 to 0.3.4).
- Minor version changes might be backwards incompatible. Read the
  release notes carefully before upgrading (for example, when upgrading from
  0.3.4 to 0.4).
- All backwards incompatible changes are mentioned in this document.

0.6.5
-----
2020-12-19

.. note::

    Release dedicated to defenders of Armenia and Artsakh (Nagorno Karabakh)
    and all the victims of Turkish and Azerbaijani aggression.

- Added `QueryStringBackend`.

0.6.4
-----
2020-12-12

.. note::

    Release dedicated to defenders of Armenia and Artsakh (Nagorno Karabakh)
    and all the victims of Turkish and Azerbaijani aggression.

- Added `SimpleQueryStringBackend`.

0.6.3
-----
2020-07-19

.. note::

    Release dedicated to defenders of Armenia and Artsakh (Nagorno Karabakh)
    and all the victims of Turkish and Azerbaijani aggression.

- Added `ScoreFilterBackend` and ordering by score.

0.6.2
-----
2020-07-07

- Renamed JSONString to ElasticJSONString and changed references in related 
  files. The reason for this change is to support `grapehene_federation` 
  `build_schema` which eventually helps build federated schemas

0.6.1
-----
2020-02-13

- Tested against Python 3.8.
- Tested against Elasticsearch 6.x and 7.x on Travis.
- Replace some custom code parts (casing related) with `stringcase` package
  functionality.

0.6
---
2019-10-11

.. note::

    Release dedicated to John Lennon. Happy birthday, dear John!

.. note::

    This release introduces minor backwards incompatibility for ``range``,
    ``gt``, ``gte``, ``lt`` and ``lte`` filters. You should update your code.

- The ``range``, ``gt``, ``gte``, ``lt`` and ``lte`` filters are now complex
  input types. This makes it possible to use the following types in comparison:
  ``decimal.Decimal``, ``float``, ``int``, ``datetime.datetime`` and
  ``datetime.date``.

Sample new GraphQL query:

.. code-block:: javascript

    query {
      allPostDocuments(postFilter:{numViews:{gt:{decimal:"100.00"}}}) {
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

Sample old GraphQL query:

.. code-block:: javascript

    query {
      allPostDocuments(postFilter:{numViews:{gt:"100.00"}}) {
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

0.5
---
2019-09-29

- PostFilter backend.
- Documentation improvements.

0.4
---
2019-09-23

- Added faceted search backend (with global aggregations support).
- Some refactoring which makes possible for the backends to alter the
  connection. A lot of minor changes. If you have written custom filter
  backend, you most likely need to modify some parts.

0.3
---
2019-09-20

- Minor refactoring allowing third-party independent backends do a lot more
  without touching the core.
- Source filter backend.
- More tests.

0.2
---
2019-09-18

- Highlight filter backend.

0.1
---
2019-09-08

- Documentation fixes.
- Speed up tests.
- Clean up requirements.

0.0.13
------
2019-09-07

- Documentation improvements and fixes.
- Clean up.

0.0.12
------
2019-09-06

.. note::

    In memory of Erik Slim. RIP.

- More tests.

0.0.11
------
2019-09-05

- Fixes in search backend.

0.0.10
------
2019-09-04

- Fixes.
- Clean up.

0.0.9
-----
2019-09-03

- Added pagination.
- Documentation improvements.

0.0.8
-----
2019-09-02

- Tested default ordering backend.
- Documentation improvements.

0.0.7
-----
2019-09-01

- Ordering backend.
- Added more filter lookups.
- Minor fixes in existing filter lookups.
- Improved test coverage for the filtering backend.
- Documentation improvements.

0.0.6
-----
2019-08-30

- Added more filter lookups.
- Fixes in filtering backend.
- Improved test coverage for the filtering backend.
- Documentation improvements.

0.0.5
-----
2019-08-30

- Implemented custom lookups in favour of a single ``lookup`` attribute.
- Updated tests.

0.0.4
-----
2019-08-28

- Fixed travis config (moved to elasticsearch 6.x on travis, since 7.x was
  causing problems).
- Fixes in setup.py.

0.0.3
-----
2019-08-26

- Documentation fixes.
- Add test suite and initial tests for filter backend and search backend.

0.0.2
-----
2019-08-25

- Added dynamic lookup generation for the filter backend.
- Working lookup param argument handling on the schema (filter backend).

0.0.1
-----
2019-08-24

- Initial alpha release.
