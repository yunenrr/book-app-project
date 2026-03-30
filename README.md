# Book Collection App

A robust Python application for managing your book collection with professional-grade code quality, comprehensive testing, and best practices implementation.

## Features

### Core Functionality
* 📚 **Full CRUD Operations** - Add, remove, list, and find books
* 🔍 **Advanced Search** - Filter by author, year range, and read status
* ⭐ **Review System** - Add and manage book reviews with ratings
* ✅ **Read Status Tracking** - Mark books as read or unread
* 💾 **Persistent Storage** - Atomic file operations with data integrity

### Code Quality Features
* ✨ **Context Managers** - Safe file operations with automatic cleanup
* 🎯 **Type Hints** - Complete type annotations throughout
* 🛡️ **Custom Exceptions** - Unified error handling system
* 📖 **Comprehensive Documentation** - Google-style docstrings
* ✅ **93 Tests** - 100% pass rate with comprehensive coverage
* 🔒 **Atomic Writes** - Data never corrupted on errors

---

## Architecture

### Core Files
* **`book_app.py`** - CLI entry point with Command pattern
* **`books.py`** - Domain models (Book, Review, BookCollection)
* **`storage.py`** - Persistence layer with context managers
* **`utils.py`** - UI utilities with data/presentation separation
* **`exceptions.py`** - Custom exception hierarchy

### Data Files
* **`data.json`** - Persistent book storage

### Test Files
* **`tests/test_books.py`** - Original test suite (15 tests)
* **`tests/test_books_comprehensive.py`** - Comprehensive tests (78 tests)

### Documentation
* **`CONTEXT_MANAGERS_GUIDE.md`** - Context manager implementation guide
* **`EXCEPTION_HANDLING_GUIDE.md`** - Exception system documentation
* **`REFACTORING_SUMMARY.md`** - Recent refactoring summary
* **`CODE_QUALITY_CHECKLIST.md`** - Code quality guidelines
* **`tests/TEST_SUITE_DOCUMENTATION.md`** - Test suite documentation

---

## Installation

```bash
# Clone or download the project
cd book-app-project

# Install dependencies (pytest for testing)
pip install pytest

# Verify installation
python -m pytest tests/ -v
```

---

## Usage

### Basic Commands

```bash
# List all books
python book_app.py list

# Add a new book (interactive)
python book_app.py add

# Find a book by title
python book_app.py find

# Remove a book
python book_app.py remove

# Mark book as read
python book_app.py read

# Search with filters
python book_app.py search

# Add a review
python book_app.py review

# Show help
python book_app.py help
```

### Example Workflow

```bash
# Add a book
$ python book_app.py add
Enter book title: Clean Code
Enter author: Robert Martin
Enter publication year: 2008
✅ Book added: Clean Code by Robert Martin (2008)

# Mark it as read
$ python book_app.py read
Enter book title: Clean Code
✅ "Clean Code" marked as read

# Add a review
$ python book_app.py review
Enter book title: Clean Code
Enter your name: Alice
Enter your comment: Essential reading for developers!
Enter rating (1-5): 5
✅ Review added to "Clean Code"

# List all books
$ python book_app.py list
Your Book Collection:

1. [✓] Clean Code by Robert Martin (2008)
   ⭐ Average rating: 5.00
```

---

## Running Tests

### Run All Tests
```bash
# Run all 93 tests
python -m pytest tests/ -v

# Run with coverage info
python -m pytest tests/ -v --tb=short

# Run specific test file
python -m pytest tests/test_books_comprehensive.py -v
```

### Test Statistics
- **Total Tests**: 93 (15 original + 78 comprehensive)
- **Pass Rate**: 100%
- **Execution Time**: ~0.5 seconds
- **Coverage**: All classes, methods, edge cases

---

## Code Quality Features

### Context Managers (Latest Addition)
Safe file operations with automatic cleanup and atomic writes:

```python
# Reading files safely
with safe_file_read("data.json") as f:
    if f is None:
        return []  # File doesn't exist
    data = json.load(f)

# Writing files atomically
with safe_file_write("data.json") as f:
    json.dump(data, f)  # Original file safe on error
```

### Custom Exceptions
Unified error handling with specific exception types:

```python
try:
    collection.add_book("", "Author", 2020)
except EmptyFieldError as e:
    print(f"Error: {e}")  # "Title cannot be empty"
```

### Type Hints
Complete type annotations for better IDE support and type checking.

### Comprehensive Documentation
Every method has Google-style docstrings with examples.

---

## Design Patterns

### Command Pattern
CLI commands use dictionary dispatch with Command classes.

### Data/Presentation Separation
Display logic separated from data processing.

### Context Manager Pattern
Safe resource management with automatic cleanup.

---

## Performance Features

### O(1) Lookups
- Title searches use hash index
- Author searches use hash index
- Fast search even with large collections

### Atomic Writes
- Data integrity guaranteed
- No partial writes on errors
- Uses temp file + atomic replace

---

## Documentation Files

| File | Description | Size |
|------|-------------|------|
| `CONTEXT_MANAGERS_GUIDE.md` | Context manager patterns | 15KB |
| `EXCEPTION_HANDLING_GUIDE.md` | Exception system | 150+ lines |
| `REFACTORING_SUMMARY.md` | Latest refactoring | 9KB |
| `CODE_QUALITY_CHECKLIST.md` | Quality standards | - |
| `tests/TEST_SUITE_DOCUMENTATION.md` | Test documentation | 11KB |

### Demo Scripts
- **`demo_context_managers.py`** - Interactive demos (4 scenarios)

Run the demo:
```bash
python demo_context_managers.py
```

---

## Project Statistics

| Metric | Value |
|--------|-------|
| **Total Tests** | 93 |
| **Test Pass Rate** | 100% |
| **Public Methods** | 14 |
| **Custom Exceptions** | 14+ |
| **Type Annotations** | Complete |
| **Documentation** | ~40KB |

---

## Recent Improvements

### ✨ Context Manager Refactoring (2026-03-30)
✅ Implemented `safe_file_write()` and `safe_file_read()` context managers  
✅ Refactored `BookStorage` to use context managers  
✅ 40% less code in critical methods  
✅ Atomic writes with error recovery  
✅ All 93 tests pass (zero breaking changes)

### ✅ Comprehensive Test Suite
✅ Created 78 new comprehensive tests  
✅ 11 test classes organized by functionality  
✅ Complete coverage of all public methods

### 🛡️ Exception Handling System
✅ Hierarchical exception system (14+ types)  
✅ Unified error handling across codebase  
✅ Clear error messages with context

### 📖 Documentation Improvements
✅ Google-style docstrings throughout  
✅ Complete parameter documentation  
✅ Usage examples in docstrings

---

## Running the App

```bash
## Running the App (Quick Reference)

```bash
python book_app.py list      # List all books
python book_app.py add       # Add a book (interactive)
python book_app.py find      # Find a book
python book_app.py remove    # Remove a book
python book_app.py read      # Mark as read
python book_app.py search    # Advanced search
python book_app.py review    # Add review
python book_app.py help      # Show help
```

---

## Development Guidelines

### Code Quality Standards
✅ Type hints on all functions  
✅ Docstrings on all public methods  
✅ Custom exceptions (no string returns)  
✅ Separation of concerns  
✅ DRY principle followed

### Before Committing
```bash
# 1. Run all tests
python -m pytest tests/ -v

# 2. Verify app works
python book_app.py list

# 3. Run demo (optional)
python demo_context_managers.py
```

---

## License

This is a sample educational project demonstrating Python best practices.

---

## Contributing

See `CODE_QUALITY_CHECKLIST.md` for code quality standards.

All contributions must:
1. Pass all 93 tests
2. Include type hints
3. Include docstrings
4. Use custom exceptions
5. Follow separation of concerns

---
