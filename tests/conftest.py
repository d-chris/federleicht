import random
import string

import pandas as pd
import pytest
from pathlibutil import Path

from federleicht.config import CACHE


@pytest.fixture
def cache() -> str:
    """
    random generated cachefile name
    """
    name = "".join(
        random.choices(
            string.hexdigits,
            k=CACHE.digest,
        )
    )

    return name.lower()


@pytest.fixture
def cachefile(cache):
    """
    cache file with random name in cache directory.
    """

    try:
        file = Path(CACHE.dir).joinpath(cache)

        yield file

    finally:
        file.delete(missing_ok=True)
        file.with_suffix(CACHE.attrs).delete(missing_ok=True)


@pytest.fixture
def tmp_cachefile(tmp_path, cache):
    """
    cache file with random name in temp directory.
    """

    cache_file = tmp_path / cache

    cache_file.touch()

    return cache_file


@pytest.fixture
def dataframe() -> pd.DataFrame:
    """
    temp dataframe without attrs
    """
    return pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})


@pytest.fixture
def dataframe_attrs(dataframe, tmp_cachefile):
    """
    copy of temp dataframe with "pytest" in attrs
    """

    df = dataframe.copy()

    df.attrs["from_cache"] = tmp_cachefile.as_posix()

    return df


@pytest.fixture
def mock_hash(mocker, cachefile) -> Path:

    mocker.patch(
        "federleicht.hash.function",
        return_value=cachefile.name,
    )

    return cachefile


@pytest.fixture
def csvframe(dataframe: pd.DataFrame, tmp_path):

    csvfile = Path(tmp_path) / "data.csv"

    dataframe.to_csv(csvfile, index=False)

    return (csvfile, dataframe)
