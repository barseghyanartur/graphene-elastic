"""
Transitional compatibility module. Contains various field wrappers and
helpers for painless (testing of) Elastic 6.x to Elastic 7.x transition. This
module is not supposed to solve all transition issues for you. Better move to
Elastic 7.x as soon as possible.
"""

__title__ = 'graphene_elastic.compat'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2019 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = (
    'get_elasticsearch_version',
    'nested_sort_entry',
)


def get_elasticsearch_version(default=(2, 0, 0)):
    """Get Elasticsearch version.

    :param default: Default value. Mainly added for building the docs
        when Elasticsearch is not running.
    :type default: tuple
    :return:
    :rtype: list
    """
    try:
        from elasticsearch_dsl import __version__
        return __version__
    except ImportError:
        return default


def nested_sort_entry(path):
    """String field.
        :param path: Full path to nested container, separated by period
        :type: str
        :return: Dictionary of full nested path
        :rtype: dict
        """
    version = get_elasticsearch_version()
    if version[0] < 6 or (version[0] == 6 and version[1] < 1):
        return {'nested_path': path}
    nested_path = {}
    path_list = path.split('.')
    for _ in reversed(path_list):
        if nested_path:
            nested_path = {'path': '.'.join(path_list), 'nested': nested_path}
        else:
            nested_path = {'path': '.'.join(path_list)}
        path_list.pop()
    return {'nested': nested_path}
