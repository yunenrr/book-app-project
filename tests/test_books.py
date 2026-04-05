import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import books
from books import BookCollection
from exceptions import (
    BookNotFoundError,
    DuplicateBookError,
    EmptyFieldError,
    InvalidYearError,
    InvalidRatingError,
    ReviewNotFoundError
)


@pytest.fixture(autouse=True)
def use_temp_data_file(tmp_path, monkeypatch):
    """Use a temporary data file for each test."""
    temp_file = tmp_path / "data.json"
    temp_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(temp_file))


def test_add_book():
    collection = BookCollection()
    initial_count = len(collection.books)
    result = collection.add_book("1984", "George Orwell", 1949)
    assert isinstance(result, books.Book)
    assert len(collection.books) == initial_count + 1
    book = collection.find_book_by_title("1984")
    assert book is not None
    assert book.author == "George Orwell"
    assert book.year == 1949
    assert book.read is False

def test_add_book_empty_title():
    collection = BookCollection()
    with pytest.raises(EmptyFieldError) as exc_info:
        collection.add_book("", "Author", 2020)
    assert "Title" in str(exc_info.value)
    
    with pytest.raises(EmptyFieldError):
        collection.add_book("   ", "Author", 2020)

def test_add_duplicate_book():
    collection = BookCollection()
    collection.add_book("1984", "George Orwell", 1949)
    with pytest.raises(DuplicateBookError) as exc_info:
        collection.add_book("1984", "George Orwell", 1949)
    assert "already exists" in str(exc_info.value)

def test_add_book_invalid_year():
    collection = BookCollection()
    with pytest.raises(InvalidYearError):
        collection.add_book("Book", "Author", 999)

def test_mark_book_as_read():
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    collection.mark_as_read("Dune")
    book = collection.find_book_by_title("Dune")
    assert book.read is True

def test_mark_book_as_read_invalid():
    collection = BookCollection()
    with pytest.raises(BookNotFoundError) as exc_info:
        collection.mark_as_read("Nonexistent Book")
    assert "not found" in str(exc_info.value)

def test_remove_book():
    collection = BookCollection()
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    collection.remove_book("The Hobbit")
    book = collection.find_book_by_title("The Hobbit")
    assert book is None

def test_remove_book_invalid():
    collection = BookCollection()
    with pytest.raises(BookNotFoundError) as exc_info:
        collection.remove_book("Nonexistent Book")
    assert "not found" in str(exc_info.value)

def test_add_review():
    collection = BookCollection()
    collection.add_book("Book1", "Author1", 2000)
    result = collection.add_review("Book1", "user", "Great!", 5)
    assert isinstance(result, books.Review)
    reviews = collection.list_reviews("Book1")
    assert len(reviews) == 1
    assert reviews[0].user == "user"
    assert reviews[0].comment == "Great!"
    assert reviews[0].rating == 5

def test_add_review_invalid_book():
    collection = BookCollection()
    with pytest.raises(BookNotFoundError) as exc_info:
        collection.add_review("NoBook", "user", "Comment", 4)
    assert "not found" in str(exc_info.value)

def test_add_review_invalid_rating():
    collection = BookCollection()
    collection.add_book("Book2", "Author2", 2001)
    with pytest.raises(InvalidRatingError):
        collection.add_review("Book2", "user", "Bad", 6)

def test_remove_review():
    collection = BookCollection()
    collection.add_book("Book3", "Author3", 2002)
    collection.add_review("Book3", "user", "Nice", 4)
    collection.remove_review("Book3", "user", "Nice")
    reviews = collection.list_reviews("Book3")
    assert len(reviews) == 0

def test_remove_review_not_found():
    collection = BookCollection()
    collection.add_book("Book4", "Author4", 2003)
    with pytest.raises(ReviewNotFoundError):
        collection.remove_review("Book4", "user", "NoComment")

def test_mark_as_unread():
    collection = BookCollection()
    collection.add_book("Book5", "Author5", 2004)
    collection.mark_as_read("Book5")
    collection.mark_as_unread("Book5")
    book = collection.find_book_by_title("Book5")
    assert book.read is False

def test_mark_as_unread_invalid():
    collection = BookCollection()
    with pytest.raises(BookNotFoundError) as exc_info:
        collection.mark_as_unread("NoBook")
    assert "not found" in str(exc_info.value)

# ----------------------
# Tests for find_by_year_range
# ----------------------

def test_find_by_year_range_exact_bounds_returns_books():
    collection = BookCollection()
    collection.add_book("Old", "AuthorA", 1999)
    collection.add_book("Mid", "AuthorB", 2005)
    collection.add_book("New", "AuthorC", 2012)
    results = collection.find_by_year_range(1999, 2012)
    assert len(results) == 3


def test_find_by_year_range_min_only_returns_from_min_onwards():
    collection = BookCollection()
    collection.add_book("A", "X", 2008)
    collection.add_book("B", "Y", 2015)
    results = collection.find_by_year_range(2010, None)
    assert all(b.year >= 2010 for b in results) and len(results) == 1


def test_find_by_year_range_max_only_returns_up_to_max():
    collection = BookCollection()
    collection.add_book("A", "X", 1995)
    collection.add_book("B", "Y", 2005)
    results = collection.find_by_year_range(None, 2000)
    assert all(b.year <= 2000 for b in results) and len(results) == 1


def test_find_by_year_range_no_bounds_returns_all():
    collection = BookCollection()
    collection.add_book("One", "A", 2000)
    collection.add_book("Two", "B", 2010)
    results = collection.find_by_year_range(None, None)
    assert len(results) == 2


def test_find_by_year_range_min_greater_than_max_returns_empty():
    collection = BookCollection()
    collection.add_book("A", "X", 2000)
    results = collection.find_by_year_range(2010, 2000)
    assert results == []


def test_find_by_year_range_inclusive_bounds():
    collection = BookCollection()
    collection.add_book("EdgeLow", "E", 2000)
    collection.add_book("EdgeHigh", "E", 2010)
    results = collection.find_by_year_range(2000, 2010)
    years = {b.year for b in results}
    assert 2000 in years and 2010 in years


def test_find_by_year_range_multiple_books_same_year():
    collection = BookCollection()
    collection.add_book("Book1", "A", 2001)
    collection.add_book("Book2", "B", 2001)
    results = collection.find_by_year_range(2001, 2001)
    assert len(results) == 2


def test_find_by_year_range_invalid_type_raises_InvalidYearError():
    collection = BookCollection()
    collection.add_book("A", "X", 2000)
    with pytest.raises(InvalidYearError):
        collection.find_by_year_range("2000", "2010")
    with pytest.raises(InvalidYearError):
        collection.find_by_year_range(2000.5, 2010)


def test_find_by_year_range_index_updates_on_add_remove():
    collection = BookCollection()
    collection.add_book("Transient", "T", 2020)
    assert any(b.title == "Transient" for b in collection.find_by_year_range(2020, 2020))
    collection.remove_book("Transient")
    assert all(b.title != "Transient" for b in collection.find_by_year_range(2020, 2020))
