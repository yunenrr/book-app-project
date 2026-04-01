"""
Pruebas completas para books.py
================================
Suite de pruebas exhaustivas que cubre todas las funcionalidades principales:
- Agregar libros
- Eliminar libros  
- Buscar por título
- Buscar por autor
- Marcar como leído/no leído
- Casos límite con datos vacíos

Autor: Generado con GitHub Copilot
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import datetime
import books
from books import Book, Review, BookCollection
from exceptions import (
    BookNotFoundError,
    DuplicateBookError,
    EmptyFieldError,
    InvalidYearError,
    InvalidRatingError,
    ReviewNotFoundError,
    SaveError
)


@pytest.fixture(autouse=True)
def use_temp_data_file(tmp_path, monkeypatch):
    """Usa un archivo temporal para cada prueba."""
    temp_file = tmp_path / "data.json"
    temp_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(temp_file))


@pytest.fixture
def collection():
    """Fixture que proporciona una colección vacía."""
    return BookCollection()


@pytest.fixture
def collection_with_books():
    """Fixture que proporciona una colección con libros de ejemplo."""
    coll = BookCollection()
    coll.add_book("1984", "George Orwell", 1949)
    coll.add_book("Dune", "Frank Herbert", 1965)
    coll.add_book("Foundation", "Isaac Asimov", 1951)
    coll.add_book("Neuromancer", "William Gibson", 1984)
    coll.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
    return coll


# ====================
# PRUEBAS: AGREGAR LIBROS
# ====================

class TestAddBook:
    """Pruebas para agregar libros a la colección."""
    
    def test_agregar_libro_basico(self, collection):
        """Debe agregar un libro con datos válidos."""
        resultado = collection.add_book("Fahrenheit 451", "Ray Bradbury", 1953)
        
        assert isinstance(resultado, Book)
        assert resultado.title == "Fahrenheit 451"
        assert resultado.author == "Ray Bradbury"
        assert resultado.year == 1953
        assert resultado.read is False
        assert len(collection.books) == 1
    
    def test_agregar_varios_libros(self, collection):
        """Debe poder agregar múltiples libros."""
        collection.add_book("Book 1", "Author 1", 2000)
        collection.add_book("Book 2", "Author 2", 2001)
        collection.add_book("Book 3", "Author 3", 2002)
        
        assert len(collection.books) == 3
    
    def test_agregar_libro_titulo_vacio(self, collection):
        """No debe permitir agregar libro con título vacío."""
        with pytest.raises(EmptyFieldError) as exc:
            collection.add_book("", "Author", 2020)
        assert "Title" in str(exc.value)
    
    def test_agregar_libro_titulo_espacios(self, collection):
        """No debe permitir agregar libro con título solo espacios."""
        with pytest.raises(EmptyFieldError):
            collection.add_book("   ", "Author", 2020)
    
    def test_agregar_libro_autor_vacio(self, collection):
        """No debe permitir agregar libro con autor vacío."""
        with pytest.raises(EmptyFieldError) as exc:
            collection.add_book("Title", "", 2020)
        assert "Author" in str(exc.value)
    
    def test_agregar_libro_autor_espacios(self, collection):
        """No debe permitir agregar libro con autor solo espacios."""
        with pytest.raises(EmptyFieldError):
            collection.add_book("Title", "   ", 2020)
    
    def test_agregar_libro_anio_invalido_bajo(self, collection):
        """No debe permitir año menor a 1000."""
        with pytest.raises(InvalidYearError):
            collection.add_book("Ancient Text", "Unknown", 999)
    
    def test_agregar_libro_anio_invalido_alto(self, collection):
        """No debe permitir año mayor a 2100."""
        with pytest.raises(InvalidYearError):
            collection.add_book("Future Book", "Unknown", 2101)
    
    def test_agregar_libro_anio_limite_inferior(self, collection):
        """Debe aceptar año 1000 (límite inferior)."""
        libro = collection.add_book("Old Book", "Old Author", 1000)
        assert libro.year == 1000
    
    def test_agregar_libro_anio_limite_superior(self, collection):
        """Debe aceptar año 2100 (límite superior)."""
        libro = collection.add_book("Future Book", "Future Author", 2100)
        assert libro.year == 2100
    
    def test_agregar_libro_duplicado_mismo_caso(self, collection):
        """No debe permitir agregar libro duplicado (mismo caso)."""
        collection.add_book("Duplicate", "Author", 2020)
        
        with pytest.raises(DuplicateBookError) as exc:
            collection.add_book("Duplicate", "Author", 2020)
        assert "already exists" in str(exc.value)
    
    def test_agregar_libro_duplicado_diferente_caso(self, collection):
        """No debe permitir agregar libro duplicado (diferente caso)."""
        collection.add_book("Test Book", "Test Author", 2020)
        
        with pytest.raises(DuplicateBookError):
            collection.add_book("TEST BOOK", "test author", 2020)
    
    def test_agregar_libro_mismo_titulo_diferente_autor(self, collection):
        """Debe permitir mismo título con diferente autor."""
        libro1 = collection.add_book("Common Title", "Author A", 2020)
        libro2 = collection.add_book("Common Title", "Author B", 2021)
        
        assert len(collection.books) == 2
        assert libro1.author != libro2.author
    
    def test_agregar_libro_persiste(self, collection, tmp_path, monkeypatch):
        """El libro agregado debe persistir en el almacenamiento."""
        collection.add_book("Persistent Book", "Author", 2020)
        
        # Crear nueva colección para verificar persistencia
        nueva_collection = BookCollection()
        assert len(nueva_collection.books) == 1
        assert nueva_collection.books[0].title == "Persistent Book"


# ====================
# PRUEBAS: ELIMINAR LIBROS
# ====================

class TestRemoveBook:
    """Pruebas para eliminar libros de la colección."""
    
    def test_eliminar_libro_existente(self, collection_with_books):
        """Debe eliminar un libro existente."""
        cantidad_inicial = len(collection_with_books.books)
        collection_with_books.remove_book("1984")
        
        assert len(collection_with_books.books) == cantidad_inicial - 1
        assert collection_with_books.find_book_by_title("1984") is None
    
    def test_eliminar_libro_no_existente(self, collection):
        """Debe lanzar error al eliminar libro inexistente."""
        with pytest.raises(BookNotFoundError) as exc:
            collection.remove_book("Nonexistent Book")
        assert "not found" in str(exc.value)
    
    def test_eliminar_libro_case_insensitive(self, collection_with_books):
        """Debe eliminar libro independiente de mayúsculas/minúsculas."""
        collection_with_books.remove_book("dune")  # minúsculas
        assert collection_with_books.find_book_by_title("Dune") is None
    
    def test_eliminar_libro_actualiza_indice_titulo(self, collection_with_books):
        """Debe actualizar el índice de títulos al eliminar."""
        collection_with_books.remove_book("1984")
        assert "1984".lower() not in collection_with_books._title_index
    
    def test_eliminar_libro_actualiza_indice_autor(self, collection_with_books):
        """Debe actualizar el índice de autores al eliminar."""
        # George Orwell solo tiene 1 libro
        collection_with_books.remove_book("1984")
        assert "george orwell" not in collection_with_books._author_index
    
    def test_eliminar_uno_de_varios_del_mismo_autor(self, collection):
        """Debe mantener otros libros del mismo autor al eliminar uno."""
        collection.add_book("Book 1", "Same Author", 2000)
        collection.add_book("Book 2", "Same Author", 2001)
        
        collection.remove_book("Book 1")
        
        libros_autor = collection.find_by_author("Same Author")
        assert len(libros_autor) == 1
        assert libros_autor[0].title == "Book 2"
    
    def test_eliminar_libro_persiste(self, collection_with_books):
        """La eliminación debe persistir en el almacenamiento."""
        collection_with_books.remove_book("1984")
        
        # Crear nueva colección para verificar persistencia
        nueva_collection = BookCollection()
        assert collection_with_books.find_book_by_title("1984") is None
    
    def test_eliminar_todos_los_libros(self, collection_with_books):
        """Debe poder eliminar todos los libros."""
        titulos = [libro.title for libro in collection_with_books.books]
        
        for titulo in titulos:
            collection_with_books.remove_book(titulo)
        
        assert len(collection_with_books.books) == 0
        assert len(collection_with_books._title_index) == 0
        assert len(collection_with_books._author_index) == 0


# ====================
# PRUEBAS: BUSCAR POR TÍTULO
# ====================

class TestFindByTitle:
    """Pruebas para buscar libros por título."""
    
    def test_buscar_titulo_existente(self, collection_with_books):
        """Debe encontrar un libro existente por título exacto."""
        libro = collection_with_books.find_book_by_title("1984")
        
        assert libro is not None
        assert libro.title == "1984"
        assert libro.author == "George Orwell"
        assert libro.year == 1949
    
    def test_buscar_titulo_no_existente(self, collection_with_books):
        """Debe retornar None para título inexistente."""
        libro = collection_with_books.find_book_by_title("Nonexistent Book")
        assert libro is None
    
    def test_buscar_titulo_case_insensitive(self, collection_with_books):
        """Búsqueda debe ser insensible a mayúsculas/minúsculas."""
        libro1 = collection_with_books.find_book_by_title("dune")
        libro2 = collection_with_books.find_book_by_title("DUNE")
        libro3 = collection_with_books.find_book_by_title("Dune")
        
        assert libro1 is not None
        assert libro1 == libro2 == libro3
    
    def test_buscar_titulo_coleccion_vacia(self, collection):
        """Debe retornar None en colección vacía."""
        libro = collection.find_book_by_title("Any Book")
        assert libro is None
    
    def test_buscar_titulo_vacio(self, collection_with_books):
        """Debe retornar None para título vacío."""
        libro = collection_with_books.find_book_by_title("")
        assert libro is None
    
    def test_buscar_titulo_espacios(self, collection_with_books):
        """Debe retornar None para título solo espacios."""
        libro = collection_with_books.find_book_by_title("   ")
        assert libro is None


# ====================
# PRUEBAS: BUSCAR POR AUTOR
# ====================

class TestFindByAuthor:
    """Pruebas para buscar libros por autor."""
    
    def test_buscar_autor_un_libro(self, collection_with_books):
        """Debe encontrar libro de autor con un solo libro."""
        libros = collection_with_books.find_by_author("George Orwell")
        
        assert len(libros) == 1
        assert libros[0].title == "1984"
        assert libros[0].author == "George Orwell"
    
    def test_buscar_autor_varios_libros(self, collection):
        """Debe encontrar todos los libros de un autor."""
        collection.add_book("Book 1", "Prolific Author", 2000)
        collection.add_book("Book 2", "Prolific Author", 2001)
        collection.add_book("Book 3", "Prolific Author", 2002)
        collection.add_book("Other Book", "Other Author", 2003)
        
        libros = collection.find_by_author("Prolific Author")
        
        assert len(libros) == 3
        titulos = [libro.title for libro in libros]
        assert "Book 1" in titulos
        assert "Book 2" in titulos
        assert "Book 3" in titulos
        assert "Other Book" not in titulos
    
    def test_buscar_autor_no_existente(self, collection_with_books):
        """Debe retornar lista vacía para autor inexistente."""
        libros = collection_with_books.find_by_author("Unknown Author")
        assert libros == []
    
    def test_buscar_autor_case_insensitive(self, collection_with_books):
        """Búsqueda debe ser insensible a mayúsculas/minúsculas."""
        libros1 = collection_with_books.find_by_author("george orwell")
        libros2 = collection_with_books.find_by_author("GEORGE ORWELL")
        libros3 = collection_with_books.find_by_author("George Orwell")
        
        assert len(libros1) == len(libros2) == len(libros3) == 1
        assert libros1[0] == libros2[0] == libros3[0]
    
    def test_buscar_autor_coleccion_vacia(self, collection):
        """Debe retornar lista vacía en colección vacía."""
        libros = collection.find_by_author("Any Author")
        assert libros == []
    
    def test_buscar_autor_vacio(self, collection_with_books):
        """Debe retornar lista vacía para autor vacío."""
        libros = collection_with_books.find_by_author("")
        assert libros == []
    
    def test_buscar_autor_retorna_copia(self, collection_with_books):
        """Debe retornar una copia de la lista, no la original."""
        libros1 = collection_with_books.find_by_author("George Orwell")
        libros2 = collection_with_books.find_by_author("George Orwell")
        
        # Modificar una lista no debe afectar la otra
        assert libros1 is not libros2
        assert len(libros1) == len(libros2)


# ====================
# PRUEBAS: MARCAR COMO LEÍDO
# ====================

class TestMarkAsRead:
    """Pruebas para marcar libros como leídos."""
    
    def test_marcar_como_leido_libro_existente(self, collection_with_books):
        """Debe marcar un libro existente como leído."""
        libro = collection_with_books.find_book_by_title("1984")
        assert libro.read is False
        
        collection_with_books.mark_as_read("1984")
        
        libro = collection_with_books.find_book_by_title("1984")
        assert libro.read is True
    
    def test_marcar_como_leido_libro_no_existente(self, collection):
        """Debe lanzar error al marcar libro inexistente."""
        with pytest.raises(BookNotFoundError) as exc:
            collection.mark_as_read("Nonexistent Book")
        assert "not found" in str(exc.value)
    
    def test_marcar_como_leido_case_insensitive(self, collection_with_books):
        """Debe funcionar independiente de mayúsculas/minúsculas."""
        collection_with_books.mark_as_read("dune")  # minúsculas
        
        libro = collection_with_books.find_book_by_title("Dune")
        assert libro.read is True
    
    def test_marcar_como_leido_persiste(self, collection_with_books):
        """El cambio debe persistir en el almacenamiento."""
        collection_with_books.mark_as_read("1984")
        
        # Crear nueva colección para verificar persistencia
        nueva_collection = BookCollection()
        libro = nueva_collection.find_book_by_title("1984")
        assert libro.read is True
    
    def test_marcar_como_leido_varias_veces(self, collection_with_books):
        """Debe poder marcar como leído varias veces sin error."""
        collection_with_books.mark_as_read("1984")
        collection_with_books.mark_as_read("1984")  # Segunda vez
        
        libro = collection_with_books.find_book_by_title("1984")
        assert libro.read is True
    
    def test_marcar_varios_libros_como_leidos(self, collection_with_books):
        """Debe poder marcar varios libros como leídos."""
        collection_with_books.mark_as_read("1984")
        collection_with_books.mark_as_read("Dune")
        collection_with_books.mark_as_read("Foundation")
        
        assert collection_with_books.find_book_by_title("1984").read is True
        assert collection_with_books.find_book_by_title("Dune").read is True
        assert collection_with_books.find_book_by_title("Foundation").read is True
        assert collection_with_books.find_book_by_title("Neuromancer").read is False


# ====================
# PRUEBAS: MARCAR COMO NO LEÍDO
# ====================

class TestMarkAsUnread:
    """Pruebas para marcar libros como no leídos."""
    
    def test_marcar_como_no_leido(self, collection_with_books):
        """Debe marcar un libro como no leído."""
        collection_with_books.mark_as_read("1984")
        assert collection_with_books.find_book_by_title("1984").read is True
        
        collection_with_books.mark_as_unread("1984")
        assert collection_with_books.find_book_by_title("1984").read is False
    
    def test_marcar_como_no_leido_libro_no_existente(self, collection):
        """Debe lanzar error al marcar libro inexistente como no leído."""
        with pytest.raises(BookNotFoundError) as exc:
            collection.mark_as_unread("Nonexistent Book")
        assert "not found" in str(exc.value)
    
    def test_marcar_como_no_leido_persiste(self, collection_with_books):
        """El cambio debe persistir en el almacenamiento."""
        collection_with_books.mark_as_read("1984")
        collection_with_books.mark_as_unread("1984")
        
        # Crear nueva colección para verificar persistencia
        nueva_collection = BookCollection()
        libro = nueva_collection.find_book_by_title("1984")
        assert libro.read is False


# ====================
# PRUEBAS: CASOS LÍMITE Y DATOS VACÍOS
# ====================

class TestCasosLimite:
    """Pruebas de casos límite y datos vacíos."""
    
    def test_coleccion_vacia_inicial(self, collection):
        """Una colección nueva debe estar vacía."""
        assert len(collection.books) == 0
        assert collection.list_books() == []
    
    def test_operaciones_en_coleccion_vacia(self, collection):
        """Operaciones en colección vacía deben comportarse correctamente."""
        # Buscar por título
        assert collection.find_book_by_title("Any") is None
        
        # Buscar por autor
        assert collection.find_by_author("Any") == []
        
        # Listar libros
        assert collection.list_books() == []
        
        # Buscar sin criterios
        assert collection.search() == []
    
    def test_agregar_y_eliminar_unico_libro(self, collection):
        """Debe manejar correctamente agregar y eliminar el único libro."""
        collection.add_book("Only Book", "Only Author", 2020)
        assert len(collection.books) == 1
        
        collection.remove_book("Only Book")
        assert len(collection.books) == 0
        assert len(collection._title_index) == 0
        assert len(collection._author_index) == 0
    
    def test_titulo_con_caracteres_especiales(self, collection):
        """Debe manejar títulos con caracteres especiales."""
        titulo = "Book: A Story (2020) - Part 1!"
        libro = collection.add_book(titulo, "Author", 2020)
        
        assert libro.title == titulo
        encontrado = collection.find_book_by_title(titulo)
        assert encontrado is not None
    
    def test_autor_con_caracteres_especiales(self, collection):
        """Debe manejar autores con caracteres especiales."""
        autor = "O'Brien, María José"
        libro = collection.add_book("Book", autor, 2020)
        
        assert libro.author == autor
        libros = collection.find_by_author(autor)
        assert len(libros) == 1
    
    def test_titulo_muy_largo(self, collection):
        """Debe manejar títulos muy largos."""
        titulo = "A" * 1000
        libro = collection.add_book(titulo, "Author", 2020)
        
        assert libro.title == titulo
        assert collection.find_book_by_title(titulo) is not None
    
    def test_autor_muy_largo(self, collection):
        """Debe manejar nombres de autor muy largos."""
        autor = "B" * 1000
        libro = collection.add_book("Book", autor, 2020)
        
        assert libro.author == autor
        assert len(collection.find_by_author(autor)) == 1
    
    def test_muchos_libros(self, collection):
        """Debe manejar una gran cantidad de libros."""
        cantidad = 100
        
        for i in range(cantidad):
            collection.add_book(f"Book {i}", f"Author {i % 10}", 2000 + i % 50)
        
        assert len(collection.books) == cantidad
        
        # Verificar que búsquedas funcionan correctamente
        libro = collection.find_book_by_title("Book 50")
        assert libro is not None
        
        libros_autor = collection.find_by_author("Author 5")
        assert len(libros_autor) == 10


# ====================
# PRUEBAS: BÚSQUEDA AVANZADA
# ====================

class TestSearchAdvanced:
    """Pruebas para búsqueda avanzada con múltiples criterios."""
    
    def test_buscar_sin_criterios(self, collection_with_books):
        """Debe retornar todos los libros sin criterios."""
        resultados = collection_with_books.search()
        assert len(resultados) == len(collection_with_books.books)
    
    def test_buscar_por_autor(self, collection_with_books):
        """Debe buscar por autor."""
        resultados = collection_with_books.search(author="George Orwell")
        assert len(resultados) == 1
        assert resultados[0].title == "1984"
    
    def test_buscar_por_rango_anios(self, collection_with_books):
        """Debe buscar por rango de años."""
        resultados = collection_with_books.search(year_min=1950, year_max=1970)
        assert len(resultados) == 2  # Foundation (1951) y Dune (1965)
    
    def test_buscar_por_estado_leido(self, collection_with_books):
        """Debe buscar por estado de lectura."""
        collection_with_books.mark_as_read("1984")
        collection_with_books.mark_as_read("Dune")
        
        leidos = collection_with_books.search(read=True)
        no_leidos = collection_with_books.search(read=False)
        
        assert len(leidos) == 2
        assert len(no_leidos) == 3
    
    def test_buscar_criterios_multiples(self, collection):
        """Debe buscar con múltiples criterios combinados."""
        collection.add_book("Book 1", "Author A", 2000)
        collection.add_book("Book 2", "Author A", 2010)
        collection.add_book("Book 3", "Author B", 2005)
        collection.mark_as_read("Book 2")
        
        resultados = collection.search(
            author="Author A",
            year_min=2005,
            read=True
        )
        
        assert len(resultados) == 1
        assert resultados[0].title == "Book 2"


# ====================
# PRUEBAS: INTEGRACIÓN
# ====================

class TestIntegracion:
    """Pruebas de integración de flujos completos."""
    
    def test_flujo_completo_libro(self, collection):
        """Prueba el ciclo de vida completo de un libro."""
        # 1. Agregar libro
        libro = collection.add_book("Test Book", "Test Author", 2020)
        assert libro.read is False
        
        # 2. Buscar por título
        encontrado = collection.find_book_by_title("Test Book")
        assert encontrado is not None
        
        # 3. Buscar por autor
        por_autor = collection.find_by_author("Test Author")
        assert len(por_autor) == 1
        
        # 4. Marcar como leído
        collection.mark_as_read("Test Book")
        assert collection.find_book_by_title("Test Book").read is True
        
        # 5. Marcar como no leído
        collection.mark_as_unread("Test Book")
        assert collection.find_book_by_title("Test Book").read is False
        
        # 6. Eliminar libro
        collection.remove_book("Test Book")
        assert collection.find_book_by_title("Test Book") is None
    
    def test_persistencia_entre_sesiones(self, collection):
        """Datos deben persistir entre sesiones."""
        # Sesión 1: Agregar libros
        collection.add_book("Book 1", "Author 1", 2000)
        collection.add_book("Book 2", "Author 2", 2001)
        collection.mark_as_read("Book 1")
        
        # Sesión 2: Nueva colección
        nueva_collection = BookCollection()
        
        assert len(nueva_collection.books) == 2
        assert nueva_collection.find_book_by_title("Book 1").read is True
        assert nueva_collection.find_book_by_title("Book 2").read is False
    
    def test_gestion_biblioteca_completa(self, collection):
        """Simula gestión completa de una biblioteca."""
        # Agregar varios libros
        collection.add_book("1984", "George Orwell", 1949)
        collection.add_book("Animal Farm", "George Orwell", 1945)
        collection.add_book("Brave New World", "Aldous Huxley", 1932)
        collection.add_book("Fahrenheit 451", "Ray Bradbury", 1953)
        
        # Marcar algunos como leídos
        collection.mark_as_read("1984")
        collection.mark_as_read("Animal Farm")
        
        # Buscar libros de Orwell
        orwell_books = collection.find_by_author("George Orwell")
        assert len(orwell_books) == 2
        
        # Buscar libros leídos
        leidos = collection.search(read=True)
        assert len(leidos) == 2
        
        # Buscar libros no leídos del siglo XX
        no_leidos_siglo_xx = collection.search(
            year_min=1900,
            year_max=1999,
            read=False
        )
        assert len(no_leidos_siglo_xx) == 2
        
        # Eliminar un libro
        collection.remove_book("Animal Farm")
        assert len(collection.books) == 3
        
        # Verificar que Orwell ahora tiene 1 libro
        orwell_books = collection.find_by_author("George Orwell")
        assert len(orwell_books) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
