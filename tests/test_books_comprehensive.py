"""
Comprehensive test suite for books.py covering all functionality.

This test suite ensures complete coverage before any refactoring.
Tests are organized by class/functionality.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import datetime
import books
from books import Book, Review, BookCollection
from exceptions import (
    BookNotFoundError,
    DuplicateBookError,
    EmptyFieldError,
    InvalidYearError,
    InvalidRatingError,
    ReviewNotFoundError,
    SaveError
)


@pytest.fixture(autouse=True)
def use_temp_data_file(tmp_path, monkeypatch):
    """Use a temporary data file for each test."""
    temp_file = tmp_path / "data.json"
    temp_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(temp_file))


# ====================
# Review Class Tests
# ====================

class TestReview:
    """Test suite for the Review dataclass."""
    
    def test_review_creation_with_all_fields(self):
        """Test creating a review with all fields provided."""
        date_str = "2026-03-30T12:00:00"
        review = Review(user="Alice", comment="Great book!", rating=5, date=date_str)
        assert review.user == "Alice"
        assert review.comment == "Great book!"
        assert review.rating == 5
        assert review.date == date_str
    
    def test_review_creation_auto_date(self):
        """Test that date is auto-generated if not provided."""
        review = Review(user="Bob", comment="Good read", rating=4)
        assert review.date is not None
        assert isinstance(review.date, str)
        # Verify it's a valid ISO format date
        datetime.fromisoformat(review.date)
    
    def test_review_empty_user(self):
        """Test that empty user raises EmptyFieldError."""
        with pytest.raises(EmptyFieldError) as exc_info:
            Review(user="", comment="Comment", rating=3)
        assert "User" in str(exc_info.value)
    
    def test_review_whitespace_user(self):
        """Test that whitespace-only user raises EmptyFieldError."""
        with pytest.raises(EmptyFieldError):
            Review(user="   ", comment="Comment", rating=3)
    
    def test_review_empty_comment(self):
        """Test that empty comment raises EmptyFieldError."""
        with pytest.raises(EmptyFieldError) as exc_info:
            Review(user="User", comment="", rating=3)
        assert "Comment" in str(exc_info.value)
    
    def test_review_whitespace_comment(self):
        """Test that whitespace-only comment raises EmptyFieldError."""
        with pytest.raises(EmptyFieldError):
            Review(user="User", comment="   ", rating=3)
    
    def test_review_rating_too_low(self):
        """Test that rating < 1 raises InvalidRatingError."""
        with pytest.raises(InvalidRatingError):
            Review(user="User", comment="Comment", rating=0)
    
    def test_review_rating_too_high(self):
        """Test that rating > 5 raises InvalidRatingError."""
        with pytest.raises(InvalidRatingError):
            Review(user="User", comment="Comment", rating=6)
    
    def test_review_valid_ratings(self):
        """Test all valid rating values (1-5)."""
        for rating in range(1, 6):
            review = Review(user="User", comment="Comment", rating=rating)
            assert review.rating == rating


# ====================
# Book Class Tests
# ====================

class TestBook:
    """Test suite for the Book dataclass."""
    
    def test_book_creation_minimal(self):
        """Test creating a book with minimal required fields."""
        book = Book(title="1984", author="George Orwell", year=1949)
        assert book.title == "1984"
        assert book.author == "George Orwell"
        assert book.year == 1949
        assert book.read is False
        assert book.reviews == []
    
    def test_book_creation_with_read_status(self):
        """Test creating a book with read status."""
        book = Book(title="Test", author="Author", year=2000, read=True)
        assert book.read is True
    
    def test_book_creation_with_reviews(self):
        """Test creating a book with reviews."""
        reviews = [
            Review(user="User1", comment="Great!", rating=5),
            Review(user="User2", comment="Good", rating=4)
        ]
        book = Book(title="Test", author="Author", year=2000, reviews=reviews)
        assert len(book.reviews) == 2
        assert book.reviews[0].user == "User1"
    
    def test_book_empty_title(self):
        """Test that empty title raises EmptyFieldError."""
        with pytest.raises(EmptyFieldError) as exc_info:
            Book(title="", author="Author", year=2000)
        assert "Title" in str(exc_info.value)
    
    def test_book_whitespace_title(self):
        """Test that whitespace-only title raises EmptyFieldError."""
        with pytest.raises(EmptyFieldError):
            Book(title="   ", author="Author", year=2000)
    
    def test_book_empty_author(self):
        """Test that empty author raises EmptyFieldError."""
        with pytest.raises(EmptyFieldError) as exc_info:
            Book(title="Title", author="", year=2000)
        assert "Author" in str(exc_info.value)
    
    def test_book_whitespace_author(self):
        """Test that whitespace-only author raises EmptyFieldError."""
        with pytest.raises(EmptyFieldError):
            Book(title="Title", author="   ", year=2000)
    
    def test_book_year_too_low(self):
        """Test that year < 1000 raises InvalidYearError."""
        with pytest.raises(InvalidYearError):
            Book(title="Title", author="Author", year=999)
    
    def test_book_year_too_high(self):
        """Test that year > 2100 raises InvalidYearError."""
        with pytest.raises(InvalidYearError):
            Book(title="Title", author="Author", year=2101)
    
    def test_book_year_boundary_values(self):
        """Test boundary year values."""
        # Min valid year
        book_min = Book(title="Old Book", author="Author", year=1000)
        assert book_min.year == 1000
        
        # Max valid year
        book_max = Book(title="Future Book", author="Author", year=2100)
        assert book_max.year == 2100
    
    def test_book_non_integer_year(self):
        """Test that non-integer year raises InvalidYearError."""
        with pytest.raises(InvalidYearError):
            Book(title="Title", author="Author", year="2000")  # String instead of int


# ====================
# BookCollection Initialization Tests
# ====================

class TestBookCollectionInit:
    """Test suite for BookCollection initialization."""
    
    def test_collection_init_default_storage(self):
        """Test collection initialization with default storage."""
        collection = BookCollection()
        assert collection.books == []
        assert collection._title_index == {}
        assert collection._author_index == {}
    
    def test_collection_init_empty_file(tmp_path):
        """Test that collection handles empty data file."""
        collection = BookCollection()
        assert len(collection.books) == 0
    
    def test_collection_loads_existing_books(self, tmp_path, monkeypatch):
        """Test that collection loads books from existing file."""
        # Prepare a data file with books
        import json
        temp_file = tmp_path / "data_with_books.json"
        books_data = [
            {"title": "Book1", "author": "Author1", "year": 2000, "read": False, "reviews": []},
            {"title": "Book2", "author": "Author2", "year": 2001, "read": True, "reviews": []}
        ]
        temp_file.write_text(json.dumps(books_data))
        monkeypatch.setattr(books, "DATA_FILE", str(temp_file))
        
        collection = BookCollection()
        assert len(collection.books) == 2
        assert collection.books[0].title == "Book1"
        assert collection.books[1].read is True


# ====================
# BookCollection - Add Book Tests
# ====================

class TestBookCollectionAddBook:
    """Test suite for adding books to collection."""
    
    def test_add_book_basic(self):
        """Test adding a basic book."""
        collection = BookCollection()
        book = collection.add_book("Test Book", "Test Author", 2020)
        
        assert isinstance(book, Book)
        assert book.title == "Test Book"
        assert book.author == "Test Author"
        assert book.year == 2020
        assert len(collection.books) == 1
    
    def test_add_book_updates_title_index(self):
        """Test that adding a book updates the title index."""
        collection = BookCollection()
        collection.add_book("Indexed Book", "Author", 2020)
        
        assert "indexed book" in collection._title_index
        found = collection._title_index["indexed book"]
        assert found.title == "Indexed Book"
    
    def test_add_book_updates_author_index(self):
        """Test that adding a book updates the author index."""
        collection = BookCollection()
        collection.add_book("Book1", "John Doe", 2020)
        collection.add_book("Book2", "John Doe", 2021)
        
        assert "john doe" in collection._author_index
        assert len(collection._author_index["john doe"]) == 2
    
    def test_add_duplicate_book_same_case(self):
        """Test that adding duplicate book (same case) raises error."""
        collection = BookCollection()
        collection.add_book("Duplicate", "Author", 2020)
        
        with pytest.raises(DuplicateBookError) as exc_info:
            collection.add_book("Duplicate", "Author", 2020)
        assert "already exists" in str(exc_info.value)
    
    def test_add_duplicate_book_different_case(self):
        """Test that duplicate detection is case-insensitive."""
        collection = BookCollection()
        collection.add_book("Test Book", "Author", 2020)
        
        with pytest.raises(DuplicateBookError):
            collection.add_book("TEST BOOK", "author", 2020)
    
    def test_add_same_title_different_author(self):
        """Test that same title with different author is allowed."""
        collection = BookCollection()
        book1 = collection.add_book("Common Title", "Author A", 2020)
        book2 = collection.add_book("Common Title", "Author B", 2021)
        
        assert len(collection.books) == 2
        assert book1.author != book2.author
    
    def test_add_book_persists_to_storage(self):
        """Test that adding a book saves to storage."""
        collection = BookCollection()
        collection.add_book("Persisted Book", "Author", 2020)
        
        # Create new collection to verify persistence
        collection2 = BookCollection()
        assert len(collection2.books) == 1
        assert collection2.books[0].title == "Persisted Book"


# ====================
# BookCollection - List Books Tests
# ====================

class TestBookCollectionListBooks:
    """Test suite for listing books."""
    
    def test_list_books_empty(self):
        """Test listing books from empty collection."""
        collection = BookCollection()
        assert collection.list_books() == []
    
    def test_list_books_returns_all(self):
        """Test that list_books returns all books."""
        collection = BookCollection()
        collection.add_book("Book1", "Author1", 2020)
        collection.add_book("Book2", "Author2", 2021)
        collection.add_book("Book3", "Author3", 2022)
        
        books = collection.list_books()
        assert len(books) == 3
        assert books[0].title == "Book1"
        assert books[1].title == "Book2"
        assert books[2].title == "Book3"


# ====================
# BookCollection - Find Book Tests
# ====================

class TestBookCollectionFindBook:
    """Test suite for finding books."""
    
    def test_find_book_by_title_exists(self):
        """Test finding an existing book by title."""
        collection = BookCollection()
        collection.add_book("Findable Book", "Author", 2020)
        
        book = collection.find_book_by_title("Findable Book")
        assert book is not None
        assert book.title == "Findable Book"
    
    def test_find_book_by_title_case_insensitive(self):
        """Test that title search is case-insensitive."""
        collection = BookCollection()
        collection.add_book("Case Test", "Author", 2020)
        
        book = collection.find_book_by_title("CASE TEST")
        assert book is not None
        assert book.title == "Case Test"
    
    def test_find_book_by_title_not_found(self):
        """Test finding a non-existent book returns None."""
        collection = BookCollection()
        book = collection.find_book_by_title("Nonexistent")
        assert book is None
    
    def test_find_by_author_single_book(self):
        """Test finding books by author with one result."""
        collection = BookCollection()
        collection.add_book("Book", "Unique Author", 2020)
        
        books = collection.find_by_author("Unique Author")
        assert len(books) == 1
        assert books[0].author == "Unique Author"
    
    def test_find_by_author_multiple_books(self):
        """Test finding books by author with multiple results."""
        collection = BookCollection()
        collection.add_book("Book1", "Prolific Author", 2020)
        collection.add_book("Book2", "Prolific Author", 2021)
        collection.add_book("Book3", "Other Author", 2022)
        
        books = collection.find_by_author("Prolific Author")
        assert len(books) == 2
    
    def test_find_by_author_case_insensitive(self):
        """Test that author search is case-insensitive."""
        collection = BookCollection()
        collection.add_book("Book", "John Doe", 2020)
        
        books = collection.find_by_author("JOHN DOE")
        assert len(books) == 1
    
    def test_find_by_author_not_found(self):
        """Test finding books by non-existent author."""
        collection = BookCollection()
        books = collection.find_by_author("Ghost Author")
        assert books == []
    
    def test_find_by_author_returns_copy(self):
        """Test that find_by_author returns a copy, not reference."""
        collection = BookCollection()
        collection.add_book("Book", "Author", 2020)
        
        books1 = collection.find_by_author("Author")
        books2 = collection.find_by_author("Author")
        
        assert books1 is not books2  # Different list objects
        assert books1 == books2  # Same content


# ====================
# BookCollection - Search Tests
# ====================

class TestBookCollectionSearch:
    """Test suite for advanced search functionality."""
    
    def test_search_no_criteria_returns_all(self):
        """Test that search with no criteria returns all books."""
        collection = BookCollection()
        collection.add_book("Book1", "Author1", 2020)
        collection.add_book("Book2", "Author2", 2021)
        
        results = collection.search()
        assert len(results) == 2
    
    def test_search_by_author_only(self):
        """Test searching by author only."""
        collection = BookCollection()
        collection.add_book("Book1", "Target Author", 2020)
        collection.add_book("Book2", "Target Author", 2021)
        collection.add_book("Book3", "Other Author", 2022)
        
        results = collection.search(author="Target Author")
        assert len(results) == 2
        assert all(b.author == "Target Author" for b in results)
    
    def test_search_by_year_min_only(self):
        """Test searching by minimum year."""
        collection = BookCollection()
        collection.add_book("Old Book", "Author", 2000)
        collection.add_book("Newer Book", "Author", 2015)
        collection.add_book("Recent Book", "Author", 2020)
        
        results = collection.search(year_min=2015)
        assert len(results) == 2
        assert all(b.year >= 2015 for b in results)
    
    def test_search_by_year_max_only(self):
        """Test searching by maximum year."""
        collection = BookCollection()
        collection.add_book("Old Book", "Author", 2000)
        collection.add_book("Mid Book", "Author", 2010)
        collection.add_book("New Book", "Author", 2020)
        
        results = collection.search(year_max=2010)
        assert len(results) == 2
        assert all(b.year <= 2010 for b in results)
    
    def test_search_by_year_range(self):
        """Test searching by year range."""
        collection = BookCollection()
        collection.add_book("Book1", "Author", 2000)
        collection.add_book("Book2", "Author", 2010)
        collection.add_book("Book3", "Author", 2015)
        collection.add_book("Book4", "Author", 2020)
        
        results = collection.search(year_min=2010, year_max=2015)
        assert len(results) == 2
        assert all(2010 <= b.year <= 2015 for b in results)
    
    def test_search_by_read_status_true(self):
        """Test searching for read books."""
        collection = BookCollection()
        collection.add_book("Book1", "Author", 2020)
        collection.add_book("Book2", "Author", 2021)
        collection.mark_as_read("Book1")
        
        results = collection.search(read=True)
        assert len(results) == 1
        assert results[0].title == "Book1"
    
    def test_search_by_read_status_false(self):
        """Test searching for unread books."""
        collection = BookCollection()
        collection.add_book("Book1", "Author", 2020)
        collection.add_book("Book2", "Author", 2021)
        collection.mark_as_read("Book1")
        
        results = collection.search(read=False)
        assert len(results) == 1
        assert results[0].title == "Book2"
    
    def test_search_multiple_criteria(self):
        """Test searching with multiple criteria (AND operation)."""
        collection = BookCollection()
        collection.add_book("Book1", "Author A", 2015)
        collection.add_book("Book2", "Author A", 2020)
        collection.add_book("Book3", "Author B", 2020)
        collection.mark_as_read("Book2")
        
        results = collection.search(author="Author A", year_min=2018, read=True)
        assert len(results) == 1
        assert results[0].title == "Book2"


# ====================
# BookCollection - Mark Read/Unread Tests
# ====================

class TestBookCollectionReadStatus:
    """Test suite for marking books as read/unread."""
    
    def test_mark_as_read_success(self):
        """Test marking a book as read."""
        collection = BookCollection()
        collection.add_book("To Read", "Author", 2020)
        
        collection.mark_as_read("To Read")
        book = collection.find_book_by_title("To Read")
        assert book.read is True
    
    def test_mark_as_read_persists(self):
        """Test that read status persists to storage."""
        collection = BookCollection()
        collection.add_book("Book", "Author", 2020)
        collection.mark_as_read("Book")
        
        # Reload from storage
        collection2 = BookCollection()
        book = collection2.find_book_by_title("Book")
        assert book.read is True
    
    def test_mark_as_read_nonexistent_book(self):
        """Test marking non-existent book as read raises error."""
        collection = BookCollection()
        
        with pytest.raises(BookNotFoundError):
            collection.mark_as_read("Nonexistent")
    
    def test_mark_as_unread_success(self):
        """Test marking a book as unread."""
        collection = BookCollection()
        collection.add_book("Book", "Author", 2020)
        collection.mark_as_read("Book")
        
        collection.mark_as_unread("Book")
        book = collection.find_book_by_title("Book")
        assert book.read is False
    
    def test_mark_as_unread_persists(self):
        """Test that unread status persists to storage."""
        collection = BookCollection()
        collection.add_book("Book", "Author", 2020)
        collection.mark_as_read("Book")
        collection.mark_as_unread("Book")
        
        # Reload from storage
        collection2 = BookCollection()
        book = collection2.find_book_by_title("Book")
        assert book.read is False
    
    def test_mark_as_unread_nonexistent_book(self):
        """Test marking non-existent book as unread raises error."""
        collection = BookCollection()
        
        with pytest.raises(BookNotFoundError):
            collection.mark_as_unread("Nonexistent")


# ====================
# BookCollection - Remove Book Tests
# ====================

class TestBookCollectionRemoveBook:
    """Test suite for removing books."""
    
    def test_remove_book_success(self):
        """Test removing a book from collection."""
        collection = BookCollection()
        collection.add_book("To Remove", "Author", 2020)
        
        collection.remove_book("To Remove")
        assert len(collection.books) == 0
        assert collection.find_book_by_title("To Remove") is None
    
    def test_remove_book_updates_title_index(self):
        """Test that removing a book updates the title index."""
        collection = BookCollection()
        collection.add_book("Book", "Author", 2020)
        
        collection.remove_book("Book")
        assert "book" not in collection._title_index
    
    def test_remove_book_updates_author_index(self):
        """Test that removing a book updates the author index."""
        collection = BookCollection()
        collection.add_book("Book1", "Author", 2020)
        collection.add_book("Book2", "Author", 2021)
        
        collection.remove_book("Book1")
        assert len(collection._author_index["author"]) == 1
    
    def test_remove_last_book_by_author_cleans_index(self):
        """Test that removing last book by author removes author from index."""
        collection = BookCollection()
        collection.add_book("Only Book", "Sole Author", 2020)
        
        collection.remove_book("Only Book")
        assert "sole author" not in collection._author_index
    
    def test_remove_book_persists(self):
        """Test that book removal persists to storage."""
        collection = BookCollection()
        collection.add_book("Book1", "Author", 2020)
        collection.add_book("Book2", "Author", 2021)
        collection.remove_book("Book1")
        
        # Reload from storage
        collection2 = BookCollection()
        assert len(collection2.books) == 1
        assert collection2.books[0].title == "Book2"
    
    def test_remove_nonexistent_book(self):
        """Test removing non-existent book raises error."""
        collection = BookCollection()
        
        with pytest.raises(BookNotFoundError):
            collection.remove_book("Nonexistent")


# ====================
# BookCollection - Review Tests
# ====================

class TestBookCollectionReviews:
    """Test suite for book review functionality."""
    
    def test_add_review_success(self):
        """Test adding a review to a book."""
        collection = BookCollection()
        collection.add_book("Book", "Author", 2020)
        
        review = collection.add_review("Book", "Reviewer", "Great!", 5)
        assert isinstance(review, Review)
        assert review.user == "Reviewer"
        assert review.rating == 5
    
    def test_add_review_to_nonexistent_book(self):
        """Test adding review to non-existent book raises error."""
        collection = BookCollection()
        
        with pytest.raises(BookNotFoundError):
            collection.add_review("Nonexistent", "User", "Comment", 5)
    
    def test_add_multiple_reviews(self):
        """Test adding multiple reviews to a book."""
        collection = BookCollection()
        collection.add_book("Book", "Author", 2020)
        
        collection.add_review("Book", "User1", "Good", 4)
        collection.add_review("Book", "User2", "Great", 5)
        
        reviews = collection.list_reviews("Book")
        assert len(reviews) == 2
    
    def test_list_reviews_empty(self):
        """Test listing reviews for book with no reviews."""
        collection = BookCollection()
        collection.add_book("Book", "Author", 2020)
        
        reviews = collection.list_reviews("Book")
        assert reviews == []
    
    def test_list_reviews_nonexistent_book(self):
        """Test listing reviews for non-existent book returns empty list."""
        collection = BookCollection()
        
        reviews = collection.list_reviews("Nonexistent")
        assert reviews == []
    
    def test_list_reviews_returns_copy(self):
        """Test that list_reviews returns a copy, not reference."""
        collection = BookCollection()
        collection.add_book("Book", "Author", 2020)
        collection.add_review("Book", "User", "Comment", 5)
        
        reviews1 = collection.list_reviews("Book")
        reviews2 = collection.list_reviews("Book")
        
        assert reviews1 is not reviews2  # Different list objects
    
    def test_remove_review_success(self):
        """Test removing a review from a book."""
        collection = BookCollection()
        collection.add_book("Book", "Author", 2020)
        collection.add_review("Book", "User", "Comment", 5)
        
        collection.remove_review("Book", "User", "Comment")
        reviews = collection.list_reviews("Book")
        assert len(reviews) == 0
    
    def test_remove_review_from_nonexistent_book(self):
        """Test removing review from non-existent book raises error."""
        collection = BookCollection()
        
        with pytest.raises(BookNotFoundError):
            collection.remove_review("Nonexistent", "User", "Comment")
    
    def test_remove_nonexistent_review(self):
        """Test removing non-existent review raises error."""
        collection = BookCollection()
        collection.add_book("Book", "Author", 2020)
        
        with pytest.raises(ReviewNotFoundError):
            collection.remove_review("Book", "User", "Nonexistent Comment")
    
    def test_remove_review_exact_match(self):
        """Test that review removal requires exact user and comment match."""
        collection = BookCollection()
        collection.add_book("Book", "Author", 2020)
        collection.add_review("Book", "User1", "Comment A", 5)
        collection.add_review("Book", "User2", "Comment B", 4)
        
        collection.remove_review("Book", "User1", "Comment A")
        reviews = collection.list_reviews("Book")
        
        assert len(reviews) == 1
        assert reviews[0].user == "User2"
    
    def test_average_rating_single_review(self):
        """Test average rating with one review."""
        collection = BookCollection()
        collection.add_book("Book", "Author", 2020)
        collection.add_review("Book", "User", "Comment", 4)
        
        avg = collection.average_rating("Book")
        assert avg == 4.0
    
    def test_average_rating_multiple_reviews(self):
        """Test average rating with multiple reviews."""
        collection = BookCollection()
        collection.add_book("Book", "Author", 2020)
        collection.add_review("Book", "User1", "Comment", 5)
        collection.add_review("Book", "User2", "Comment", 3)
        collection.add_review("Book", "User3", "Comment", 4)
        
        avg = collection.average_rating("Book")
        assert avg == 4.0  # (5+3+4)/3 = 4.0
    
    def test_average_rating_rounds_to_two_decimals(self):
        """Test that average rating is rounded to 2 decimal places."""
        collection = BookCollection()
        collection.add_book("Book", "Author", 2020)
        collection.add_review("Book", "User1", "Comment", 5)
        collection.add_review("Book", "User2", "Comment", 4)
        
        avg = collection.average_rating("Book")
        assert avg == 4.5  # (5+4)/2 = 4.5
    
    def test_average_rating_no_reviews(self):
        """Test average rating for book with no reviews returns None."""
        collection = BookCollection()
        collection.add_book("Book", "Author", 2020)
        
        avg = collection.average_rating("Book")
        assert avg is None
    
    def test_average_rating_nonexistent_book(self):
        """Test average rating for non-existent book returns None."""
        collection = BookCollection()
        
        avg = collection.average_rating("Nonexistent")
        assert avg is None


# ====================
# Integration Tests
# ====================

class TestBookCollectionIntegration:
    """Integration tests for complete workflows."""
    
    def test_complete_book_lifecycle(self):
        """Test complete lifecycle: add, read, review, remove."""
        collection = BookCollection()
        
        # Add book
        book = collection.add_book("Life Cycle Book", "Author", 2020)
        assert book.title == "Life Cycle Book"
        assert book.read is False
        
        # Mark as read
        collection.mark_as_read("Life Cycle Book")
        assert collection.find_book_by_title("Life Cycle Book").read is True
        
        # Add review
        review = collection.add_review("Life Cycle Book", "Reviewer", "Excellent!", 5)
        assert review.rating == 5
        
        # Verify review exists
        reviews = collection.list_reviews("Life Cycle Book")
        assert len(reviews) == 1
        
        # Remove book
        collection.remove_book("Life Cycle Book")
        assert collection.find_book_by_title("Life Cycle Book") is None
    
    def test_multiple_books_same_author(self):
        """Test managing multiple books by same author."""
        collection = BookCollection()
        
        collection.add_book("Book 1", "Prolific Writer", 2015)
        collection.add_book("Book 2", "Prolific Writer", 2018)
        collection.add_book("Book 3", "Prolific Writer", 2020)
        
        # Find by author
        books = collection.find_by_author("Prolific Writer")
        assert len(books) == 3
        
        # Search by year
        recent = collection.search(author="Prolific Writer", year_min=2018)
        assert len(recent) == 2
        
        # Mark one as read
        collection.mark_as_read("Book 2")
        read_books = collection.search(author="Prolific Writer", read=True)
        assert len(read_books) == 1
    
    def test_persistence_across_sessions(self):
        """Test data persistence across multiple collection instances."""
        # Session 1: Add books
        collection1 = BookCollection()
        collection1.add_book("Persistent Book 1", "Author A", 2020)
        collection1.add_book("Persistent Book 2", "Author B", 2021)
        collection1.mark_as_read("Persistent Book 1")
        
        # Session 2: Verify and add review
        collection2 = BookCollection()
        assert len(collection2.books) == 2
        assert collection2.find_book_by_title("Persistent Book 1").read is True
        collection2.add_review("Persistent Book 1", "User", "Great!", 5)
        
        # Session 3: Verify everything
        collection3 = BookCollection()
        assert len(collection3.books) == 2
        reviews = collection3.list_reviews("Persistent Book 1")
        assert len(reviews) == 1
        assert reviews[0].rating == 5
