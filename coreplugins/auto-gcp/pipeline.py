"""
Thin wrapper that imports run_pipeline from the geo repo.

If ~/git/geo is not on the Python path (e.g. inside a Docker container),
a self-contained copy of gcp_pipeline.py should be placed here instead.
"""
import sys
import os

_GEO_REPO = os.path.expanduser('~/git/geo')
if _GEO_REPO not in sys.path:
    sys.path.insert(0, _GEO_REPO)

try:
    from gcp_pipeline import run_pipeline  # noqa: F401
except ImportError as e:
    raise ImportError(
        "Cannot import gcp_pipeline from {}. "
        "Either place a copy of gcp_pipeline.py in this directory "
        "or ensure ~/git/geo is on the Python path. "
        "Original error: {}".format(_GEO_REPO, e)
    )
