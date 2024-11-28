import importlib.metadata
from collections import namedtuple

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
    version=importlib.metadata.version(__package__),
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
