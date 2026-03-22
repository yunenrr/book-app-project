import sys
from typing import Dict, List, Any
from books import BookCollection, Book


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
    def show_books(books: List[Book]) -> None:
        """Display books in a user-friendly format."""
        if not books:
            print("No books found.")
            return

        print("\nYour Book Collection:\n")

        for index, book in enumerate(books, start=1):
            status = "✓" if book.read else " "
            print(f"{index}. [{status}] {book.title} by {book.author} ({book.year})")

        print()

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
        self.ui.show_books(books)

    @property
    def description(self) -> str:
        return "Show all books"


class AddCommand(Command):
    """Add a new book to the collection."""

    def execute(self) -> None:
        self.ui.print_section("Add a New Book")

        title = input("Title: ").strip()
        author = input("Author: ").strip()
        year_str = input("Year (optional): ").strip()

        if not title:
            self.ui.print_error("Title cannot be empty.")
            return

        if not author:
            self.ui.print_error("Author cannot be empty.")
            return

        try:
            year = int(year_str) if year_str else 0
            if year < 0:
                self.ui.print_error("Year must be a positive number.")
                return
            self.collection.add_book(title, author, year)
            self.ui.print_success(f'"{title}" by {author} added to your collection.')
        except ValueError:
            self.ui.print_error("Year must be a valid number.")

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

        if self.collection.remove_book(title):
            self.ui.print_success(f'"{title}" has been removed from your collection.')
        else:
            self.ui.print_error(f'Book titled "{title}" not found.')

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

        print(f"Books by {author}:\n")
        self.ui.show_books(books)

    @property
    def description(self) -> str:
        return "Find books by author"


class MarkReadCommand(Command):
    """Mark a book as read."""

    def execute(self) -> None:
        self.ui.print_section("Mark Book as Read")

        title = input("Enter the title of the book to mark as read: ").strip()

        if not title:
            self.ui.print_error("Title cannot be empty.")
            return

        if self.collection.mark_as_read(title):
            self.ui.print_success(f'"{title}" has been marked as read.')
        else:
            self.ui.print_error(f'Book titled "{title}" not found.')

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
