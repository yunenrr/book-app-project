import sys
from books import BookCollection


# Global collection instance
collection = BookCollection()


def _print_section(title):
    """Print a formatted section header."""
    print(f"\n{title}\n")


def _print_success(message):
    """Print a success message."""
    print(f"\n✓ {message}\n")


def _print_error(message):
    """Print an error message."""
    print(f"\n✗ Error: {message}\n")


def show_books(books):
    """Display books in a user-friendly format."""
    if not books:
        print("No books found.")
        return

    print("\nYour Book Collection:\n")

    for index, book in enumerate(books, start=1):
        status = "✓" if book.read else " "
        print(f"{index}. [{status}] {book.title} by {book.author} ({book.year})")

    print()


def handle_list():
    books = collection.list_books()
    show_books(books)


def handle_add():
    _print_section("Add a New Book")

    title = input("Title: ").strip()
    author = input("Author: ").strip()
    year_str = input("Year (optional): ").strip()

    # Validate inputs
    if not title:
        _print_error("Title cannot be empty.")
        return
    
    if not author:
        _print_error("Author cannot be empty.")
        return

    try:
        year = int(year_str) if year_str else 0
        if year < 0:
            _print_error("Year must be a positive number.")
            return
        collection.add_book(title, author, year)
        _print_success(f'"{title}" by {author} added to your collection.')
    except ValueError:
        _print_error("Year must be a valid number.")


def handle_remove():
    _print_section("Remove a Book")

    title = input("Enter the title of the book to remove: ").strip()
    
    if not title:
        _print_error("Title cannot be empty.")
        return

    if collection.remove_book(title):
        _print_success(f'"{title}" has been removed from your collection.')
    else:
        _print_error(f'Book titled "{title}" not found.')


def handle_find():
    _print_section("Find Books by Author")

    author = input("Author name: ").strip()
    
    if not author:
        _print_error("Author name cannot be empty.")
        return

    books = collection.find_by_author(author)

    if not books:
        print(f"No books found by {author}.")
        return

    print(f"Books by {author}:\n")
    show_books(books)


def handle_mark_read():
    _print_section("Mark Book as Read")

    title = input("Enter the title of the book to mark as read: ").strip()
    
    if not title:
        _print_error("Title cannot be empty.")
        return

    if collection.mark_as_read(title):
        _print_success(f'"{title}" has been marked as read.')
    else:
        _print_error(f'Book titled "{title}" not found.')


def show_help():
    print("""
Book Collection Manager

Commands:
  list        - Show all books
  add         - Add a new book
  remove      - Remove a book by title
  find        - Find books by author
  mark-read   - Mark a book as read
  help        - Show this help message
""")


def main():
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    # Command mapping for better scalability
    commands = {
        "list": handle_list,
        "add": handle_add,
        "remove": handle_remove,
        "find": handle_find,
        "mark-read": handle_mark_read,
        "help": show_help,
    }

    if command in commands:
        commands[command]()
    else:
        _print_error(f'Unknown command "{command}".')
        show_help()


if __name__ == "__main__":
    main()
