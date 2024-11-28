import pathlib
import random
from datetime import datetime

import numpy as np
import pandas as pd
import pathlibutil
import pytest

import federleicht.args as args


@pytest.mark.parametrize(
    "obj",
    [
        list(),
        dict(),
    ],
    ids=lambda x: type(x).__name__,
)
def test_args_representation_raises(obj):
    """
    Test if the function raises a TypeError when the object is mutable.
    """
    with pytest.raises(TypeError):
        args.representation(obj)


@pytest.mark.parametrize(
    "obj",
    [
        datetime.now(),
        "string",
    ],
    ids=lambda x: type(x).__name__,
)
def test_args_representation(obj):
    """
    Test if the function returns a string representation of the immutable object.
    """

    result = args.representation(obj)

    assert isinstance(result, str)


@pytest.mark.parametrize(
    "obj",
    [
        datetime.now(),
        pd.DataFrame({"a": [1, 2, 3], " b": [4, 5, 6]}),
        pd.Series([1, 2, 3]),
        np.array([1, 2, 3]),
        pathlib.Path(__file__),
        pathlibutil.Path(__file__),
        lambda x: x,
    ],
    ids=lambda x: type(x).__name__,
)
def test_args_json_encoder(obj):
    """
    Test if the function returns a string representation of the certain mutable object.
    """

    result = args.json_encoder(obj)

    assert isinstance(result, str)


def test_args_dumps():
    """
    Test if the function returns a string representation of the certain mutable object.
    """

    result = args.dumps(
        datetime.now(),
        pd.DataFrame({"a": [1, 2, 3], " b": [4, 5, 6]}),
        foo="bar",
        numpy=np.array([1, 2, 3]),
        func=lambda x: x,
    )

    assert isinstance(result, str)


def test_args_dumps_raises():
    """
    Test if the function raises a TypeError when the object is mutable.
    """

    class Mutable:
        pass

    with pytest.raises(TypeError):
        args.dumps(Mutable())


def test_args_unique():
    """
    check if the unique hash is the same for the same arguments in different order.
    """

    arg = (1, "two", datetime.now())
    kwargs = {
        "c": pd.DataFrame({"a": [1, 2, 3], " b": [4, 5, 6]}),
        "b": pd.Series([1, 2, 3]),
        "a": np.array([1, 2, 3]),
    }

    unsorted_hash = args.unique(*arg, **kwargs)
    sorted_hash = args.unique(*arg, **dict(sorted(kwargs.items())))

    assert unsorted_hash.hexdigest() == sorted_hash.hexdigest()


def test_arqs_unique_file(cachefile):
    """
    unique hash should be diffrent for the same file when size and/or mtime changes.
    """

    with cachefile.open("w") as f:
        f.write("foo\n")
        f.flush()

    foo = args.unique(cachefile)

    with cachefile.open("a") as f:
        f.write("bar\n")
        f.flush()

    bar = args.unique(cachefile)

    assert foo.hexdigest() != bar.hexdigest()


def test_args_unique_series():
    """
    check if unique hash is the same for two different series with the same data.
    """

    data = random.sample(range(0, 256), 8)

    s1 = pd.Series(data)
    s2 = pd.Series(data)

    assert s1 is not s2
    assert args.unique(s1).hexdigest() == args.unique(s2).hexdigest()


def test_args_unique_series_attrs():
    """
    check if unique hash is different when the series is the same but with different
    attributes.
    """

    data = random.sample(range(0, 256), 8)

    s1 = pd.Series(data)
    s2 = pd.Series(data)

    s1.attrs["salt"] = "foo"
    s2.attrs["salt"] = "bar"

    assert args.unique(s1).hexdigest() != args.unique(s2).hexdigest()


@pytest.mark.parametrize(
    "func",
    [
        "hash",
        "unique",
    ],
)
def test_args_attr(func):
    """
    check if module has the required functions
    """
    assert hasattr(args, func)


@pytest.mark.parametrize(
    "attr",
    list(args._Hash.__abstractmethods__),
)
def test_args_hash(attr):
    """
    check if hasher has all required functions from abstract base class.
    """

    hasher = args.hash()

    assert hasattr(hasher, attr)
