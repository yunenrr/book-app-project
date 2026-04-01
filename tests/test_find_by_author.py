from storage import BookStorage
from books import BookCollection


def test_find_by_author_full_match(tmp_path):
    storage = BookStorage(str(tmp_path / "books_full.json"))
    collection = BookCollection(storage=storage)
    collection.add_book("Book A", "John Smith", 2000)

    results = collection.find_by_author("John Smith")
    assert len(results) == 1
    assert results[0].title == "Book A"


def test_find_by_author_partial_match(tmp_path):
    storage = BookStorage(str(tmp_path / "books_partial.json"))
    collection = BookCollection(storage=storage)
    collection.add_book("Book A", "John Smith", 2000)
    collection.add_book("Book B", "Ann Smith", 2001)
    collection.add_book("Book C", "Johnson", 2002)

    results = collection.find_by_author("Smith")
    titles = {b.title for b in results}
    assert titles == {"Book A", "Book B"}


def test_find_by_author_case_insensitive(tmp_path):
    storage = BookStorage(str(tmp_path / "books_case.json"))
    collection = BookCollection(storage=storage)
    collection.add_book("Book A", "John Smith", 2000)

    results = collection.find_by_author("joHN sMiTh")
    assert len(results) == 1
    assert results[0].title == "Book A"


def test_find_by_author_not_found(tmp_path):
    storage = BookStorage(str(tmp_path / "books_none.json"))
    collection = BookCollection(storage=storage)
    collection.add_book("Book A", "John Smith", 2000)

    results = collection.find_by_author("Nonexistent")
    assert results == []
