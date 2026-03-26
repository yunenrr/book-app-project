import json
import os
import tempfile
import logging
from typing import List, Type
from books import Book, Review

logger = logging.getLogger(__name__)

class BookStorage:
    def __init__(self, data_file: str = "data.json"):
        self.data_file = data_file

    def load_books(self) -> List[Book]:
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Book(**b) for b in data]
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            logger.warning(f"{self.data_file} is corrupted. Starting with empty collection.")
            return []
        except ValueError as e:
            logger.warning(f"Invalid book data in file: {e}. Starting with empty collection.")
            return []

    def save_books(self, books: List[Book]):
        try:
            dir_name = os.path.dirname(os.path.abspath(self.data_file))
            fd, temp_path = tempfile.mkstemp(dir=dir_name, suffix='.json', text=True)
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    def book_to_dict(b):
                        d = b.__dict__.copy()
                        d['reviews'] = [r.__dict__ for r in b.reviews]
                        return d
                    json.dump([book_to_dict(b) for b in books], f, indent=2, ensure_ascii=False)
                if os.path.exists(self.data_file):
                    os.replace(temp_path, self.data_file)
                else:
                    os.rename(temp_path, self.data_file)
            except:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise
        except (IOError, OSError) as e:
            raise IOError(f"Failed to save books to {self.data_file}: {e}")
