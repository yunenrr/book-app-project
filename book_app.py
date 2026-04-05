import sys
from typing import Dict, List, Any
from books import BookCollection, Book
from utils import show_books, get_book_details
from exceptions import (
    BookAppException,
    BookNotFoundError,
    DuplicateBookError,
    EmptyFieldError,
    InvalidYearError,
    SaveError,
    InputTooLongError,
    MaxRetriesExceededError,
    UserCancelledError
)


class UI:
    """Handles all user interface formatting and output."""

    @staticmethod
    def print_section(title: str) -> None:
        """Print a formatted section header."""
        print(f"\n{title}\n")

    @staticmethod
    def print_success(message: str) -> None:
        """Print a success message."""
        print(f"\n✓ {message}\n")

    @staticmethod
    def print_error(message: str) -> None:
        """Print an error message."""
        print(f"\n✗ Error: {message}\n")



    @staticmethod
    def show_help(commands_info: Dict[str, Dict[str, str]]) -> None:
        """Display help message with command information."""
        print("\nBook Collection Manager\n")
        print("Commands:")
        for cmd, info in commands_info.items():
            print(f"  {cmd:<12} - {info['description']}")
        print()


class Command:
    """Base class for all commands."""

    def __init__(self, collection: BookCollection) -> None:
        self.collection = collection
        self.ui = UI

    def execute(self) -> None:
        """Execute the command. Override in subclasses."""
        raise NotImplementedError

    @property
    def description(self) -> str:
        """Command description for help text."""
        raise NotImplementedError


class ListCommand(Command):
    """List all books in the collection."""

    def execute(self) -> None:
        books = self.collection.list_books()
        show_books(books)

    @property
    def description(self) -> str:
        return "Show all books"


class AddCommand(Command):
    """Add a new book to the collection."""

    def execute(self) -> None:
        self.ui.print_section("Add a New Book")

        try:
            title, author, year = get_book_details()
            # get_book_details validates title, author length and year range
            self.collection.add_book(title, author, year)
            self.ui.print_success(f'"{title}" by {author} added to your collection.')
        except (InputTooLongError, MaxRetriesExceededError, UserCancelledError) as e:
            # Input-related errors: show message and abort
            self.ui.print_error(str(e))
            return
        except DuplicateBookError as e:
            self.ui.print_error(str(e))
        except (EmptyFieldError, InvalidYearError, SaveError) as e:
            self.ui.print_error(str(e))
        except BookAppException as e:
            self.ui.print_error(f"Failed to add book: {e}")

    @property
    def description(self) -> str:
        return "Add a new book"


class RemoveCommand(Command):
    """Remove a book from the collection."""

    def execute(self) -> None:
        self.ui.print_section("Remove a Book")

        title = input("Enter the title of the book to remove: ").strip()

        if not title:
            self.ui.print_error("Title cannot be empty.")
            return

        try:
            self.collection.remove_book(title)
            self.ui.print_success(f'"{title}" has been removed from your collection.')
        except BookNotFoundError as e:
            self.ui.print_error(str(e))
        except BookAppException as e:
            self.ui.print_error(f"Failed to remove book: {e}")

    @property
    def description(self) -> str:
        return "Remove a book by title"


class FindCommand(Command):
    """Find books by author."""

    def execute(self) -> None:
        self.ui.print_section("Find Books by Author")

        author = input("Author name: ").strip()

        if not author:
            self.ui.print_error("Author name cannot be empty.")
            return

        books = self.collection.find_by_author(author)

        if not books:
            print(f"No books found by {author}.")
            return

        show_books(books, header=f"Books by {author}")

    @property
    def description(self) -> str:
        return "Find books by author"


class SearchYearCommand(Command):
    """Search books by year range."""

    def execute(self) -> None:
        self.ui.print_section("Search Books by Year Range")

        # Import constants locally to avoid changing module-level imports
        from utils import CURRENT_YEAR, MIN_YEAR

        min_input = input(f"Enter minimum year ({MIN_YEAR}-{CURRENT_YEAR}) or leave blank: ").strip()
        max_input = input(f"Enter maximum year ({MIN_YEAR}-{CURRENT_YEAR}) or leave blank: ").strip()

        if not min_input and not max_input:
            self.ui.print_error("At least one of minimum or maximum year must be provided.")
            return

        try:
            year_min = int(min_input) if min_input else None
            year_max = int(max_input) if max_input else None
        except ValueError:
            self.ui.print_error("Years must be valid integers.")
            return

        if year_min is not None and (year_min < MIN_YEAR or year_min > CURRENT_YEAR):
            self.ui.print_error(f"Minimum year must be between {MIN_YEAR} and {CURRENT_YEAR}.")
            return
        if year_max is not None and (year_max < MIN_YEAR or year_max > CURRENT_YEAR):
            self.ui.print_error(f"Maximum year must be between {MIN_YEAR} and {CURRENT_YEAR}.")
            return

        if year_min is not None and year_max is not None and year_min > year_max:
            self.ui.print_error("Minimum year cannot be greater than maximum year.")
            return

        books = self.collection.search(year_min=year_min, year_max=year_max)

        if not books:
            print("No books found in that year range.")
            return

        header = f"Books from {year_min if year_min is not None else 'start'} to {year_max if year_max is not None else 'now'}"
        show_books(books, header=header)


class MarkReadCommand(Command):
    """Mark a book as read."""

    def execute(self) -> None:
        self.ui.print_section("Mark Book as Read")

        title = input("Enter the title of the book to mark as read: ").strip()

        if not title:
            self.ui.print_error("Title cannot be empty.")
            return

        try:
            self.collection.mark_as_read(title)
            self.ui.print_success(f'"{title}" has been marked as read.')
        except BookNotFoundError as e:
            self.ui.print_error(str(e))
        except BookAppException as e:
            self.ui.print_error(f"Failed to mark book as read: {e}")

    @property
    def description(self) -> str:
        return "Mark a book as read"


class BookApp:
    """Main application controller."""

    def __init__(self) -> None:
        self.collection = BookCollection()
        self.ui = UI
        self.commands = self._register_commands()

    def _register_commands(self) -> Dict[str, Command]:
        """Register all available commands."""
        return {
            "list": ListCommand(self.collection),
            "add": AddCommand(self.collection),
            "remove": RemoveCommand(self.collection),
            "find": FindCommand(self.collection),
            "search-year": SearchYearCommand(self.collection),
            "mark-read": MarkReadCommand(self.collection),
        }

    def get_help_info(self) -> Dict[str, Dict[str, str]]:
        """Get command information for help text."""
        return {name: {"description": cmd.description} for name, cmd in self.commands.items()}

    def execute_command(self, command_name: str) -> None:
        """Execute a command by name."""
        command_name = command_name.lower()

        if command_name == "help":
            self.ui.show_help(self.get_help_info())
            return

        if command_name not in self.commands:
            self.ui.print_error(f'Unknown command "{command_name}".')
            self.ui.show_help(self.get_help_info())
            return

        self.commands[command_name].execute()

    def run(self, args: List[str]) -> None:
        """Run the application with given arguments."""
        if len(args) < 2:
            self.ui.show_help(self.get_help_info())
            return

        self.execute_command(args[1])




if __name__ == "__main__":
    app = BookApp()
    app.run(sys.argv)
