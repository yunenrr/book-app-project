"""
Pruebas extra para books.py: escenarios concurrentes y errores de guardado

Cubre:
- Agregar libros duplicados (mismo título y autor)
- Eliminar por coincidencia parcial del título (debe fallar)
- Encontrar libros cuando la colección está vacía
- Errores de permisos de archivo durante la guardada (SaveError)
- Acceso concurrente (lecturas mientras se escribe) sin lanzar excepciones
"""

import sys
import os
import time
import threading
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import books
from books import BookCollection
from exceptions import (
    DuplicateBookError,
    BookNotFoundError,
    SaveError
)
import storage


@pytest.fixture(autouse=True)
def use_temp_data_file(tmp_path, monkeypatch):
    """Usar archivo temporal para cada prueba para evitar colisiones."""
    temp_file = tmp_path / "data.json"
    temp_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(temp_file))


def test_add_duplicate_book_same_title_author():
    """Agregar dos veces el mismo título y autor debe lanzar DuplicateBookError."""
    collection = BookCollection()
    collection.add_book("Duplicate Title", "Same Author", 2000)

    with pytest.raises(DuplicateBookError):
        collection.add_book("Duplicate Title", "Same Author", 2000)


def test_remove_book_partial_title_no_match():
    """Intentar eliminar usando coincidencia parcial de título debe fallar con BookNotFoundError."""
    collection = BookCollection()
    collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)

    # Partial title - not exact match, expect BookNotFoundError
    with pytest.raises(BookNotFoundError):
        collection.remove_book("Hobb")

    # Ensure original book still exists
    assert collection.find_book_by_title("The Hobbit") is not None


def test_find_book_when_collection_empty():
    """Buscar en colección vacía debe devolver None / listas vacías sin errores."""
    collection = BookCollection()
    assert collection.find_book_by_title("Any Title") is None
    assert collection.find_by_author("Any Author") == []
    assert collection.list_books() == []


def test_save_permission_error_raises_saveerror(monkeypatch):
    """Simular error de permisos durante save_books y esperar SaveError."""
    # Make BookStorage.save_books raise PermissionError
    original_save = storage.BookStorage.save_books

    def raise_permission(self, books_list):
        raise PermissionError("Permission denied")

    monkeypatch.setattr(storage.BookStorage, "save_books", raise_permission)

    try:
        collection = BookCollection()
        # add_book calls save_books internally, should raise SaveError
        with pytest.raises(SaveError):
            collection.add_book("Perm Test", "Author", 2020)
    finally:
        # Restore original to avoid affecting other tests
        monkeypatch.setattr(storage.BookStorage, "save_books", original_save)


def test_concurrent_access_reads_during_save(monkeypatch, tmp_path):
    """Verifica que lecturas concurrentes no lancen excepciones mientras se realizan guardados.

    Este test simula un guardado lento inyectando una sleep en save_books y ejecutando varias
    lecturas (list_books) en hilos concurrentes. Verifica que no ocurra ninguna excepción
    en los hilos y que las operaciones finalicen.
    """
    # Use a real storage but patch its save_books to sleep a bit to simulate long IO
    temp_file = tmp_path / "concurrent.json"
    temp_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(temp_file))

    original_save = storage.BookStorage.save_books

    def slow_save(self, books_list):
        # small sleep to increase chance of concurrent access
        time.sleep(0.05)
        return original_save(self, books_list)

    monkeypatch.setattr(storage.BookStorage, "save_books", slow_save)

    collection = BookCollection()
    # Pre-populate some books
    for i in range(3):
        collection.add_book(f"Initial {i}", f"Author {i}", 2000 + i)

    exceptions = []

    def reader_task():
        try:
            # Perform multiple reads
            for _ in range(20):
                books_list = collection.list_books()
                # simple assertion inside thread to exercise code paths
                assert isinstance(books_list, list)
                time.sleep(0.01)
        except Exception as e:
            exceptions.append(e)

    # Start reader threads
    readers = [threading.Thread(target=reader_task) for _ in range(5)]
    for t in readers:
        t.start()

    # While readers run, perform multiple writes
    try:
        for j in range(5):
            collection.add_book(f"Concurrent {j}", f"Author C{j}", 2010 + j)
            time.sleep(0.02)
    finally:
        for t in readers:
            t.join()

    # Restore save
    monkeypatch.setattr(storage.BookStorage, "save_books", original_save)

    # No exceptions should have occurred in reader threads
    assert exceptions == []

    # Verify that all concurrent books were added
    for j in range(5):
        assert collection.find_book_by_title(f"Concurrent {j}") is not None
