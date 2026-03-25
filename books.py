import json
import os
import tempfile
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict

DATA_FILE = "data.json"


@dataclass
class Book:
    title: str
    author: str
    year: int
    read: bool = False
    
    def __post_init__(self):
        """Validate book data after initialization."""
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        if not self.author or not self.author.strip():
            raise ValueError("Author cannot be empty")
        if not isinstance(self.year, int):
            raise ValueError("Year must be an integer")
        if self.year < 1000 or self.year > 2100:
            raise ValueError("Year must be between 1000 and 2100")


class BookCollection:
    def __init__(self):
        self.books: List[Book] = []
        self._title_index: Dict[str, Book] = {}
        self._author_index: Dict[str, List[Book]] = {}
        self.load_books()

    def load_books(self):
        """Load books from the JSON file if it exists."""
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.books = [Book(**b) for b in data]
                self._rebuild_indexes()
        except FileNotFoundError:
            self.books = []
            self._title_index = {}
            self._author_index = {}
        except json.JSONDecodeError:
            print("Warning: data.json is corrupted. Starting with empty collection.")
            self.books = []
            self._title_index = {}
            self._author_index = {}
        except ValueError as e:
            print(f"Warning: Invalid book data in file: {e}. Starting with empty collection.")
            self.books = []
            self._title_index = {}
            self._author_index = {}
    
    def _rebuild_indexes(self):
        """Rebuild title and author indexes from the current book list."""
        self._title_index = {}
        self._author_index = {}
        for book in self.books:
            self._add_to_indexes(book)
    
    def _add_to_indexes(self, book: Book):
        """Add a book to the search indexes."""
        title_key = book.title.lower()
        author_key = book.author.lower()
        
        self._title_index[title_key] = book
        
        if author_key not in self._author_index:
            self._author_index[author_key] = []
        self._author_index[author_key].append(book)
    
    def _remove_from_indexes(self, book: Book):
        """Remove a book from the search indexes."""
        title_key = book.title.lower()
        author_key = book.author.lower()
        
        if title_key in self._title_index:
            del self._title_index[title_key]
        
        if author_key in self._author_index:
            self._author_index[author_key].remove(book)
            if not self._author_index[author_key]:
                del self._author_index[author_key]

    def save_books(self):
        """Save the current book collection to JSON using atomic write."""
        try:
            # Create temporary file in the same directory as the target file
            dir_name = os.path.dirname(os.path.abspath(DATA_FILE))
            fd, temp_path = tempfile.mkstemp(dir=dir_name, suffix='.json', text=True)
            
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    json.dump([asdict(b) for b in self.books], f, indent=2, ensure_ascii=False)
                
                # Atomic rename (on Windows, need to remove target first)
                if os.path.exists(DATA_FILE):
                    os.replace(temp_path, DATA_FILE)
                else:
                    os.rename(temp_path, DATA_FILE)
            except:
                # Clean up temp file if something went wrong
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise
        except (IOError, OSError) as e:
            raise IOError(f"Failed to save books to {DATA_FILE}: {e}")

    def add_book(self, title: str, author: str, year: int) -> Book:
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
                raise ValueError(f"Book '{title}' by {author} already exists in collection")
        
        book = Book(title=title, author=author, year=year)
        self.books.append(book)
        self._add_to_indexes(book)
        self.save_books()
        return book

    def list_books(self) -> List[Book]:
        return self.books

    def find_book_by_title(self, title: str) -> Optional[Book]:
        """Find a book by title (case-insensitive). O(1) lookup using index."""
        return self._title_index.get(title.lower())

    def mark_as_read(self, title: str) -> bool:
        """Mark a book as read by title."""
        book = self.find_book_by_title(title)
        if book:
            book.read = True
            self.save_books()
            return True
        return False
    
    def mark_as_unread(self, title: str) -> bool:
        """Mark a book as unread by title."""
        book = self.find_book_by_title(title)
        if book:
            book.read = False
            self.save_books()
            return True
        return False

    def remove_book(self, title: str) -> bool:
        """Remove a book by title."""
        book = self.find_book_by_title(title)
        if book:
            self.books.remove(book)
            self._remove_from_indexes(book)
            self.save_books()
            return True
        return False

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
