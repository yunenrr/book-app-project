"""
Custom exceptions for the Book Collection application.

This module provides a unified error handling approach with specific exception types
for different error scenarios.
"""


# ====================
# Base Exception
# ====================

class BookAppException(Exception):
    """Base exception for all book application errors."""
    
    def __init__(self, message: str, details: str = None) -> None:
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


# ====================
# Validation Exceptions
# ====================

class ValidationError(BookAppException):
    """Raised when input validation fails."""
    pass


class EmptyFieldError(ValidationError):
    """Raised when a required field is empty."""
    
    def __init__(self, field_name: str) -> None:
        super().__init__(f"{field_name} cannot be empty")
        self.field_name = field_name


class InvalidYearError(ValidationError):
    """Raised when year is out of valid range."""
    
    def __init__(self, year: int, min_year: int, max_year: int) -> None:
        super().__init__(
            f"Invalid year: {year}",
            f"Year must be between {min_year} and {max_year}"
        )
        self.year = year
        self.min_year = min_year
        self.max_year = max_year


class InvalidRatingError(ValidationError):
    """Raised when rating is out of valid range."""
    
    def __init__(self, rating: int) -> None:
        super().__init__(
            f"Invalid rating: {rating}",
            "Rating must be between 1 and 5"
        )
        self.rating = rating


class InputTooLongError(ValidationError):
    """Raised when input exceeds maximum length."""
    
    def __init__(self, field_name: str, length: int, max_length: int) -> None:
        super().__init__(
            f"{field_name} is too long",
            f"Maximum length is {max_length}, got {length}"
        )
        self.field_name = field_name
        self.length = length
        self.max_length = max_length


class MaxRetriesExceededError(ValidationError):
    """Raised when maximum input retry attempts are exceeded."""
    
    def __init__(self, attempts: int) -> None:
        super().__init__(
            f"Failed to get valid input after {attempts} attempts"
        )
        self.attempts = attempts


# ====================
# Book Operation Exceptions
# ====================

class BookOperationError(BookAppException):
    """Base exception for book-related operations."""
    pass


class BookNotFoundError(BookOperationError):
    """Raised when a book is not found in the collection."""
    
    def __init__(self, title: str) -> None:
        super().__init__(f"Book '{title}' not found")
        self.title = title


class DuplicateBookError(BookOperationError):
    """Raised when attempting to add a book that already exists."""
    
    def __init__(self, title: str, author: str) -> None:
        super().__init__(f"Book '{title}' by {author} already exists in collection")
        self.title = title
        self.author = author


class BookModificationError(BookOperationError):
    """Raised when a book modification operation fails."""
    pass


# ====================
# Review Exceptions
# ====================

class ReviewError(BookAppException):
    """Base exception for review-related operations."""
    pass


class ReviewNotFoundError(ReviewError):
    """Raised when a review is not found."""
    
    def __init__(self, book_title: str, user: str = None) -> None:
        if user:
            msg = f"Review by '{user}' not found for book '{book_title}'"
        else:
            msg = f"No reviews found for book '{book_title}'"
        super().__init__(msg)
        self.book_title = book_title
        self.user = user


# ====================
# Storage Exceptions
# ====================

class StorageError(BookAppException):
    """Base exception for storage-related operations."""
    pass


class SaveError(StorageError):
    """Raised when saving data fails."""
    
    def __init__(self, filename: str, reason: str = None) -> None:
        super().__init__(
            f"Failed to save to '{filename}'",
            reason
        )
        self.filename = filename


class LoadError(StorageError):
    """Raised when loading data fails."""
    
    def __init__(self, filename: str, reason: str = None) -> None:
        super().__init__(
            f"Failed to load from '{filename}'",
            reason
        )
        self.filename = filename


class CorruptedDataError(StorageError):
    """Raised when data file is corrupted."""
    
    def __init__(self, filename: str) -> None:
        super().__init__(f"Data file '{filename}' is corrupted or invalid")
        self.filename = filename


# ====================
# User Interface Exceptions
# ====================

class UIError(BookAppException):
    """Base exception for user interface operations."""
    pass


class UserCancelledError(UIError):
    """Raised when user cancels an operation."""
    
    def __init__(self) -> None:
        super().__init__("Operation cancelled by user")


class DisplayError(UIError):
    """Raised when displaying data fails."""
    
    def __init__(self, reason: str) -> None:
        super().__init__("Failed to display data", reason)
