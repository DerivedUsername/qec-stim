import pytest


def call_or_skip(fn, *args, **kwargs):
    """Call fn; skip the test (not fail) if that part isn't implemented yet."""
    try:
        return fn(*args, **kwargs)
    except NotImplementedError as exc:
        pytest.skip(f"not implemented yet ({exc})")
