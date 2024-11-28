"""
.. include:: ../README.md
"""

from federleicht.cache import clear_cache, delete_cache, from_cache
from federleicht.config import CACHE
from federleicht.dataframe import cache_dataframe

__all__ = [
    "from_cache",
    "clear_cache",
    "delete_cache",
    "cache_dataframe",
    "CACHE",
]
