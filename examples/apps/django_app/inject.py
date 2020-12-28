import os
import sys

__all__ = (
    'project_dir',
)


def project_dir(base):
    """Absolute path to a file from current directory."""
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), base).replace('\\', '/')
    )


sys.path.insert(0, project_dir("../../../src"))
sys.path.insert(0, project_dir("../../../examples"))
sys.path.insert(
    0,
    '/home/delusionalinsanity/bbrepos/graphene-elastic/examples'
)
