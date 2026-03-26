import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import books
from books import BookCollection


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

def test_add_duplicate_book():
    collection = BookCollection()
    collection.add_book("1984", "George Orwell", 1949)
    result = collection.add_book("1984", "George Orwell", 1949)
    assert isinstance(result, str)
    assert "already exists" in result

def test_add_book_invalid_year():
    collection = BookCollection()
    result = collection.add_book("Book", "Author", 999)
    assert isinstance(result, str)
    assert "Error adding book" in result

def test_mark_book_as_read():
    collection = BookCollection()
    collection.add_book("Dune", "Frank Herbert", 1965)
    result = collection.mark_as_read("Dune")
    assert result == "Book marked as read"
    book = collection.find_book_by_title("Dune")
    assert book.read is True

def test_mark_book_as_read_invalid():
    collection = BookCollection()
    result = collection.mark_as_read("Nonexistent Book")
    assert isinstance(result, str)
    assert "not found" in result

def test_remove_book():
    collection = BookCollection()
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    result = collection.remove_book("The Hobbit")
    assert result == "Book removed"
    book = collection.find_book_by_title("The Hobbit")
    assert book is None

def test_remove_book_invalid():
    collection = BookCollection()
    result = collection.remove_book("Nonexistent Book")
    assert isinstance(result, str)
    assert "not found" in result

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
    result = collection.add_review("NoBook", "user", "Comment", 4)
    assert isinstance(result, str)
    assert "not found" in result

def test_add_review_invalid_rating():
    collection = BookCollection()
    collection.add_book("Book2", "Author2", 2001)
    result = collection.add_review("Book2", "user", "Bad", 6)
    assert isinstance(result, str)
    assert "Error adding review" in result

def test_remove_review():
    collection = BookCollection()
    collection.add_book("Book3", "Author3", 2002)
    collection.add_review("Book3", "user", "Nice", 4)
    result = collection.remove_review("Book3", "user", "Nice")
    assert result == "Review removed"
    reviews = collection.list_reviews("Book3")
    assert len(reviews) == 0

def test_remove_review_not_found():
    collection = BookCollection()
    collection.add_book("Book4", "Author4", 2003)
    result = collection.remove_review("Book4", "user", "NoComment")
    assert result == "Review not found"

def test_mark_as_unread():
    collection = BookCollection()
    collection.add_book("Book5", "Author5", 2004)
    collection.mark_as_read("Book5")
    result = collection.mark_as_unread("Book5")
    assert result == "Book marked as unread"
    book = collection.find_book_by_title("Book5")
    assert book.read is False

def test_mark_as_unread_invalid():
    collection = BookCollection()
    result = collection.mark_as_unread("NoBook")
    assert isinstance(result, str)
    assert "not found" in result
