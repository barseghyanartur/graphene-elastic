#!/usr/bin/env python
import os
import sys
from IPython import start_ipython


def project_dir(base):
    """Absolute path to a file from current directory."""
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), base).replace('\\', '/')
    )


def main():
    sys.path.insert(0, project_dir("src"))
    sys.path.insert(0, project_dir("examples"))
    start_ipython(argv=[])


if __name__ == '__main__':
    sys.exit(main())
