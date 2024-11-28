import json
from typing import Any, Callable, Dict

import pandas as pd
from pathlibutil import Path

import federleicht.args as args
from federleicht.config import CACHE


def lock(mydict: Dict, **kwargs) -> str:
    """
    Create a hash for the dict, skip all keys which are not of type int, float, str,
    bool, or None.

    All value types must be serializable to JSON.
    """

    skip_keys = (int, float, str, bool, type(None))

    cleandict = {k: v for k, v in mydict.items() if type(k) in skip_keys}

    attrs = json.dumps(cleandict, sort_keys=True, **kwargs)

    return args.hash(attrs.encode()).hexdigest()


def save(
    df: pd.DataFrame,
    filename: Path,
    default: Callable[[Any], str] = None,
) -> Path:
    """
    Dump the DataFrame attributes and their hash into a JSON file.

    Creates a JSON file only when `df.attrs` is not empty.

    Args:
        df (pd.DataFrame): The DataFrame whose attributes are to be dumped.
        file (str): The file path where the JSON file will be created.
        default (Callable[[Any], str]): A function to convert non-serializable objects.

    Returns:
        Path: The path to the created JSON file, or None if df.attrs is empty.
    """

    if not df.attrs:
        return None

    file: Path = filename.with_suffix(CACHE.attrs)

    file.write_text(
        json.dumps(
            {
                "attrs": df.attrs,
                "lock": lock(df.attrs, default=default),
            },
            default=default,
            indent=4,
        ),
    )

    return file


def restore(df: pd.DataFrame, filename: Path, **kwargs) -> pd.DataFrame:
    """
    Verify and restore the DataFrame attributes from a JSON file.

    Args:
        df (pd.DataFrame): The DataFrame to which the attributes will be loaded.
        file (str): The file path from where the JSON file will be read.
        **kwargs: Additional arguments for `json.loads`.

    Returns:
        pd.DataFrame: The DataFrame with updated attributes.
    """

    file: Path = filename.with_suffix(CACHE.attrs)

    try:
        cached = json.loads(file.read_text(), **kwargs)
    except FileNotFoundError:
        return df

    try:
        attrs = cached["attrs"]

        if lock(attrs) == cached["lock"]:
            df.attrs.update(attrs)
    except KeyError:
        pass

    return df


__all__ = [
    "save",
    "restore",
]
