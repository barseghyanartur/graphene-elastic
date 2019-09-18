from enum import Enum
import graphene

__title__ = "graphene_elastic.enums"
__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2019 Artur Barseghyan"
__license__ = "GPL-2.0-only OR LGPL-2.1-or-later"
__all__ = ("NoValue", "convert_list_to_enum")


class NoValue(Enum):
    """String values in enum.

    Example:

    >>> class Color(NoValue):
    >>>     RED = 'stop'
    >>>     GREEN = 'go'
    >>>     BLUE = 'too fast!'

    Graphene example:

    >>> @graphene.Enum.from_enum
    >>> class ColorOptions(NoValue):
    >>>
    >>>     RED = 'stop'
    >>>     GREEN = 'go'
    >>>     BLUE = 'too fast!'
    """

    def __repr__(self):
        return "<%s.%s>" % (self.__class__.__name__, self.name)


def convert_list_to_enum(values, enum_name="DynamicEnum", upper=True):
    """Prepare list values for creating an Enum.

    Example:

    >>> values = ['red', 'green', 'blue']
    >>> print(prepare_list_for_enum(values))
    {'RED': 'red', 'GREEN': 'green', 'BLUE': 'blue'}
    """
    if upper:
        _d = {el.upper(): el for el in values}
    else:
        _d = {el: el for el in values}
    return NoValue(enum_name, _d)
