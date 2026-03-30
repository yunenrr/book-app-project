import json
import os
import tempfile
import logging
from typing import List, Type, TYPE_CHECKING, Optional
from contextlib import contextmanager

if TYPE_CHECKING:
    from books import Book, Review

logger = logging.getLogger(__name__)


@contextmanager
def safe_file_write(filepath: str):
    """Context manager for safe atomic file writes.
    
    Creates a temporary file in the same directory, writes to it, and then
    atomically replaces the target file. If an error occurs, the temporary
    file is cleaned up and the original file remains unchanged.
    
    Args:
        filepath (str): Path to the target file.
        
    Yields:
        file: File handle opened for writing (text mode, UTF-8).
        
    Raises:
        IOError: If writing fails.
        
    Examples:
        >>> with safe_file_write("data.json") as f:
        ...     json.dump({"key": "value"}, f)
    """
    dir_name = os.path.dirname(os.path.abspath(filepath))
    fd, temp_path = tempfile.mkstemp(dir=dir_name, suffix='.json', text=True)
    
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            yield f
        
        # Atomic replace: if target exists, use replace; otherwise rename
        if os.path.exists(filepath):
            os.replace(temp_path, filepath)
        else:
            os.rename(temp_path, filepath)
    except Exception:
        # Clean up temp file on error
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise


@contextmanager
def safe_file_read(filepath: str):
    """Context manager for safe file reads.
    
    Opens a file for reading with UTF-8 encoding. Handles FileNotFoundError
    gracefully by yielding None.
    
    Args:
        filepath (str): Path to the file to read.
        
    Yields:
        Optional[file]: File handle opened for reading, or None if file not found.
        
    Examples:
        >>> with safe_file_read("data.json") as f:
        ...     if f:
        ...         data = json.load(f)
        ...     else:
        ...         data = []
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            yield f
    except FileNotFoundError:
        yield None

class BookStorage:
    """Handles persistent storage of book collections.
    
    Uses context managers for safe file operations with atomic writes.
    
    Attributes:
        data_file (str): Path to the JSON data file.
        
    Examples:
        >>> storage = BookStorage("my_books.json")
        >>> books = storage.load_books()
        >>> storage.save_books(books)
    """
    
    def __init__(self, data_file: str = "data.json"):
        """Initialize storage with a data file path.
        
        Args:
            data_file (str): Path to the JSON file for book storage.
                Defaults to "data.json".
        """
        self.data_file = data_file

    def load_books(self) -> List["Book"]:
        """Load books from the data file using safe context manager.
        
        Returns:
            List[Book]: List of loaded books, or empty list if file doesn't exist
                or is corrupted.
                
        Note:
            - Returns empty list if file not found (normal first run)
            - Logs warning and returns empty list if file is corrupted
            - Logs warning and returns empty list if book data is invalid
            
        Examples:
            >>> storage = BookStorage("books.json")
            >>> books = storage.load_books()
            >>> len(books) >= 0
            True
        """
        from books import Book
        
        with safe_file_read(self.data_file) as f:
            if f is None:
                # File doesn't exist - normal for first run
                return []
            
            try:
                data = json.load(f)
                return [Book(**b) for b in data]
            except json.JSONDecodeError:
                logger.warning(f"{self.data_file} is corrupted. Starting with empty collection.")
                return []
            except ValueError as e:
                logger.warning(f"Invalid book data in file: {e}. Starting with empty collection.")
                return []

    def save_books(self, books: List["Book"]) -> None:
        """Save books to the data file using atomic write context manager.
        
        Uses a temporary file and atomic replacement to ensure data integrity.
        If the write fails, the original file remains unchanged.
        
        Args:
            books (List[Book]): List of books to save.
            
        Raises:
            IOError: If the write operation fails.
            
        Examples:
            >>> from books import Book
            >>> storage = BookStorage("test_books.json")
            >>> books = [Book("Title", "Author", 2020)]
            >>> storage.save_books(books)  # doctest: +SKIP
        """
        try:
            with safe_file_write(self.data_file) as f:
                def book_to_dict(b):
                    """Convert a Book object to a dictionary for JSON serialization."""
                    d = b.__dict__.copy()
                    d['reviews'] = [r.__dict__ for r in b.reviews]
                    return d
                
                json.dump(
                    [book_to_dict(b) for b in books], 
                    f, 
                    indent=2, 
                    ensure_ascii=False
                )
        except (IOError, OSError) as e:
            raise IOError(f"Failed to save books to {self.data_file}: {e}")
