"""
Pruebas para find_by_author con casos límite de nombres de autor

Cubre:
- Autor con guiones (Jean-Paul Sartre)
- Autor con múltiples nombres de pila (Mary Ann Evans)
- Autor vacío (cadena vacía)
- Autor con caracteres acentuados (Gabriel García Márquez)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from books import BookCollection
import books


@pytest.fixture(autouse=True)
def use_temp_data_file(tmp_path, monkeypatch):
    temp_file = tmp_path / "data.json"
    temp_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(temp_file))


def test_find_by_author_hyphen():
    """Encontrar autor con guion como 'Jean-Paul Sartre'."""
    coll = BookCollection()
    coll.add_book("Being and Nothingness", "Jean-Paul Sartre", 1943)
    coll.add_book("Nausea", "Jean-Paul Sartre", 1938)

    results = coll.find_by_author("Jean-Paul Sartre")
    assert len(results) == 2
    titles = {b.title for b in results}
    assert "Being and Nothingness" in titles
    assert "Nausea" in titles

    # Case-insensitive
    results_lower = coll.find_by_author("jean-paul sartre")
    assert len(results_lower) == 2


def test_find_by_author_multiple_given_names():
    """Encontrar autor con múltiples nombres de pila ('Mary Ann Evans')."""
    coll = BookCollection()
    coll.add_book("Middlemarch", "Mary Ann Evans", 1871)

    res_exact = coll.find_by_author("Mary Ann Evans")
    assert len(res_exact) == 1
    assert res_exact[0].title == "Middlemarch"

    # search with different casing
    res_case = coll.find_by_author("mary ann evans")
    assert len(res_case) == 1


def test_find_by_author_empty_string():
    """Buscar con cadena vacía debe retornar lista vacía (no lanzar)."""
    coll = BookCollection()
    # Empty collection case
    assert coll.find_by_author("") == []

    # Non-empty collection should also return empty list for empty author
    coll.add_book("Some Book", "Some Author", 2000)
    assert coll.find_by_author("") == []


def test_find_by_author_accented_characters():
    """Encontrar autor con caracteres acentuados ('Gabriel García Márquez')."""
    coll = BookCollection()
    coll.add_book("Cien años de soledad", "Gabriel García Márquez", 1967)
    coll.add_book("El coronel no tiene quien le escriba", "Gabriel García Márquez", 1961)

    results = coll.find_by_author("Gabriel García Márquez")
    assert len(results) == 2
    titles = {b.title for b in results}
    assert "Cien años de soledad" in titles
    assert "El coronel no tiene quien le escriba" in titles

    # lower-case input should still match
    results_lower = coll.find_by_author("gabriel garcía márquez")
    assert len(results_lower) == 2
