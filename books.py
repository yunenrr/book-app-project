from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict
from datetime import datetime
from storage import BookStorage
import logging

DATA_FILE = "data.json"

logger = logging.getLogger(__name__)


@dataclass
class Review:
    user: str
    comment: str
    rating: int
    date: Optional[str] = None  # ISO format

    def __post_init__(self) -> None:
        if not self.user or not self.user.strip():
            raise ValueError("User cannot be empty")
        if not self.comment or not self.comment.strip():
            raise ValueError("Comment cannot be empty")
        if not (1 <= self.rating <= 5):
            raise ValueError("Rating must be between 1 and 5")
        if self.date is None:
            self.date = datetime.now().isoformat()

@dataclass
class Book:
    title: str
    author: str
    year: int
    read: bool = False
    reviews: List[Review] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Validate book data after initialization."""
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        if not self.author or not self.author.strip():
            raise ValueError("Author cannot be empty")
        if not isinstance(self.year, int):
            raise ValueError("Year must be an integer")
        if self.year < 1000 or self.year > 2100:
            raise ValueError("Year must be between 1000 and 2100")
        # Convert reviews from dicts if loaded from JSON
        if self.reviews and isinstance(self.reviews[0], dict):
            self.reviews = [Review(**r) for r in self.reviews]


class BookCollection:
    def __init__(self, storage: Optional[BookStorage] = None) -> None:
        self.storage = storage or BookStorage(DATA_FILE)
        self.books: List[Book] = []
        self._title_index: Dict[str, Book] = {}
        self._author_index: Dict[str, List[Book]] = {}
        self._load_books()

    def _load_books(self) -> None:
        try:
            self.books = self.storage.load_books()
            self._rebuild_indexes()
        except Exception as e:
            logger.error(f"Error loading books: {e}")
            self.books = []
            self._title_index = {}
            self._author_index = {}

    def _rebuild_indexes(self) -> None:
        """Rebuild title and author indexes from the current book list."""
        self._title_index = {}
        self._author_index = {}
        for book in self.books:
            self._add_to_indexes(book)
    
    def _add_to_indexes(self, book: Book) -> None:
        """Add a book to the search indexes."""
        title_key = book.title.lower()
        author_key = book.author.lower()
        
        self._title_index[title_key] = book
        
        if author_key not in self._author_index:
            self._author_index[author_key] = []
        self._author_index[author_key].append(book)
    
    def _remove_from_indexes(self, book: Book) -> None:
        """Remove a book from the search indexes."""
        title_key = book.title.lower()
        author_key = book.author.lower()
        
        if title_key in self._title_index:
            del self._title_index[title_key]
        
        if author_key in self._author_index:
            self._author_index[author_key].remove(book)
            if not self._author_index[author_key]:
                del self._author_index[author_key]

    def save_books(self) -> Optional[str]:
        """Save the current book collection using the storage class."""
        try:
            self.storage.save_books(self.books)
            return None
        except Exception as e:
            logger.error(f"Error saving books: {e}")
            return f"Error saving books: {e}"

    def add_book(self, title: str, author: str, year: int) -> Optional[Book]:
        """
        Add a new book to the collection.
        
        Raises:
            ValueError: If book data is invalid or book already exists.
            IOError: If saving to file fails.
        """
        # Check for duplicates
        title_key = title.lower()
        if title_key in self._title_index:
            existing = self._title_index[title_key]
            if existing.author.lower() == author.lower():
                logger.warning(f"Book '{title}' by {author} already exists in collection")
                return f"Book '{title}' by {author} already exists in collection"
        try:
            book = Book(title=title, author=author, year=year)
            self.books.append(book)
            self._add_to_indexes(book)
            err = self.save_books()
            if err:
                return err
            return book
        except Exception as e:
            logger.error(f"Error adding book: {e}")
            return f"Error adding book: {e}"

    def list_books(self) -> List[Book]:
        return self.books

    def add_review(self, title: str, user: str, comment: str, rating: int) -> Optional[Review]:
        """
        Add a review to a book by title.
        Raises ValueError if book not found or review invalid.
        """
        book = self.find_book_by_title(title)
        if not book:
            logger.warning(f"Book '{title}' not found")
            return f"Book '{title}' not found"
        try:
            review = Review(user=user, comment=comment, rating=rating)
            book.reviews.append(review)
            err = self.save_books()
            if err:
                return err
            return review
        except Exception as e:
            logger.error(f"Error adding review: {e}")
            return f"Error adding review: {e}"

    def list_reviews(self, title: str) -> List[Review]:
        """
        List all reviews for a book by title.
        Returns empty list if no reviews or book not found.
        """
        book = self.find_book_by_title(title)
        if not book:
            return []
        return book.reviews.copy()

    def remove_review(self, title: str, user: str, comment: str) -> str:
        """
        Remove a review by user and comment for a book.
        Returns True if removed, False if not found.
        """
        book = self.find_book_by_title(title)
        if not book:
            logger.warning(f"Book '{title}' not found")
            return f"Book '{title}' not found"
        for r in book.reviews:
            if r.user == user and r.comment == comment:
                try:
                    book.reviews.remove(r)
                    err = self.save_books()
                    if err:
                        return err
                    return "Review removed"
                except Exception as e:
                    logger.error(f"Error removing review: {e}")
                    return f"Error removing review: {e}"
        logger.warning("Review not found")
        return "Review not found"

    def average_rating(self, title: str) -> Optional[float]:
        """
        Get the average rating for a book by title.
        Returns None if no reviews or book not found.
        """
        book = self.find_book_by_title(title)
        if not book or not book.reviews:
            return None
        return round(sum(r.rating for r in book.reviews) / len(book.reviews), 2)

    def find_book_by_title(self, title: str) -> Optional[Book]:
        """Find a book by title (case-insensitive). O(1) lookup using index."""
        return self._title_index.get(title.lower())

    def mark_as_read(self, title: str) -> str:
        """Mark a book as read by title."""
        book = self.find_book_by_title(title)
        if book:
            try:
                book.read = True
                err = self.save_books()
                if err:
                    return err
                return "Book marked as read"
            except Exception as e:
                logger.error(f"Error marking as read: {e}")
                return f"Error marking as read: {e}"
        logger.warning(f"Book '{title}' not found")
        return f"Book '{title}' not found"
    
    def mark_as_unread(self, title: str) -> str:
        """Mark a book as unread by title."""
        book = self.find_book_by_title(title)
        if book:
            try:
                book.read = False
                err = self.save_books()
                if err:
                    return err
                return "Book marked as unread"
            except Exception as e:
                logger.error(f"Error marking as unread: {e}")
                return f"Error marking as unread: {e}"
        logger.warning(f"Book '{title}' not found")
        return f"Book '{title}' not found"

    def remove_book(self, title: str) -> str:
        """Remove a book by title."""
        book = self.find_book_by_title(title)
        if book:
            try:
                self.books.remove(book)
                self._remove_from_indexes(book)
                err = self.save_books()
                if err:
                    return err
                return "Book removed"
            except Exception as e:
                logger.error(f"Error removing book: {e}")
                return f"Error removing book: {e}"
        logger.warning(f"Book '{title}' not found")
        return f"Book '{title}' not found"

    def find_by_author(self, author: str) -> List[Book]:
        """Find all books by a given author. O(1) lookup using index."""
        return self._author_index.get(author.lower(), []).copy()
    
    def search(
        self,
        author: Optional[str] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        read: Optional[bool] = None
    ) -> List[Book]:
        self,
        author: Optional[str] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        read: Optional[bool] = None
    ) -> List[Book]:
        """
        Search books by multiple criteria.
        
        Args:
            author: Filter by author name (case-insensitive, optional)
            year_min: Minimum publication year (inclusive, optional)
            year_max: Maximum publication year (inclusive, optional)
            read: Filter by read status (optional)
        
        Returns:
            List of books matching all specified criteria.
        """
        results = self.books
        
        if author is not None:
            results = [b for b in results if b.author.lower() == author.lower()]
        
        if year_min is not None:
            results = [b for b in results if b.year >= year_min]
        
        if year_max is not None:
            results = [b for b in results if b.year <= year_max]
        
        if read is not None:
            results = [b for b in results if b.read == read]
        
        return results
