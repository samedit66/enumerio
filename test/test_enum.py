from enumerio import Enum


def test_map():
    assert Enum([1, 2, 3]).map(lambda x: x**2) == [1, 4, 9]


def test_chunk_every():
    assert Enum([1, 2, 3, 4, 5]).chunk_every(3) == [[1, 2, 3], [4, 5]]
    assert Enum([1, 2, 3, 4, 5]).chunk_every(3, 1) == [[1, 2, 3], [2, 3, 4], [3, 4, 5]]


def test_map_join():
    assert Enum([1, 2, 3]).map_join(str, "*") == "1*2*3"
    assert Enum([1, 2, 3]).map(str).join("*") == Enum([1, 2, 3]).map_join(str, "*")


def test_split():
    assert Enum([1, 2, 3]).split(2) == ([1, 2], [3])
    assert Enum([1, 2, 3]).split(10) == ([1, 2, 3], [])
    assert Enum([1, 2, 3]).split(0) == ([], [1, 2, 3])
    assert Enum([1, 2, 3]).split(-1) == ([1, 2], [3])
    assert Enum([1, 2, 3]).split(-5) == ([], [1, 2, 3])


def test_sublist():
    assert Enum([[1, 2, 3], [4, 5, 6]]).sublist(0, 1) == [[1, 2], [4, 5]]


def test_subdict():
    assert Enum([{"a": 1, "b": 2, "c": 3}, {"a": 5, "b": 6}]).subdict("a") == [
        {"a": 1},
        {"a": 5},
    ]


def test_select():
    assert Enum([{"a": 1, "b": 2, "c": 3}, {"a": 5, "b": 6}]).select("a") == [1, 5]
