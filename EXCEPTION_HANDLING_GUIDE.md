# Exception Handling Guide

## Overview

This project uses a unified exception handling approach with custom exceptions for consistent error management across the application.

## Exception Hierarchy

```
BookAppException (Base)
├── ValidationError
│   ├── EmptyFieldError
│   ├── InvalidYearError
│   ├── InvalidRatingError
│   ├── InputTooLongError
│   └── MaxRetriesExceededError
├── BookOperationError
│   ├── BookNotFoundError
│   ├── DuplicateBookError
│   └── BookModificationError
├── ReviewError
│   └── ReviewNotFoundError
├── StorageError
│   ├── SaveError
│   ├── LoadError
│   └── CorruptedDataError
└── UIError
    ├── UserCancelledError
    └── DisplayError
```

## Usage Examples

### 1. Validation Errors

```python
from exceptions import EmptyFieldError, InvalidYearError
from books import Book

# EmptyFieldError
try:
    book = Book("", "Author", 2020)
except EmptyFieldError as e:
    print(f"Validation failed: {e}")
    # Output: Validation failed: Title cannot be empty

# InvalidYearError
try:
    book = Book("Title", "Author", 999)
except InvalidYearError as e:
    print(f"Year error: {e}")
    # Output: Year error: Invalid year: 999: Year must be between 1000 and 2100
```

### 2. Book Operations

```python
from exceptions import BookNotFoundError, DuplicateBookError
from books import BookCollection

collection = BookCollection()

# BookNotFoundError
try:
    collection.mark_as_read("Nonexistent Book")
except BookNotFoundError as e:
    print(f"Error: {e}")
    # Output: Error: Book 'Nonexistent Book' not found

# DuplicateBookError
try:
    collection.add_book("1984", "Orwell", 1949)
    collection.add_book("1984", "Orwell", 1949)  # Duplicate
except DuplicateBookError as e:
    print(f"Error: {e}")
    # Output: Error: Book '1984' by Orwell already exists in collection
```

### 3. Review Operations

```python
from exceptions import ReviewNotFoundError, InvalidRatingError

# InvalidRatingError
try:
    collection.add_review("Book", "User", "Comment", 6)  # Rating > 5
except InvalidRatingError as e:
    print(f"Error: {e}")
    # Output: Error: Invalid rating: 6: Rating must be between 1 and 5

# ReviewNotFoundError
try:
    collection.remove_review("Book", "User", "NonexistentComment")
except ReviewNotFoundError as e:
    print(f"Error: {e}")
    # Output: Error: Review by 'User' not found for book 'Book'
```

### 4. Storage Operations

```python
from exceptions import SaveError

# SaveError (automatically raised by BookCollection)
try:
    collection.add_book("Title", "Author", 2020)
except SaveError as e:
    print(f"Storage error: {e}")
    # Output: Storage error: Failed to save to 'data.json': [reason]
```

### 5. User Interface

```python
from exceptions import UserCancelledError, MaxRetriesExceededError
from utils import get_book_details

# UserCancelledError (user presses Ctrl+C)
try:
    title, author, year = get_book_details()
except UserCancelledError:
    print("Operation cancelled by user")

# MaxRetriesExceededError
try:
    title, author, year = get_book_details()
except MaxRetriesExceededError as e:
    print(f"Too many invalid attempts: {e}")
    # Output: Too many invalid attempts: Failed to get valid input after 3 attempts
```

## Exception Properties

All custom exceptions have these properties:

- **message**: Main error message
- **details**: Optional additional details (if provided)

Some exceptions have specific properties:

```python
try:
    book = Book("Title", "Author", 999)
except InvalidYearError as e:
    print(e.year)       # 999
    print(e.min_year)   # 1000
    print(e.max_year)   # 2100
```

## Best Practices

### 1. Catch Specific Exceptions First

```python
try:
    collection.add_book(title, author, year)
except DuplicateBookError as e:
    # Handle duplicate specifically
    print(f"Book already exists: {e}")
except EmptyFieldError as e:
    # Handle empty field
    print(f"Invalid input: {e}")
except BookAppException as e:
    # Catch any other book app error
    print(f"Unexpected error: {e}")
```

### 2. Use Base Exceptions for General Error Handling

```python
try:
    # Multiple operations
    collection.add_book(...)
    collection.add_review(...)
except BookOperationError as e:
    # Handles BookNotFoundError, DuplicateBookError, etc.
    print(f"Book operation failed: {e}")
except BookAppException as e:
    # Handles all custom exceptions
    print(f"Application error: {e}")
```

### 3. Let Exceptions Propagate When Appropriate

```python
def add_book_to_collection(title, author, year):
    """Add a book. Let exceptions propagate to caller."""
    # Don't catch exceptions here - let caller handle them
    return collection.add_book(title, author, year)
```

### 4. Log Errors Before Re-raising

```python
import logging

try:
    collection.save_books()
except SaveError as e:
    logging.error(f"Failed to save: {e}")
    raise  # Re-raise for caller to handle
```

## Migration from Old Code

### Before (inconsistent error handling):
```python
def add_book(title, author, year):
    if not title:
        return "Title cannot be empty"  # String return
    try:
        # ...
        return book  # Object return
    except Exception as e:
        return f"Error: {e}"  # String return
```

### After (consistent exception handling):
```python
def add_book(title, author, year):
    if not title:
        raise EmptyFieldError("Title")  # Always raise exceptions
    # ...
    return book  # Always return object on success
```

## Benefits

1. **Type Safety**: Functions have predictable return types
2. **Consistency**: All errors handled the same way
3. **Specificity**: Catch and handle specific error types
4. **Clarity**: Exception names clearly indicate what went wrong
5. **Debugging**: Stack traces show exactly where errors occurred
6. **Documentation**: Exceptions document what can go wrong
