import importlib.metadata
from collections import namedtuple

__version__ = importlib.metadata.version(__package__)

CacheConfig = namedtuple(
    "CacheConfig",
    [
        "version",
        "dir",
        "digest",
        "expires",
        "attrs",
    ],
)

CACHE = CacheConfig(
    version=__version__,
    dir=".pandas_cache",
    digest=16,
    expires="seconds",
    attrs=".json",
)
"""
CACHE configuration.

Attributes:
    version (str): The version of the package.
    dir (str): The directory where the cache is stored.
    digest (int): The digest size for hashing.
    expires (str): The expiration time unit for the cache.
    attrs (str): The file extension for attribute storage.
"""
