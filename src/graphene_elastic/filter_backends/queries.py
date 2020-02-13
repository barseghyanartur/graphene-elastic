import graphene
from ..enums import NoValue

__title__ = "graphene_elastic.filter_backends.queries"
__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2019-2020 Artur Barseghyan"
__license__ = "GPL-2.0-only OR LGPL-2.1-or-later"
__all__ = (
    'Contains',
    'Direction',
    'EndsWith',
    'Exclude',
    'Exists',
    'GeoBoundingBox',
    'GeoDistance',
    'GeoPolygon',
    'Gt',
    'Gte',
    'In',
    'IsNull',
    'Lt',
    'Lte',
    'Point',
    'Prefix',
    'Range',
    'StartsWith',
    'Term',
    'Terms',
    'Wildcard',
)


class _ListOfTypeString(graphene.List):
    """List of type string."""

    required = True

    def __init__(self, *args, **kwargs):
        super(_ListOfTypeString, self).__init__(
            of_type=graphene.String,
            *args,
            **kwargs
        )


_number_or_date_types = (
    graphene.Decimal,
    graphene.Float,
    graphene.Int,
    graphene.Date,
    graphene.DateTime,
)


class _NumberOrDate(graphene.InputObjectType):
    """Number or Date."""

    decimal = graphene.Decimal(required=False)
    float = graphene.Float(required=False)
    int = graphene.Int(required=False)
    datetime = graphene.DateTime(required=False)
    date = graphene.Date(required=False)

# ***************************************************************
# ************************* Filtering ***************************
# ***************************************************************


class Term(graphene.String):
    """Terms.

        filter:[
            {category: {term: "Python"}]}}
        ]
    """

    required = True


class Terms(_ListOfTypeString):
    """Terms.

        filter:[
            {category: {terms: ["Python", "Django"]}}
        ]
    """


class Range(graphene.InputObjectType):
    """Range.

        filter:[
            {range: {lower: "1000", upper: "2000", boost: "2.0"}]}}
        ]
    """
    lower = graphene.Field(_NumberOrDate, required=True)
    upper = graphene.Field(_NumberOrDate)
    boost = graphene.Decimal()


class Exists(graphene.Boolean):
    """Exists.

        filter:[
            {category: {exist: true}]}}
        ]
    """

    required = True


class Prefix(graphene.String):
    """Prefix.

        filter:[
            {category: {prefix: "bio"}]}}
        ]
    """

    required = True


class StartsWith(Prefix):
    """Starts with (alias of prefix)."""


class Wildcard(graphene.String):
    """Wildcard.

        filter:[
            {category: {wildcard: "*bio*"}]}}
        ]
    """

    required = True


class GeoDistance(graphene.InputObjectType):
    """Geo distance.

        filter:[
            {place: {geoDistance: {distance: "9km", lat: "40.0", lon="70.0"}}}
        ]
    """

    distance = graphene.String(required=True)
    lat = graphene.Decimal(required=True)
    lon = graphene.Decimal(required=True)


class Point(graphene.InputObjectType):
    """Point. Helper for many geo lookups."""

    lat = graphene.Decimal(required=True)
    lon = graphene.Decimal(required=True)


class GeoPolygon(graphene.InputObjectType):
    """Geo polygon.

        filter:[
            {place: {geoPolygon: {points: [{lat: "40.0", lon="70.0"}]}}}
        ]
    """

    points = graphene.List(Point, required=True)


class GeoBoundingBox(graphene.InputObjectType):
    """Geo polygon.

        filter:[
            {place: {geoBoundingBox: {
                topLeft: {lat: "40.0", lon="70.0"},
                bottomRight: {lat: "80.0", lon: "90.0"}
            }}}
        ]
    """

    top_left = graphene.Field(Point, required=True)
    bottom_right = graphene.Field(Point, required=True)


class Contains(graphene.String):
    """Wildcard.

        filter:[
            {category: {contains: "lish"}]}}
        ]
    """

    required = True


class In(_ListOfTypeString):
    """In.

        filter:[
            {category: {in: ["Python", "Django"]}}
        ]
    """


class Gt(_NumberOrDate):
    """Gt.

        filter:[
            {category: {gt: "1"}]}}
        ]
    """

    class Meta:
        types = list(_number_or_date_types)

    required = True


class Gte(_NumberOrDate):
    """Gte.

        filter:[
            {category: {gte: "1"}]}}
        ]
    """

    class Meta:
        types = list(_number_or_date_types)

    required = True


class Lt(_NumberOrDate):
    """Lt.

        filter:[
            {category: {lt: "1"}]}}
        ]
    """

    class Meta:
        types = list(_number_or_date_types)

    required = True


class Lte(_NumberOrDate):
    """Lte.

        filter:[
            {category: {lte: "1"}]}}
        ]
    """

    class Meta:
        types = list(_number_or_date_types)

    required = True


class EndsWith(graphene.String):
    """Ends with.

        filter:[
            {category: {endsWith: "dren"}]}}
        ]
    """

    required = True


class IsNull(graphene.Boolean):
    """Is null.

        filter:[
            {category: {isNull: true}]}}
        ]
    """

    required = True


class Exclude(_ListOfTypeString):
    """Exclude.

        filter:[
            {category: {exclude: ["Python", "Django"]}}
        ]
    """

# ***************************************************************
# ************************** Ordering ***************************
# ***************************************************************


@graphene.Enum.from_enum
class Direction(NoValue):
    """Ordering direction."""

    ASC = 'asc'
    DESC = 'desc'
