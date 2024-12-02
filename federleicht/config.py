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
        "buffer",
    ],
)

CACHE = CacheConfig(
    version=__version__,
    dir=".pandas_cache",
    digest=16,
    expires="seconds",
    attrs=".json",
    buffer=2**30,
)
"""
CACHE configuration.

Attributes:
    version (str): The version of the package.
    dir (str): The directory where the cache is stored.
    digest (int): The number of bytes in the hash digest.
    expires (str): The expiration time unit for the cache.
    attrs (str): The file extension for attribute storage.
    buffer (int): The buffer size for reading and writing feather files.
"""
