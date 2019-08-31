from ... import constants
from ..queries import (
    Term,
    Terms,
    Range,
    Exists,
    Prefix,
    Wildcard,
    GeoDistance,
    GeoPolygon,
    GeoBoundingBox,
    Contains,
    In,
    Gt,
    Gte,
    Lt,
    Lte,
    StartsWith,
    EndsWith,
    IsNull,
    Exclude,
)

__title__ = "graphene_elastic.filter_backends.filtering.queries"
__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2019 Artur Barseghyan"
__license__ = "GPL-2.0-only OR LGPL-2.1-or-later"
__all__ = (
    'LOOKUP_FILTER_MAPPING',
)

LOOKUP_FILTER_MAPPING = {
    constants.LOOKUP_FILTER_TERM: Term,
    constants.LOOKUP_FILTER_TERMS: Terms,
    constants.LOOKUP_FILTER_RANGE: Range,
    constants.LOOKUP_FILTER_EXISTS: Exists,
    constants.LOOKUP_FILTER_PREFIX: Prefix,
    constants.LOOKUP_FILTER_WILDCARD: Wildcard,
    # constants.LOOKUP_FILTER_REGEXP: Regexp,
    # constants.LOOKUP_FILTER_FUZZY: Fuzzy,
    # constants.LOOKUP_FILTER_TYPE: Type,
    constants.LOOKUP_FILTER_GEO_DISTANCE: GeoDistance,
    constants.LOOKUP_FILTER_GEO_POLYGON: GeoPolygon,
    constants.LOOKUP_FILTER_GEO_BOUNDING_BOX: GeoBoundingBox,
    constants.LOOKUP_QUERY_CONTAINS: Contains,
    constants.LOOKUP_QUERY_IN: In,
    constants.LOOKUP_QUERY_GT: Gt,
    constants.LOOKUP_QUERY_GTE: Gte,
    constants.LOOKUP_QUERY_LT: Lt,
    constants.LOOKUP_QUERY_LTE: Lte,
    constants.LOOKUP_QUERY_STARTSWITH: StartsWith,
    constants.LOOKUP_QUERY_ENDSWITH: EndsWith,
    constants.LOOKUP_QUERY_ISNULL: IsNull,
    constants.LOOKUP_QUERY_EXCLUDE: Exclude,
}
