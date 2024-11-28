import pytest

import federleicht.hash as hash
from federleicht.config import CACHE


@pytest.fixture
def function():
    def wrapped(*args, **kwargs):
        return (args, kwargs)

    return wrapped


def test_salt():
    """
    check if salt is bytes and has less or equal to 8 characters.
    """

    version = hash.salt()

    assert isinstance(version, bytes)
    assert len(version) <= 8


def test_hash_wrap(function):
    """
    check if hash has the correct digest size.
    """

    arguments = function(1, 2, 3, a=4, b=5, c=6)

    b = hash.hash_wrapped(function, arguments)

    assert b.digest_size == CACHE.digest


def test_hash_wrap_kwargs(function):
    """
    check if hash is the same for different kwargs order.
    """

    a_arguments = function(1, 2, 3, a=4, b=5, c=6)
    b_arguments = function(1, 2, 3, c=6, b=5, a=4)

    a = hash.hash_wrapped(function, a_arguments)
    b = hash.hash_wrapped(function, b_arguments)

    assert a.hexdigest() == b.hexdigest()


def test_hash_function(function):
    """
    check if teh hash of a function an it's arguments returns a string.
    """
    arguments = function(1, 2, 3, a=4, b=5, c=6)

    b = hash.function(function, arguments)

    assert isinstance(b, str)


def test_hash_function_pepper(function):
    """
    check if the peper spices the hash up a bit.
    """

    arguments = function(1, 2, 3, a=4, b=5, c=6)

    def salt() -> bytes:
        return b"pepper"

    a = hash.function(function, arguments)
    b = hash.function(function, arguments, salt)

    assert a != b


def test_hash_function_code(function):
    """
    check if the change in a function changes the hash.
    """

    arguments = function()

    def foo() -> bytes:
        return "pepper".encode()

    a = hash.function(foo, arguments)

    def foo() -> bytes:
        return b"pepper"

    b = hash.function(foo, arguments)

    def bar() -> bytes:
        return b"pepper"

    c = hash.function(bar, arguments)

    assert a != b, "same function name but different code"
    assert b != c, "same code but different function name"
    assert c != a, "different function name and code"
