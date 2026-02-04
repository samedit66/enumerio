from enumerio import Enum


def test_map():
    assert Enum([1, 2, 3]).map(lambda x: x**2) == [1, 4, 9]


def test_chunk_every():
    assert Enum([1, 2, 3, 4, 5]).chunk_every(3) == [[1, 2, 3], [4, 5]]
