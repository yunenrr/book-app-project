from typing import Tuple, List, Callable, Any, Dict
from dataclasses import dataclass
from datetime import datetime
from exceptions import (
    ValidationError,
    MaxRetriesExceededError,
    UserCancelledError,
    DisplayError,
    InputTooLongError
)
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

CURRENT_YEAR: int = datetime.now().year
MIN_YEAR: int = 1000
VALID_CHOICES: set[str] = {"1", "2", "3", "4", "5"}
MAX_RETRIES: int = 3
MAX_TEXT_LENGTH: int = 200


@dataclass
class BookDisplayData:
    """Data class for book display information."""
    index: int
    title: str
    author: str
    year: int
    read: bool
    
    def format_status(self) -> str:
        """Get formatted status symbol."""
        return "✓" if self.read else " "
    
    def format_status_text(self) -> str:
        """Get formatted status text."""
        return "✅ Read" if self.read else "📖 Unread"


# ====================
# Data Processing Functions (Pure logic, no I/O)
# ====================

def validate_input(user_input: str, validator: Callable[[str], bool]) -> bool:
    """Validate user input using provided validator function.
    
    Args:
        user_input: The input string to validate
        validator: Function that returns True if input is valid
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        return validator(user_input)
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return False


def extract_book_data(book: Any, index: int) -> BookDisplayData:
    """Extract display data from a book object.
    
    Args:
        book: Book object to extract data from
        index: Position index for display
        
    Returns:
        BookDisplayData: Structured book display information
    """
    return BookDisplayData(
        index=index,
        title=getattr(book, 'title', 'Unknown Title'),
        author=getattr(book, 'author', 'Unknown Author'),
        year=getattr(book, 'year', 0),
        read=bool(getattr(book, 'read', False))
    )


def prepare_books_for_display(books: List[Any]) -> List[BookDisplayData]:
    """Convert book objects to display data.
    
    Args:
        books: List of book objects
        
    Returns:
        List[BookDisplayData]: List of structured display data
    """
    display_data = []
    for index, book in enumerate(books, start=1):
        try:
            display_data.append(extract_book_data(book, index))
        except Exception as e:
            logger.error(f"Error processing book {index}: {e}")
    return display_data


# ====================
# Input/Output Functions (UI interactions)
# ====================

def _get_validated_input(
    prompt: str,
    validator: Callable[[str], bool],
    error_message: str
) -> str:
    """Get and validate user input with retries.
    
    Args:
        prompt: Input prompt text
        validator: Function that returns True if input is valid
        error_message: Message to display on invalid input
        
    Returns:
        str: Valid user input
        
    Raises:
        MaxRetriesExceededError: After max retries without valid input
        UserCancelledError: If user cancels with Ctrl+C
    """
    for _ in range(MAX_RETRIES):
        try:
            user_input: str = input(prompt).strip()
            if validate_input(user_input, validator):
                return user_input
            print(error_message)
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            raise UserCancelledError()
        except Exception as e:
            logger.error(f"Input error: {e}")
    
    raise MaxRetriesExceededError(MAX_RETRIES)


def print_menu() -> None:
    """Display the main menu options."""
    print("\n📚 Book Collection App")
    print("1. Add a book")
    print("2. List books")
    print("3. Mark book as read")
    print("4. Remove a book")
    print("5. Exit")


def get_user_choice() -> str:
    """Get and validate user menu choice.
    
    Returns:
        str: Valid user option (1-5).
    """
    return _get_validated_input(
        "Choose an option (1-5): ",
        lambda x: x.isdigit() and x in VALID_CHOICES,
        "Invalid choice. Please enter a number between 1 and 5."
    )


def get_book_details() -> Tuple[str, str, int]:
    """
    Solicita y valida la información de un libro desde la entrada del usuario.

    No recibe parámetros.

    Returns:
        tuple: Una tupla (title, author, year) donde:
            title (str): Título del libro, cadena no vacía y longitud máxima permitida.
            author (str): Autor del libro, cadena no vacía y longitud máxima permitida.
            year (int): Año de publicación, valor numérico entre MIN_YEAR y CURRENT_YEAR.
    
    Raises:
        InputTooLongError: If input exceeds maximum length
        MaxRetriesExceededError: If max retries exceeded
        UserCancelledError: If user cancels operation
    """
    def validate_length(text: str, max_len: int) -> bool:
        return isinstance(text, str) and 0 < len(text.strip()) <= max_len
    
    title: str = _get_validated_input(
        "Enter book title: ",
        lambda x: validate_length(x, MAX_TEXT_LENGTH),
        f"Title must be a non-empty string between 1 and {MAX_TEXT_LENGTH} characters."
    )
    
    author: str = _get_validated_input(
        "Enter author: ",
        lambda x: 0 < len(x) <= MAX_TEXT_LENGTH,
        f"Author must be between 1 and {MAX_TEXT_LENGTH} characters."
    )
    
    year: int = int(_get_validated_input(
        f"Enter publication year ({MIN_YEAR}-{CURRENT_YEAR}): ",
        lambda x: x.isdigit() and MIN_YEAR <= int(x) <= CURRENT_YEAR,
        f"Year must be a number between {MIN_YEAR} and {CURRENT_YEAR}."
    ))
    
    return title, author, year


def render_book_line(book_data: BookDisplayData, style: str = "cli") -> str:
    """Render a single book line for display.
    
    Args:
        book_data: Book display data
        style: Display style ("cli" or "detailed")
        
    Returns:
        str: Formatted book line
    """
    if style == "cli":
        status = book_data.format_status()
        return f"{book_data.index}. [{status}] {book_data.title} by {book_data.author} ({book_data.year})"
    else:  # detailed
        status = book_data.format_status_text()
        return f"{book_data.index}. {book_data.title} by {book_data.author} ({book_data.year}) - {status}"


def print_books(books: List[Any]) -> None:
    """Display all books in the collection with error handling.
    
    Args:
        books: List of book objects to display.
    
    Raises:
        DisplayError: If displaying books fails
    """
    try:
        if not books:
            print("No books in your collection.")
            return

        if not isinstance(books, list):
            raise DisplayError(f"Expected list, got {type(books).__name__}")

        print("\nYour Books:")
        
        books_data = prepare_books_for_display(books)
        for book_data in books_data:
            print(render_book_line(book_data, style="detailed"))
            
    except DisplayError:
        raise
    except Exception as e:
        logger.error(f"Error displaying books: {e}")
        raise DisplayError(str(e))


def show_books(books: List[Any], header: str = "Your Book Collection") -> None:
    """Display books in a user-friendly format for CLI.
    
    Args:
        books: List of book objects to display.
        header: Optional header text to display before the list.
    """
    if not books:
        print("No books found.")
        return

    print(f"\n{header}:\n")

    books_data = prepare_books_for_display(books)
    for book_data in books_data:
        print(render_book_line(book_data, style="cli"))

    print()
