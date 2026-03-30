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
