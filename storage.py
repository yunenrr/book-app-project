import json
import os
import tempfile
import logging
import shutil
from typing import List, Type, TYPE_CHECKING, Optional
from contextlib import contextmanager
from datetime import datetime

if TYPE_CHECKING:
    from books import Book, Review

from exceptions import CorruptedDataError, LoadError, SaveError

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
    Provides automatic backup and recovery from corrupted files.
    
    Attributes:
        data_file (str): Path to the JSON data file.
        backup_file (str): Path to the backup file.
        
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
        self.backup_file = f"{data_file}.backup"

    def _create_backup(self) -> None:
        """Create a backup of the current data file if it exists.
        
        The backup file has a .backup extension and is overwritten each time.
        """
        if os.path.exists(self.data_file):
            try:
                shutil.copy2(self.data_file, self.backup_file)
                logger.debug(f"Backup created: {self.backup_file}")
            except (IOError, OSError) as e:
                logger.warning(f"Failed to create backup: {e}")
    
    def _restore_from_backup(self) -> bool:
        """Attempt to restore data from backup file.
        
        Returns:
            bool: True if backup was successfully restored, False otherwise.
        """
        if not os.path.exists(self.backup_file):
            logger.warning("No backup file available for recovery")
            return False
        
        try:
            # Verify backup is valid JSON before restoring
            with open(self.backup_file, 'r', encoding='utf-8') as f:
                json.load(f)
            
            # Backup is valid, restore it
            shutil.copy2(self.backup_file, self.data_file)
            logger.info(f"Successfully restored data from backup")
            return True
        except json.JSONDecodeError:
            logger.error("Backup file is also corrupted")
            return False
        except (IOError, OSError) as e:
            logger.error(f"Failed to restore from backup: {e}")
            return False
    
    def load_books(self) -> List["Book"]:
        """Load books from the data file with automatic recovery from backup.
        
        Returns:
            List[Book]: List of loaded books, or empty list if file doesn't exist.
        
        Raises:
            CorruptedDataError: If the file is corrupted and backup recovery fails.
            LoadError: If there's an unrecoverable error loading the data.
                
        Note:
            - Returns empty list if file not found (normal first run)
            - Attempts to restore from backup if main file is corrupted
            - Raises CorruptedDataError if both main and backup are corrupted
            
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
                books = []
                skipped = 0
                for idx, b in enumerate(data, start=1):
                    try:
                        books.append(Book(**b))
                    except Exception as entry_err:
                        # Don't let a single bad entry prevent loading the rest
                        skipped += 1
                        logger.warning(f"Skipping invalid book entry #{idx} in {self.data_file}: {entry_err}")

                if skipped:
                    logger.info(f"Loaded {len(books)} books; skipped {skipped} invalid entries")
                else:
                    logger.debug(f"Successfully loaded {len(books)} books")

                return books
            except json.JSONDecodeError as e:
                logger.error(f"{self.data_file} is corrupted: {e}")
                
                # Attempt to restore from backup
                if self._restore_from_backup():
                    logger.info("Retrying load after backup restoration")
                    # Recursive call after restoration (only one level deep)
                    with safe_file_read(self.data_file) as f_retry:
                        if f_retry:
                            try:
                                data = json.load(f_retry)
                                books = [Book(**b) for b in data]
                                logger.info(f"Successfully loaded {len(books)} books from restored backup")
                                return books
                            except (json.JSONDecodeError, ValueError) as retry_error:
                                raise CorruptedDataError(self.data_file) from retry_error
                
                # No backup or backup failed
                raise CorruptedDataError(self.data_file) from e
            except (ValueError, TypeError, KeyError) as e:
                logger.error(f"Invalid book data in file: {e}")
                raise LoadError(self.data_file, str(e)) from e

    def _verify_saved_data(self) -> bool:
        """Verify that the saved data file is valid JSON.
        
        Returns:
            bool: True if file is valid, False otherwise.
        """
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                json.load(f)
            return True
        except (json.JSONDecodeError, IOError, OSError):
            return False
    
    def save_books(self, books: List["Book"]) -> None:
        """Save books to the data file with backup and verification.
        
        Creates a backup before saving, uses atomic write for safety,
        and verifies the saved data is valid JSON.
        
        Args:
            books (List[Book]): List of books to save.
            
        Raises:
            SaveError: If the write operation fails or verification fails.
            
        Examples:
            >>> from books import Book
            >>> storage = BookStorage("test_books.json")
            >>> books = [Book("Title", "Author", 2020)]
            >>> storage.save_books(books)  # doctest: +SKIP
        """
        # Create backup before saving
        self._create_backup()
        
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
            
            # Verify the saved data is valid
            if not self._verify_saved_data():
                logger.error("Saved data verification failed")
                # Restore from backup
                if self._restore_from_backup():
                    raise SaveError(self.data_file, "Data verification failed, restored from backup")
                else:
                    raise SaveError(self.data_file, "Data verification failed, backup restoration also failed")
            
            logger.debug(f"Successfully saved {len(books)} books")
            
        except (IOError, OSError) as e:
            logger.error(f"Failed to save books: {e}")
            # Attempt to restore backup if save failed
            self._restore_from_backup()
            raise SaveError(self.data_file, str(e)) from e
        except Exception as e:
            logger.error(f"Unexpected error while saving: {e}")
            # Attempt to restore backup for any other errors
            self._restore_from_backup()
            raise SaveError(self.data_file, f"Unexpected error: {e}") from e
