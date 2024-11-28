import pandas as pd
import pytest
from pathlibutil import Path

import federleicht.attrs as attrs
from federleicht.config import CACHE


@pytest.mark.parametrize(
    "mydict",
    [
        {"a": 1, "b": 2, "c": 3},
        {"c": "!", "a": "hello", "b": "world"},
    ],
    ids=str,
)
def test_lock_sortkeys(mydict):
    """
    check if the hash is the same for different order of keys
    """

    sdict = dict(sorted(mydict.items()))

    assert attrs.lock(mydict) == attrs.lock(sdict)


def test_lock_skipkeys():
    """
    check if invalid keys are skipped
    """

    mydict = {3: "three", 1: "one", 2: "two"}

    keydict = dict(sorted(mydict.items()))
    keydict[("foo", "bar")] = "will be ignored"

    assert attrs.lock(mydict) == attrs.lock(keydict)


def test_attrs_dump_none(dataframe: pd.DataFrame, tmp_cachefile):
    """
    check when attrs are empty no cache file is created.
    """

    assert dataframe.attrs == {}
    assert attrs.save(dataframe, tmp_cachefile) is None


def test_attrs_dump(dataframe_attrs: pd.DataFrame, tmp_cachefile):
    """
    check if the attrs are dumped into a file with correct suffix.
    """

    cacheattrs = attrs.save(dataframe_attrs, tmp_cachefile)

    assert cacheattrs.suffix == CACHE.attrs


def test_attrs_restore(dataframe, dataframe_attrs, tmp_cachefile):
    """
    check if the attrs are restored from a file.
    """

    assert attrs.save(dataframe_attrs, tmp_cachefile)
    assert dataframe.attrs == {}

    cached_df = attrs.restore(dataframe, tmp_cachefile)

    assert cached_df.attrs == dataframe_attrs.attrs


def test_attrs_restore_filenotfound(dataframe):
    """
    check if dataframe is returned when cachefile for attrs is missing.
    """

    cached_df = attrs.restore(dataframe, Path(__file__))

    assert cached_df.attrs == dataframe.attrs == {}


def test_attrs_restore_wronglock(mocker, dataframe, dataframe_attrs, tmp_cachefile):
    """
    check if the dataframe is returned when lock is invalid.
    """

    assert attrs.save(dataframe_attrs, tmp_cachefile)

    mocker.patch("federleicht.attrs.lock", return_value="None")

    cached_df = attrs.restore(dataframe, tmp_cachefile)

    assert cached_df.attrs == dataframe.attrs == {}


def test_attrs_restore_keyerror(mocker, dataframe, dataframe_attrs, tmp_cachefile):
    """
    check if dataframe is returned when keys are missing.
    """

    assert attrs.save(dataframe_attrs, tmp_cachefile)

    mocker.patch("json.loads", return_value={})

    cached_df = attrs.restore(dataframe, tmp_cachefile)

    assert cached_df.attrs == dataframe.attrs == {}
