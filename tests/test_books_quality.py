import pytest

from books import BookCollection
from storage import BookStorage
from exceptions import InvalidYearError, DuplicateBookError


def test_find_book_by_title_none(tmp_path):
    storage = BookStorage(str(tmp_path / "books.json"))
    collection = BookCollection(storage=storage)
    assert collection.find_book_by_title(None) is None


def test_search_invalid_year_type_raises(tmp_path):
    storage = BookStorage(str(tmp_path / "books.json"))
    collection = BookCollection(storage=storage)
    with pytest.raises(InvalidYearError):
        collection.search(year_min="2010")


def test_add_book_duplicate_raises(tmp_path):
    storage = BookStorage(str(tmp_path / "books.json"))
    collection = BookCollection(storage=storage)
    collection.add_book("1984", "George Orwell", 1949)
    with pytest.raises(DuplicateBookError):
        collection.add_book("1984", "George Orwell", 1949)
