from ... import constants
from ..queries import (
    SuggesterCompletion,
    SuggesterTerm,
    SuggesterPhrase,
)


__title__ = "graphene_elastic.filter_backends.suggest.queries"
__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2019-2020 Artur Barseghyan"
__license__ = "GPL-2.0-only OR LGPL-2.1-or-later"
__all__ = (
    'SUGGESTER_MAPPING',
)


SUGGESTER_MAPPING = {
    constants.SUGGESTER_TERM: SuggesterTerm,
    constants.SUGGESTER_PHRASE: SuggesterPhrase,
    constants.SUGGESTER_COMPLETION: SuggesterCompletion,
}
