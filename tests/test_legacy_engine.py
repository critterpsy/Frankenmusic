"""Pytest-discoverable wrapper for the legacy engine regression suite.

The original suite lives in `tests/test.py` because it predates the current
pytest-oriented layout. Re-exporting it here preserves the existing entrypoint
(`python3 tests/test.py`) while making the legacy checks part of the default
`pytest` run as well.
"""

from tests.test import *  # noqa: F401,F403
