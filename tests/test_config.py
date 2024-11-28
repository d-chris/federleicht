import pytest

from federleicht.config import CACHE


@pytest.mark.parametrize(
    "key, type",
    [
        ("version", str),
        ("dir", str),
        ("digest", int),
        ("expires", str),
    ],
)
def test_config(key, type):
    assert isinstance(getattr(CACHE, key), type)
