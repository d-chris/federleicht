import pathlib

import pandas as pd
import pandas.testing as pdt
import pytest
from pathlibutil import Path

from federleicht import from_cache
from federleicht.dataframe import cache_dataframe, is_expired


@pytest.mark.parametrize(
    "expires",
    [
        None,
        60,
        {"seconds": 60},
        {"minutes": 1},
        {"hours": 8},
        {"days": 7},
        {"weeks": 1},
        {"days": 7, "hours": -3},
    ],
    ids=lambda x: str(x),
)
def test_is_expired(expires):

    result = is_expired(Path(__file__), expires)

    assert isinstance(result, bool)


@pytest.mark.parametrize(
    "expires",
    [
        "None",
        "60",
        {"years": 100},
        {"centuries": 1},
    ],
    ids=lambda x: str(x),
)
def test_is_expired_typerror(expires):
    with pytest.raises(TypeError):
        is_expired(Path(__file__), expires)


def test_is_expired_filenotfound():
    with pytest.raises(FileNotFoundError):
        is_expired(Path("not_a_file"), 60)


def test_dataframe(dataframe, mock_hash):

    @cache_dataframe
    def wrapped():
        return dataframe

    df = wrapped()
    assert df is dataframe, "First call should return the dataframe."

    assert mock_hash.is_file(), "Cache file should exist."

    df = wrapped()

    assert (
        df is not dataframe
    ), "Second call should return the newly crated dataframe from cache."

    assert from_cache(df) is True
    pdt.assert_frame_equal(df, dataframe)


def test_dataframe_expires(dataframe, mock_hash):

    @cache_dataframe(expires=-60)
    def wrapped():
        return dataframe

    df = wrapped()
    assert df is dataframe, "First call should return the dataframe."

    assert mock_hash.is_file(), "Cache file should exist."

    df = wrapped()
    assert (
        df is dataframe
    ), "Second call should return the dataframe, because cache is expired."


def test_dataframe_cache_dir(dataframe, mock_hash, tmp_path):

    @cache_dataframe(cache_dir=tmp_path)
    def wrapped():
        return dataframe

    _ = wrapped()

    assert not mock_hash.is_file()
    assert Path(tmp_path).joinpath(mock_hash.name).is_file()


def test_dataframe_attrs(dataframe, mock_hash):

    @cache_dataframe(cache_attrs=True)
    def wrapped():
        dataframe.attrs["test"] = "test"
        return dataframe

    _ = wrapped()

    with pytest.raises(KeyError):
        _ = dataframe.attrs["from_cache"]

    df = wrapped()

    assert from_cache(df) is True
    assert df.attrs["test"] == "test"


def test_dataframe_args(dataframe: pd.DataFrame, tmp_path: pathlib.Path):

    @cache_dataframe(cache_dir=tmp_path)
    def wrapped(*args, **kwargs):
        return dataframe

    df = wrapped()
    assert from_cache(df) is False

    df = wrapped("hello", "world")
    assert from_cache(df) is False

    df = wrapped("hello", "world")
    assert from_cache(df) is True

    df = wrapped()
    assert from_cache(df) is True
