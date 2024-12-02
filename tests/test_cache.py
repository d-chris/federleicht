import pytest

import federleicht.cache as cache


@pytest.mark.parametrize(
    "fixture, cached",
    [
        ("dataframe", False),
        ("dataframe_attrs", True),
    ],
)
def test_from_cache(fixture, cached, request):
    """
    get temp dataframes from fixtures and check if they are cached.
    """
    dataframe = request.getfixturevalue(fixture)

    assert cache.from_cache(dataframe) is cached


def test_delete_dataframe_cache(tmp_cachefile):

    assert tmp_cachefile.is_file()

    cache.delete_cache(tmp_cachefile)

    assert not tmp_cachefile.is_file()


def test_delete_cache(tmp_cachefile):

    attr_cache = tmp_cachefile.with_suffix(cache.CACHE.attrs)
    attr_cache.touch()

    assert attr_cache.is_file()

    cache.delete_cache(tmp_cachefile)

    assert not attr_cache.is_file()
    assert not tmp_cachefile.is_file()


def test_clear_cache(tmp_cachefile):

    assert cache.clear_cache(tmp_cachefile.parent) == 0
    assert not tmp_cachefile.is_file()


def test_clear_cache_expired(tmp_cachefile):

    assert cache.clear_cache(tmp_cachefile.parent, days=1) == 0
    assert tmp_cachefile.is_file()


def test_clear_cache_error(mocker, tmp_cachefile):

    mocker.patch("federleicht.cache.delete_cache", side_effect=PermissionError)

    assert cache.clear_cache(tmp_cachefile.parent) == 1

    assert tmp_cachefile.is_file()


def test_clear_cache_different_file(tmp_path):

    file = tmp_path / "cachefile"
    file.touch()
    assert file.is_file()

    assert cache.clear_cache(tmp_path) == 0
    assert file.is_file()


def test_clear_cache_no_dir():

    assert cache.clear_cache("nonexistent") == 0
