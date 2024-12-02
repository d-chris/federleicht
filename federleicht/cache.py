import re

import pandas as pd
from pathlibutil import Path

from federleicht.config import CACHE


def from_cache(df: pd.DataFrame) -> bool:
    """
    Check if a DataFrame was loaded from the cache.

    Args:
        df (pd.DataFrame): The DataFrame to check.

    Returns:
        bool: True if the DataFrame was loaded from the cache, False otherwise.
    """
    return df.attrs.get("from_cache", None) is not None


def delete_cache(cache_file: str) -> None:
    """
    Delete a cache file and its optional attributes file.

    Args:
        filename (str): The name of the cache file to delete.

    Example:
        >>> delete_cache("cachefile")
    """

    cache = Path(cache_file)

    cache.delete(missing_ok=True)
    cache.with_suffix(CACHE.attrs).delete(missing_ok=True)


def clear_cache(cache_dir: str = CACHE.dir, **kwargs) -> int:
    """
    Clear all cache files from the cache directory.

    Args:
        cache_dir (str): The directory where the cache files are stored.
        **kwargs: argument for `datetime.timedelta` to determine expiration time.

    Returns:
        int: The number of errors encountered while clearing the cache.

    Example:
        >>> clear_cache(weeks=2)
        0
    """
    cache_dir = Path(cache_dir)

    if not cache_dir.is_dir():
        return 0

    if not kwargs:
        is_expired = lambda _: True  # noqa
    else:
        is_expired = lambda file: file.is_expired(**kwargs)  # noqa

    regex = re.compile(f"[a-f0-9]{{{CACHE.digest * 2}}}", re.IGNORECASE)

    error = 0

    for file in cache_dir.glob("*"):
        if file.is_file() and regex.match(file.name) and is_expired(file):
            try:
                delete_cache(file)
            except Exception:
                error += 1

    return error
