import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import books
from books import BookCollection
from exceptions import SaveError, InvalidYearError


class FakeStorage:
    def __init__(self, data_file="fake.json", load_result=None, save_raises=None):
        self.data_file = data_file
        self._last_saved = None
        self._load_result = load_result if load_result is not None else []
        self._save_raises = save_raises

    def load_books(self):
        return list(self._load_result)

    def save_books(self, books):
        if self._save_raises:
            raise self._save_raises
        # store a shallow copy to inspect from tests
        self._last_saved = list(books)


def test_save_books_wraps_unexpected_exceptions():
    # Storage that raises a generic Exception should cause BookCollection.save_books
    # to raise a SaveError wrapper
    storage = FakeStorage(save_raises=Exception("disk error"))
    coll = BookCollection(storage=storage)
    coll.books = []
    with pytest.raises(SaveError):
        coll.save_books()


def test_list_reviews_returns_copy_and_does_not_modify_internal_list():
    storage = FakeStorage()
    coll = BookCollection(storage=storage)
    coll.add_book("B1", "A1", 2000)
    coll.add_review("B1", "u1", "Good", 4)

    reviews = coll.list_reviews("B1")
    assert len(reviews) == 1

    # Mutate returned list and ensure internal book.reviews not affected
    reviews.clear()
    internal = coll.list_reviews("B1")
    assert len(internal) == 1


def test_average_rating_rounding_behavior():
    storage = FakeStorage()
    coll = BookCollection(storage=storage)
    coll.add_book("R1", "Auth", 2010)
    coll.add_review("R1", "u1", "r1", 5)
    coll.add_review("R1", "u2", "r2", 4)
    assert coll.average_rating("R1") == 4.5

    # More reviews leading to rounding to two decimals
    coll.add_review("R1", "u3", "r3", 4)
    assert coll.average_rating("R1") == 4.33


def test_find_by_author_partial_and_exact():
    storage = FakeStorage()
    coll = BookCollection(storage=storage)
    coll.add_book("BookA", "John Smith", 2001)
    coll.add_book("BookB", "Johnny Appleseed", 2002)

    # partial substring search
    res = coll.find_by_author("john")
    titles = {b.title for b in res}
    assert "BookA" in titles and "BookB" in titles

    # exact author fast-path
    res2 = coll.find_by_author("john smith")
    assert len(res2) == 1 and res2[0].title == "BookA"


def test_search_combination_filters_year_and_read():
    storage = FakeStorage()
    coll = BookCollection(storage=storage)
    coll.add_book("Book1", "A", 2000)
    coll.add_book("Book2", "A", 2010)
    coll.add_book("Book3", "B", 2015)

    coll.mark_as_read("Book1")
    coll.mark_as_read("Book3")

    # search for author A, year_min 2005, read True -> should return Book2 only if read True (but Book2 isn't read)
    res = coll.search(author="A", year_min=2005, read=None)
    assert any(b.title == "Book2" for b in res)

    res_read = coll.search(author="B", year_min=None, year_max=None, read=True)
    assert len(res_read) == 1 and res_read[0].title == "Book3"


def test_search_raises_on_invalid_year_bound():
    storage = FakeStorage()
    coll = BookCollection(storage=storage)
    with pytest.raises(InvalidYearError):
        coll.search(year_min="2000")


# ensure save_books is called on mutating operations (smoke test using FakeStorage)
def test_mutations_call_save_books_on_add_and_remove():
    storage = FakeStorage()
    coll = BookCollection(storage=storage)
    coll.add_book("S1", "X", 2005)
    assert storage._last_saved is not None
    coll.remove_book("S1")
    assert storage._last_saved is not None
