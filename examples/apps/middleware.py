from time import time as timer
from graphene_elastic.logging import logger

__all__ = (
    'timing_middleware',
)


def timing_middleware(next, root, info, **args):
    start = timer()
    return_value = next(root, info, **args)
    duration = round((timer() - start) * 1000, 2)
    parent_type_name = root._meta.name \
        if root and hasattr(root, '_meta') \
        else ''
    logger.debug("timing_middleware")
    logger.debug(f"{parent_type_name}.{info.field_name}: {duration} ms")
    return return_value
