from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict
from datetime import datetime
from storage import BookStorage
from exceptions import (
    EmptyFieldError,
    InvalidYearError,
    InvalidRatingError,
    BookNotFoundError,
    DuplicateBookError,
    BookModificationError,
    ReviewNotFoundError,
    SaveError
)
import logging

DATA_FILE = "data.json"

logger = logging.getLogger(__name__)


@dataclass
class Review:
    """Represents a book review with user, comment, rating, and date.
    
    A review is automatically timestamped upon creation if no date is provided.
    
    Attributes:
        user (str): Name of the reviewer. Cannot be empty.
        comment (str): Review comment text. Cannot be empty.
        rating (int): Rating from 1 to 5 stars (inclusive).
        date (Optional[str]): ISO format timestamp. Auto-generated if None.
    
    Raises:
        EmptyFieldError: If user or comment is empty or whitespace-only.
        InvalidRatingError: If rating is not between 1 and 5.
    
    Examples:
        >>> review = Review(user="John", comment="Great book!", rating=5)
        >>> review.rating
        5
        >>> review.date  # Auto-generated ISO timestamp
        '2026-03-30T00:58:25.123456'
        
        >>> Review(user="", comment="Bad", rating=3)  # doctest: +SKIP
        EmptyFieldError: User cannot be empty
        
        >>> Review(user="Jane", comment="Okay", rating=6)  # doctest: +SKIP
        InvalidRatingError: Invalid rating: 6: Rating must be between 1 and 5
    """
    user: str
    comment: str
    rating: int
    date: Optional[str] = None  # ISO format

    def __post_init__(self) -> None:
        """Validate review data and auto-generate timestamp if needed."""
        if not self.user or not self.user.strip():
            raise EmptyFieldError("User")
        if not self.comment or not self.comment.strip():
            raise EmptyFieldError("Comment")
        if not (1 <= self.rating <= 5):
            raise InvalidRatingError(self.rating)
        if self.date is None:
            self.date = datetime.now().isoformat()

@dataclass
class Book:
    """Represents a book with title, author, publication year, and read status.
    
    Books can have multiple reviews attached. Title and author are used for
    duplicate detection (case-insensitive).
    
    Attributes:
        title (str): Book title. Cannot be empty.
        author (str): Book author. Cannot be empty.
        year (int): Publication year. Must be between 1000 and 2100.
        read (bool): Whether the book has been read. Defaults to False.
        reviews (List[Review]): List of reviews for this book. Defaults to empty list.
    
    Raises:
        EmptyFieldError: If title or author is empty or whitespace-only.
        InvalidYearError: If year is not an integer or not in valid range (1000-2100).
    
    Examples:
        >>> book = Book(title="1984", author="George Orwell", year=1949)
        >>> book.title
        '1984'
        >>> book.read
        False
        
        >>> Book(title="", author="Unknown", year=2020)  # doctest: +SKIP
        EmptyFieldError: Title cannot be empty
        
        >>> Book(title="Future Book", author="Author", year=999)  # doctest: +SKIP
        InvalidYearError: Invalid year: 999: Year must be between 1000 and 2100
    """
    title: str
    author: str
    year: int
    read: bool = False
    reviews: List[Review] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Validate book data after initialization and process reviews from JSON."""
        if not self.title or not self.title.strip():
            raise EmptyFieldError("Title")
        if not self.author or not self.author.strip():
            raise EmptyFieldError("Author")
        if not isinstance(self.year, int):
            raise InvalidYearError(self.year, 1000, 2100)
        # Allow legacy/unknown year sentinel 0 to preserve backward compatibility
        if self.year == 0:
            # Treat as unknown year; do not raise an exception
            pass
        elif self.year < 1000 or self.year > 2100:
            raise InvalidYearError(self.year, 1000, 2100)
        # Convert reviews from dicts if loaded from JSON
        if self.reviews and isinstance(self.reviews[0], dict):
            self.reviews = [Review(**r) for r in self.reviews]


class BookCollection:
    """Manages a collection of books with persistent storage.
    
    The collection maintains indexes for fast title and author lookups.
    All modifications are automatically persisted to storage.
    
    Attributes:
        storage (BookStorage): Storage backend for persistence.
        books (List[Book]): List of all books in the collection.
        
    Examples:
        >>> collection = BookCollection()
        >>> book = collection.add_book("1984", "George Orwell", 1949)
        >>> len(collection.books)
        1
        >>> collection.find_book_by_title("1984").author
        'George Orwell'
    """
    
    def __init__(self, storage: Optional[BookStorage] = None) -> None:
        """Initialize the book collection and load existing books.
        
        Args:
            storage (Optional[BookStorage]): Custom storage backend. If None,
                uses default BookStorage with DATA_FILE.
        
        Examples:
            >>> # Use default storage
            >>> collection = BookCollection()
            
            >>> # Use custom storage
            >>> from storage import BookStorage
            >>> custom_storage = BookStorage("custom_books.json")
            >>> collection = BookCollection(storage=custom_storage)
        """
        self.storage = storage or BookStorage(DATA_FILE)
        self.books: List[Book] = []
        self._title_index: Dict[str, Book] = {}
        self._author_index: Dict[str, List[Book]] = {}
        self._year_index: Dict[int, List[Book]] = {}
        self._load_books()

    def _load_books(self) -> None:
        """Load books from storage and rebuild indexes.
        
        If loading fails, initializes with empty collection and logs error.
        This ensures the application can start even if the data file is corrupted.
        """
        try:
            self.books = self.storage.load_books()
            self._rebuild_indexes()
        except Exception as e:
            logger.error(f"Error loading books: {e}")
            self.books = []
            self._title_index = {}
            self._author_index = {}

    def _rebuild_indexes(self) -> None:
        """Rebuild title and author indexes from the current book list.
        
        This method is called after loading books or when the collection
        needs to resynchronize its indexes.
        """
        self._title_index = {}
        self._author_index = {}
        self._year_index = {}
        for book in self.books:
            self._add_to_indexes(book)
    
    def _add_to_indexes(self, book: Book) -> None:
        """Add a book to the search indexes for O(1) lookup.
        
        Args:
            book (Book): Book to add to indexes.
        
        Note:
            - Title index maps lowercase title to book (one-to-one).
            - Author index maps lowercase author to list of books (one-to-many).
            - Year index maps integer year to list of books (one-to-many) for fast range queries.
        """
        title_key = book.title.lower()
        author_key = book.author.lower()
        year_key = book.year
        
        # Title index (one-to-one)
        self._title_index[title_key] = book
        
        # Author index (one-to-many)
        if author_key not in self._author_index:
            self._author_index[author_key] = []
        self._author_index[author_key].append(book)
        
        # Year index (one-to-many). Use integer year as key; include sentinel years (e.g., 0)
        if year_key not in self._year_index:
            self._year_index[year_key] = []
        self._year_index[year_key].append(book)
    
    def _remove_from_indexes(self, book: Book) -> None:
        """Remove a book from the search indexes.
        
        Args:
            book (Book): Book to remove from indexes.
        
        Note:
            If the author or year has no more books after removal, the key
            is deleted from the respective index.
        """
        title_key = book.title.lower()
        author_key = book.author.lower()
        year_key = book.year
        
        if title_key in self._title_index:
            del self._title_index[title_key]
        
        if author_key in self._author_index:
            self._author_index[author_key].remove(book)
            if not self._author_index[author_key]:
                del self._author_index[author_key]
        
        if year_key in self._year_index:
            try:
                self._year_index[year_key].remove(book)
            except ValueError:
                # Book not present in year index; log and continue
                logger.debug(f"Book not found in year index for year {year_key}: {book.title}")
            if not self._year_index[year_key]:
                del self._year_index[year_key]

    def save_books(self) -> None:
        """Save the current book collection to persistent storage.
        
        Raises:
            SaveError: If saving to storage fails. Contains the filename
                and error details.
        
        Examples:
            >>> collection = BookCollection()
            >>> collection.add_book("Title", "Author", 2020)  # Auto-saves
            >>> collection.save_books()  # Manual save
        """
        try:
            self.storage.save_books(self.books)
        except Exception as e:
            logger.error(f"Error saving books: {e}")
            raise SaveError(self.storage.data_file, str(e))

    def add_book(self, title: str, author: str, year: int) -> Book:
        """Add a new book to the collection.
        
        The book is validated, added to indexes, and automatically saved.
        Duplicate detection is case-insensitive and based on title + author.
        
        Args:
            title (str): Book title. Must not be empty or whitespace-only.
            author (str): Book author. Must not be empty or whitespace-only.
            year (int): Publication year. Must be between 1000 and 2100.
            
        Returns:
            Book: The newly created and added book.
        
        Raises:
            EmptyFieldError: If title or author is empty or whitespace-only.
            InvalidYearError: If year is not in valid range (1000-2100).
            DuplicateBookError: If a book with the same title and author
                already exists (case-insensitive comparison).
            SaveError: If saving to storage fails.
        
        Examples:
            >>> collection = BookCollection()
            >>> book = collection.add_book("1984", "George Orwell", 1949)
            >>> book.title
            '1984'
            >>> book.read
            False
            
            >>> # Duplicate detection (case-insensitive)
            >>> collection.add_book("1984", "George Orwell", 1949)  # doctest: +SKIP
            DuplicateBookError: Book '1984' by George Orwell already exists in collection
            
            >>> # Invalid year
            >>> collection.add_book("Ancient Book", "Unknown", 500)  # doctest: +SKIP
            InvalidYearError: Invalid year: 500: Year must be between 1000 and 2100
        """
        # Validate title
        if not title or not title.strip():
            raise EmptyFieldError("Title")
            
        # Check for duplicates
        title_key = title.lower()
        if title_key in self._title_index:
            existing = self._title_index[title_key]
            if existing.author.lower() == author.lower():
                logger.warning(f"Book '{title}' by {author} already exists in collection")
                raise DuplicateBookError(title, author)
        
        book = Book(title=title, author=author, year=year)
        self.books.append(book)
        self._add_to_indexes(book)
        self.save_books()
        return book

    def list_books(self) -> List[Book]:
        """Get all books in the collection.
        
        Returns:
            List[Book]: List of all books. Returns empty list if collection is empty.
        
        Examples:
            >>> collection = BookCollection()
            >>> collection.add_book("Book 1", "Author 1", 2020)
            >>> collection.add_book("Book 2", "Author 2", 2021)
            >>> len(collection.list_books())
            2
            >>> collection.list_books()[0].title
            'Book 1'
        """
        return self.books

    def add_review(self, title: str, user: str, comment: str, rating: int) -> Review:
        """Add a review to a book.
        
        The review is automatically timestamped and the collection is saved.
        
        Args:
            title (str): Title of the book to review.
            user (str): Name of the reviewer. Cannot be empty.
            comment (str): Review comment text. Cannot be empty.
            rating (int): Rating from 1 to 5 stars (inclusive).
            
        Returns:
            Review: The newly created review with auto-generated timestamp.
        
        Raises:
            BookNotFoundError: If no book with the given title exists.
            EmptyFieldError: If user or comment is empty or whitespace-only.
            InvalidRatingError: If rating is not between 1 and 5.
            SaveError: If saving to storage fails.
        
        Examples:
            >>> collection = BookCollection()
            >>> collection.add_book("Great Book", "John Doe", 2020)
            >>> review = collection.add_review("Great Book", "Alice", "Loved it!", 5)
            >>> review.user
            'Alice'
            >>> review.rating
            5
            
            >>> # Invalid rating
            >>> collection.add_review("Great Book", "Bob", "Bad", 6)  # doctest: +SKIP
            InvalidRatingError: Invalid rating: 6: Rating must be between 1 and 5
            
            >>> # Book not found
            >>> collection.add_review("Missing Book", "Alice", "Comment", 4)  # doctest: +SKIP
            BookNotFoundError: Book 'Missing Book' not found
        """
        book = self.find_book_by_title(title)
        if not book:
            raise BookNotFoundError(title)
        
        review = Review(user=user, comment=comment, rating=rating)
        book.reviews.append(review)
        self.save_books()
        return review

    def list_reviews(self, title: str) -> List[Review]:
        """Get all reviews for a book.
        
        Args:
            title (str): Title of the book.
        
        Returns:
            List[Review]: List of all reviews for the book. Returns empty list
                if book has no reviews or if book doesn't exist.
        
        Examples:
            >>> collection = BookCollection()
            >>> collection.add_book("Book", "Author", 2020)
            >>> collection.add_review("Book", "User1", "Great!", 5)
            >>> collection.add_review("Book", "User2", "Good", 4)
            >>> len(collection.list_reviews("Book"))
            2
            >>> collection.list_reviews("Nonexistent")
            []
        """
        book = self.find_book_by_title(title)
        if not book:
            return []
        return book.reviews.copy()

    def remove_review(self, title: str, user: str, comment: str) -> None:
        """Remove a specific review from a book.
        
        Reviews are identified by the combination of user and comment.
        The collection is automatically saved after removal.
        
        Args:
            title (str): Title of the book.
            user (str): Name of the reviewer.
            comment (str): Exact comment text of the review.
        
        Raises:
            BookNotFoundError: If no book with the given title exists.
            ReviewNotFoundError: If no review matches the user and comment.
            SaveError: If saving to storage fails.
        
        Examples:
            >>> collection = BookCollection()
            >>> collection.add_book("Book", "Author", 2020)
            >>> collection.add_review("Book", "Alice", "Great!", 5)
            >>> collection.remove_review("Book", "Alice", "Great!")
            >>> len(collection.list_reviews("Book"))
            0
            
            >>> # Review not found
            >>> collection.remove_review("Book", "Bob", "Missing")  # doctest: +SKIP
            ReviewNotFoundError: Review by 'Bob' not found for book 'Book'
        """
        book = self.find_book_by_title(title)
        if not book:
            raise BookNotFoundError(title)
        
        for r in book.reviews:
            if r.user == user and r.comment == comment:
                book.reviews.remove(r)
                self.save_books()
                return
        
        raise ReviewNotFoundError(title, user)

    def average_rating(self, title: str) -> Optional[float]:
        """Calculate the average rating for a book.
        
        Args:
            title (str): Title of the book.
        
        Returns:
            Optional[float]: Average rating rounded to 2 decimal places.
                Returns None if book has no reviews or doesn't exist.
        
        Examples:
            >>> collection = BookCollection()
            >>> collection.add_book("Book", "Author", 2020)
            >>> collection.add_review("Book", "User1", "Great", 5)
            >>> collection.add_review("Book", "User2", "Good", 4)
            >>> collection.average_rating("Book")
            4.5
            >>> collection.average_rating("No Reviews Book")
            None
        """
        book = self.find_book_by_title(title)
        if not book or not book.reviews:
            return None
        return round(sum(r.rating for r in book.reviews) / len(book.reviews), 2)

    def find_book_by_title(self, title: str) -> Optional[Book]:
        """Find a book by its title using O(1) index lookup.
        
        Search is case-insensitive.
        
        Args:
            title (str): Title to search for (case-insensitive).
        
        Returns:
            Optional[Book]: The book if found, None otherwise.
        
        Examples:
            >>> collection = BookCollection()
            >>> collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
            >>> book = collection.find_book_by_title("the hobbit")  # Case-insensitive
            >>> book.author
            'J.R.R. Tolkien'
            >>> collection.find_book_by_title("Missing Book") is None
            True
        """
        return self._title_index.get(title.lower())

    def mark_as_read(self, title: str) -> None:
        """Mark a book as read.
        
        The collection is automatically saved after the update.
        
        Args:
            title (str): Title of the book to mark as read.
        
        Raises:
            BookNotFoundError: If no book with the given title exists.
            SaveError: If saving to storage fails.
        
        Examples:
            >>> collection = BookCollection()
            >>> collection.add_book("Book", "Author", 2020)
            >>> collection.mark_as_read("Book")
            >>> collection.find_book_by_title("Book").read
            True
            
            >>> collection.mark_as_read("Nonexistent")  # doctest: +SKIP
            BookNotFoundError: Book 'Nonexistent' not found
        """
        book = self.find_book_by_title(title)
        if not book:
            raise BookNotFoundError(title)
        
        book.read = True
        self.save_books()
    
    def mark_as_unread(self, title: str) -> None:
        """Mark a book as unread.
        
        The collection is automatically saved after the update.
        
        Args:
            title (str): Title of the book to mark as unread.
        
        Raises:
            BookNotFoundError: If no book with the given title exists.
            SaveError: If saving to storage fails.
        
        Examples:
            >>> collection = BookCollection()
            >>> collection.add_book("Book", "Author", 2020)
            >>> collection.mark_as_read("Book")
            >>> collection.find_book_by_title("Book").read
            True
            >>> collection.mark_as_unread("Book")
            >>> collection.find_book_by_title("Book").read
            False
        """
        book = self.find_book_by_title(title)
        if not book:
            raise BookNotFoundError(title)
        
        book.read = False
        self.save_books()

    def remove_book(self, title: str) -> None:
        """Remove a book from the collection.
        
        The book is removed from both the list and all indexes.
        The collection is automatically saved after removal.
        
        Args:
            title (str): Title of the book to remove.
        
        Raises:
            BookNotFoundError: If no book with the given title exists.
            SaveError: If saving to storage fails.
        
        Examples:
            >>> collection = BookCollection()
            >>> collection.add_book("To Remove", "Author", 2020)
            >>> len(collection.books)
            1
            >>> collection.remove_book("To Remove")
            >>> len(collection.books)
            0
            
            >>> collection.remove_book("Nonexistent")  # doctest: +SKIP
            BookNotFoundError: Book 'Nonexistent' not found
        """
        book = self.find_book_by_title(title)
        if not book:
            raise BookNotFoundError(title)
        
        self.books.remove(book)
        self._remove_from_indexes(book)
        self.save_books()

    def find_by_author(self, author: str) -> List[Book]:
        """Find all books by a given author.
        
        Supports case-insensitive partial (substring) matches. If the provided
        author matches an exact author in the author index, that list is
        returned (fast path). Otherwise performs a case-insensitive substring
        search over all book authors.
        Returns a copy of the list to prevent external modifications.
        """
        if author is None:
            return []
        key = author.lower().strip()
        if not key:
            return []
        # Fast exact match using index
        if key in self._author_index:
            return self._author_index[key].copy()
        # Fallback to substring search across all books' authors
        return [b for b in self.books if key in b.author.lower()]

    def find_by_year_range(self, year_min: Optional[int] = None, year_max: Optional[int] = None) -> List[Book]:
        """Find books whose publication year is within the inclusive range [year_min, year_max].

        Uses an index by year for fast lookup. Both bounds are optional; None means unbounded.

        Args:
            year_min: Minimum year (inclusive) or None.
            year_max: Maximum year (inclusive) or None.

        Returns:
            List[Book]: Books matching the year range.

        Raises:
            InvalidYearError: If provided years are not integers or out of allowed range.
        """
        # Validate inputs
        if year_min is not None:
            if not isinstance(year_min, int):
                raise InvalidYearError(year_min, 1000, 2100)
            if year_min < 1000 or year_min > 2100:
                raise InvalidYearError(year_min, 1000, 2100)
        if year_max is not None:
            if not isinstance(year_max, int):
                raise InvalidYearError(year_max, 1000, 2100)
            if year_max < 1000 or year_max > 2100:
                raise InvalidYearError(year_max, 1000, 2100)

        if year_min is not None and year_max is not None and year_min > year_max:
            # Empty range
            return []

        # Collect matching years from the index
        results: List[Book] = []
        for y, books_in_year in self._year_index.items():
            if year_min is not None and y < year_min:
                continue
            if year_max is not None and y > year_max:
                continue
            results.extend(books_in_year)

        return results

    def search(
        self,
        author: Optional[str] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        read: Optional[bool] = None
    ) -> List[Book]:
        """Search books by multiple criteria.
        
        All provided criteria must match (AND operation). Criteria with None
        values are ignored. Search is case-insensitive for author names.
        
        Args:
            author (Optional[str]): Filter by author name (case-insensitive).
            year_min (Optional[int]): Minimum publication year (inclusive).
            year_max (Optional[int]): Maximum publication year (inclusive).
            read (Optional[bool]): Filter by read status (True/False).
        
        Returns:
            List[Book]: List of books matching all specified criteria.
                Returns all books if no criteria specified.
        
        Examples:
            >>> collection = BookCollection()
            >>> collection.add_book("Book 1", "Author A", 2010)
            >>> collection.add_book("Book 2", "Author A", 2020)
            >>> collection.add_book("Book 3", "Author B", 2015)
            >>> collection.mark_as_read("Book 1")
            
            >>> # Search by author
            >>> books = collection.search(author="Author A")
            >>> len(books)
            2
            
            >>> # Search by year range
            >>> books = collection.search(year_min=2015, year_max=2020)
            >>> len(books)
            2
            
            >>> # Search by read status
            >>> books = collection.search(read=True)
            >>> len(books)
            1
            
            >>> # Combine multiple criteria
            >>> books = collection.search(author="Author A", year_min=2015, read=False)
            >>> len(books)
            1
            >>> books[0].title
            'Book 2'
        """
        results = self.books
        
        if author is not None:
            key = author.lower().strip()
            if not key:
                results = []
            else:
                results = [b for b in results if key in b.author.lower()]
        
        if year_min is not None:
            results = [b for b in results if b.year >= year_min]
        
        if year_max is not None:
            results = [b for b in results if b.year <= year_max]
        
        if read is not None:
            results = [b for b in results if b.read == read]
        
        return results
