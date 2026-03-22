from typing import Tuple, List, Callable
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

CURRENT_YEAR: int = datetime.now().year
MIN_YEAR: int = 1000
VALID_CHOICES: set[str] = {"1", "2", "3", "4", "5"}
MAX_RETRIES: int = 3
MAX_TEXT_LENGTH: int = 200


def _get_validated_input(
    prompt: str,
    validator: Callable[[str], bool],
    error_message: str
) -> str:
    """Generic input validation helper to reduce code duplication.
    
    Args:
        prompt: Input prompt text
        validator: Function that returns True if input is valid
        error_message: Message to display on invalid input
        
    Returns:
        str: Valid user input
        
    Raises:
        ValueError: After max retries without valid input
    """
    for _ in range(MAX_RETRIES):
        try:
            user_input: str = input(prompt).strip()
            if validator(user_input):
                return user_input
            print(error_message)
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            raise
        except Exception as e:
            logger.error(f"Input error: {e}")
    
    raise ValueError(f"Failed to get valid input after {MAX_RETRIES} attempts.")


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
        lambda x: x in VALID_CHOICES,
        "Invalid choice. Please enter a number between 1 and 5."
    )


def get_book_details() -> Tuple[str, str, int]:
    """Collect and validate book information from user input.
    
    Returns:
        Tuple[str, str, int]: A tuple containing (title, author, year).
    """
    title: str = _get_validated_input(
        "Enter book title: ",
        lambda x: 0 < len(x) <= MAX_TEXT_LENGTH,
        f"Title must be between 1 and {MAX_TEXT_LENGTH} characters."
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


def print_books(books: List) -> None:
    """Display all books in the collection with error handling.
    
    Args:
        books: List of book objects to display.
    """
    try:
        if not books:
            print("No books in your collection.")
            return

        if not isinstance(books, list):
            raise TypeError(f"Expected list, got {type(books).__name__}")

        print("\nYour Books:")
        for index, book in enumerate(books, start=1):
            try:
                title: str = getattr(book, 'title', 'Unknown Title')
                author: str = getattr(book, 'author', 'Unknown Author')
                year: str = str(getattr(book, 'year', '?'))
                read: bool = bool(getattr(book, 'read', False))
                
                status: str = "✅ Read" if read else "📖 Unread"
                print(f"{index}. {title} by {author} ({year}) - {status}")
            except Exception as e:
                logger.error(f"Error displaying book {index}: {e}")
    except TypeError as te:
        logger.error(f"Type error: {te}")
    except Exception as e:
        logger.error(f"Error displaying books: {e}")
