"""
The `unique` function generates a determanistic hash for all positional and keyword
arguments.

The hash is calculated with over the json string representation of all arguments.
The order of the keyword arguments is not relevant, all arguments must be serializable.

For `os.PathLike` objects a tuple with the resolved path, size and modification time is
used for hashing to detect if the file changed.

For `numpy.ndarray`, `pandas.DataFrame` and `pandas.Series` a tuple of the type and the
binary representation is used for hashing to detect if the data changed.
"""

import io
import json
import os
import pathlib
import types
from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from fractions import Fraction
from types import MappingProxyType
from typing import Any, Dict

import pandas as pd

try:
    from xxhash import xxh128 as hash  # type: ignore
except ModuleNotFoundError:
    from hashlib import md5 as hash


class _Hash(ABC):  # pragma: no cover
    """
    Abstract base class for hashing algorithms to use as type hint for the `hash`
    function.
    """

    @abstractmethod
    def __init__(self, readable: bytes) -> None:
        pass

    @abstractmethod
    def update(self, data: bytes) -> None:
        """
        Update the hash object with the bytes in data. Repeated calls
        are equivalent to a single call with the concatenation of all
        the arguments.
        """
        pass

    @abstractmethod
    def digest(self) -> bytes:
        """
        Return the digest of the bytes passed to the update() method
        so far as a bytes object.
        """
        pass

    @abstractmethod
    def hexdigest(self) -> str:
        """
        Like digest() except the digest is returned as a string
        of double length, containing only hexadecimal digits.
        """
        pass

    @abstractmethod
    def copy(self) -> "_Hash":
        """
        Return a copy (clone) of the hash object. This can be used to
        efficiently compute the digests of datas that share a common
        initial substring.
        """
        pass


def representation(obj: Any) -> str:
    """
    Return an unique string representation of the object.

    Raises a TypeError if the given object is not an immutable type.
    """
    immutable_types = (
        datetime,
        int,
        float,
        complex,
        str,
        tuple,
        frozenset,
        bytes,
        Decimal,
        Fraction,
        MappingProxyType,
    )

    if not isinstance(obj, immutable_types):
        raise TypeError(
            f"Object of type {type(obj).__qualname__} is not immutable: {obj}"
        )

    return str(obj)


def json_encoder(obj: Any) -> str:
    """
    Encode an object to a unique string representation, for mutable types it can result
    in returning a hexdigest of the object.
    """

    # pathlib.Path
    if isinstance(obj, os.PathLike):
        p = pathlib.Path(obj)
        return str(
            (
                p.resolve().as_posix(),
                p.stat().st_size,
                p.stat().st_mtime,
            )
        )

    # pandas.DataFrame
    if hasattr(obj, "to_feather"):
        buffer = io.BytesIO()
        obj.to_feather(buffer)
        return str(
            (
                type(obj),
                hash(buffer.getvalue()).hexdigest(),
                unique(**obj.attrs).hexdigest(),
            )
        )

    if isinstance(obj, pd.Series):
        return json_encoder(obj.to_frame())

    # numpy.ndarray
    if hasattr(obj, "tobytes"):
        return str(
            (
                type(obj),
                hash(obj.tobytes()).hexdigest(),
            )
        )

    if isinstance(obj, types.FunctionType):
        return str(
            (
                obj.__qualname__,
                hash(obj.__code__.co_code).hexdigest(),
            )
        )

    return representation(obj)


def dumps(
    *args: Any,
    **kwargs: Dict[str, Any],
) -> str:
    """
    Generate a JSON string for all arguments and keyword arguments.
    """

    data = json.dumps(
        (args, kwargs),
        sort_keys=True,
        default=json_encoder,
        indent=4,
    )

    return data


def unique(
    *args: Any,
    **kwargs: Dict[str, Any],
) -> _Hash:
    """
    Generate unique hash for all positional and keyword arguments. The order of the
    keyword arguments is not relevant.
    """

    data = dumps(*args, **kwargs)

    return hash(data.encode())


__all__ = [
    "unique",
    "hash",
]
