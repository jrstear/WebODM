"""
Thin wrapper that imports run_pipeline from the geo repo.

If ~/git/geo is not on the Python path (e.g. inside a Docker container),
a self-contained copy of gcp_pipeline.py should be placed here instead.
"""
import sys
import os

# Search order:
#  1. Same directory as this file (works inside Docker container)
#  2. ~/git/geo (development / host environment)
_HERE = os.path.dirname(os.path.abspath(__file__))
_GEO_REPO = os.path.expanduser('~/git/geo')

for _path in [_HERE, _GEO_REPO]:
    if _path not in sys.path:
        sys.path.insert(0, _path)

try:
    from gcp_pipeline import run_pipeline  # noqa: F401
except ImportError as e:
    raise ImportError(
        "Cannot import gcp_pipeline. "
        "Place gcp_pipeline.py alongside this file ({}/) "
        "or ensure ~/git/geo is on the Python path. "
        "Original error: {}".format(_HERE, e)
    )
