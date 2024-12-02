from functools import wraps
from typing import Any, Callable, Dict, Union

import pandas as pd
from pathlibutil import Path

import federleicht.attrs as attrs
import federleicht.hash as hash
from federleicht.cache import delete_cache
from federleicht.config import CACHE


def is_expired(file: Path, expires: Union[int, Dict[str, Any]]) -> bool:
    """Check if a file is expired.

    Args:
        file (Path): The file to check.
        expires (Union[int, Dict[str, Any]]): The expiration time in seconds or a
            dictionary containing kwargs for `datetime.timedelta`.

    Example:
        ```python
        file_to_cache = pathlibutil.Path(__file__)
        hours_to_cache: int = 90
        if is_expired(file_to_cache, expires={"hours": hours_to_cache}):
            file_to_cache.unlink()
        ```

    Returns:
        bool: True if the file is expired or expires is None, False otherwise.
    """

    if expires is None:
        return False

    if isinstance(expires, int):
        timedelta = {CACHE.expires: expires}
    elif isinstance(expires, dict):
        timedelta = expires
    else:
        raise TypeError(f"Invalid type expires: {type(expires)}. Must be int or dict.")

    return file.is_expired(**timedelta)


def cache_dataframe(
    func: Callable = None,
    *,
    cache_dir: str = CACHE.dir,
    expires: Union[int, Dict[str, int]] = None,
    cache_attrs: bool = False,
    pepper: Callable[[], bytes] = None,
):
    """
    Decorator to cache the result of a function that returns a pandas DataFrame.

    To reliable cache a DataFrame the decorated function must always return the same
    DataFrame for the same arguments!
    All arguments of the decorated function must be pickleable!

    The cache expires when:
    - the expiration time is reached
    - the decorated function changes
    - the arguments to the decorated function change
    - the pandas_cache version changes

    If the cache exists and is not expired, it loads the DataFrame from the cache.
    Otherwise, it calls the function, caches the result, and then returns the DataFrame.

    Args:
        func (callable, optional): The function to be decorated. Defaults to None.
        cache_dir (str, optional): Directory where the cache files will be stored.
            Defaults to CACHE.dir.
        expires (Union[int, Dict[str, int]], optional): Expiration time for the cache.
            Can be an integer representing the number of seconds or a dictionary with
            time units (e.g., {"hours": 1}). Defaults to None.
        cache_attrs (bool, optional): Whether to cache DataFrame attributes. These must
            all be serializable. Defaults to False.
        pepper (callable, optional): A function that returns a salt to spice up the
            hash of the cache. Defaults to None.

    Returns:
        callable: The wrapped function with caching functionality.

    Raises:
        TypeError: If the `expires` argument is not an int or dict.

    Example:
        ```python
        @cache_dataframe(expires={"hours": 1}, cache_attrs=True)
        def create_dataframe(*args, **kwargs):
            return pd.DataFrame(*args, **kwargs)
        ```
    """

    if func is None:
        return lambda f: cache_dataframe(
            f,
            expires=expires,
            cache_dir=cache_dir,
            cache_attrs=cache_attrs,
            pepper=pepper,
        )

    @wraps(func)
    def wrapper(*args, **kwargs):

        lock: str = hash.function(func, (args, kwargs), pepper)
        cache: Path = Path(cache_dir).joinpath(lock)

        try:
            if is_expired(cache, expires):
                delete_cache(cache)
                raise FileNotFoundError

            with cache.open("rb", buffering=CACHE.buffer) as f:
                df = pd.read_feather(f)

            df.attrs["from_cache"] = cache

            if cache_attrs is True:
                df = attrs.restore(df, cache)

        except FileNotFoundError:
            df: pd.DataFrame = func(*args, **kwargs)

            cache.parent.mkdir(parents=True, exist_ok=True)

            with cache.open("wb", buffering=CACHE.buffer) as f:
                df.to_feather(f)

            if cache_attrs is True:
                attrs.save(df, cache)

        return df

    return wrapper
