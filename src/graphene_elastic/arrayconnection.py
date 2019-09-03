from graphql_relay.connection.arrayconnection import (
    get_offset_with_default,
    offset_to_cursor,
)
from graphql_relay.connection.connectiontypes import (
    Connection,
    PageInfo,
    Edge,
)

from .logging import logger

__title__ = 'graphene_elastic.arrayconnection'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2019 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = (
    'connection_from_list_slice',
)


def connection_from_list_slice(
        list_slice,
        args=None,
        connection_type=None,
        edge_type=None,
        pageinfo_type=None,
        slice_start=0,
        list_length=0,
        list_slice_length=None):
    """
    Given a slice (subset) of an array, returns a connection object for use in
    GraphQL.
    This function is similar to `connectionFromArray`, but is intended for use
    cases where you know the cardinality of the connection, consider it too
    large to materialize the entire array, and instead wish pass in a slice of
    the total result large enough to cover the range specified in `args`.
    """
    connection_type = connection_type or Connection
    edge_type = edge_type or Edge
    pageinfo_type = pageinfo_type or PageInfo

    args = args or {}

    before = args.get('before')
    after = args.get('after')
    first = args.get('first')
    last = args.get('last')

    enforce_first_or_last = args.get("enforce_first_or_last")
    max_limit = args.get("max_limit")

    if enforce_first_or_last:
        assert first or last, (
            "You must provide a `first` or `last` value to properly "
            "paginate the `{}` connection."
        ).format(connection_type)

    if max_limit:
        if first or last:
            if first:
                assert first <= max_limit, (
                    "Requesting {} records on the `{}` connection exceeds "
                    "the `first` limit of {} records."
                ).format(first, connection_type, max_limit)
                first = args["first"] = min(first, max_limit)

            if last:
                assert last <= max_limit, (
                    "Requesting {} records on the `{}` connection exceeds "
                    "the `last` limit of {} records."
                ).format(last, connection_type, max_limit)
                last = args["last"] = min(last, max_limit)
        else:
            first = max_limit

    if list_slice_length is None:
        list_slice_length = len(list_slice)
    slice_end = slice_start + list_slice_length
    before_offset = get_offset_with_default(before, list_length)
    after_offset = get_offset_with_default(after, -1)

    start_offset = max(
        slice_start - 1,
        after_offset,
        -1
    ) + 1
    end_offset = min(
        slice_end,
        before_offset,
        list_length
    )
    if isinstance(first, int):
        end_offset = min(
            end_offset,
            start_offset + first
        )
    if isinstance(last, int):
        start_offset = max(
            start_offset,
            end_offset - last
        )

    # If supplied slice is too large, trim it down before mapping over it.
    _slice_qs = list_slice[
        max(start_offset - slice_start, 0):
        list_slice_length - (slice_end - end_offset)
    ]
    logger.debug(_slice_qs.to_dict())

    _slice = _slice_qs.execute()

    edges = [
        edge_type(
            node=node,
            cursor=offset_to_cursor(start_offset + i)
        )
        for i, node in enumerate(_slice)
    ]

    first_edge_cursor = edges[0].cursor if edges else None
    last_edge_cursor = edges[-1].cursor if edges else None
    lower_bound = after_offset + 1 if after else 0
    upper_bound = before_offset if before else list_length

    return connection_type(
        edges=edges,
        page_info=pageinfo_type(
            start_cursor=first_edge_cursor,
            end_cursor=last_edge_cursor,
            has_previous_page=(
                isinstance(last, int) and start_offset > lower_bound
            ),
            has_next_page=isinstance(first, int) and end_offset < upper_bound
        )
    )
