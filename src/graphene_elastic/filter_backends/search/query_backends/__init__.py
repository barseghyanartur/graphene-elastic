"""
Search query backends.
"""

from .base import BaseSearchQueryBackend
from .match import MatchQueryBackend
from .match_phrase import MatchPhraseQueryBackend
from .match_phrase_prefix import MatchPhrasePrefixQueryBackend
# from .multi_match import MultiMatchQueryBackend
# from .nested import NestedQueryBackend
# from .simple_query_string import SimpleQueryStringQueryBackend

__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2019-2022 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = (
    'BaseSearchQueryBackend',
    'MatchQueryBackend',
    'MatchPhraseQueryBackend',
    'MatchPhrasePrefixQueryBackend',
    # 'MultiMatchQueryBackend',
    # 'NestedQueryBackend',
    # 'SimpleQueryStringQueryBackend',
)
