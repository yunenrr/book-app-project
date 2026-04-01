"""
Pruebas completas para utils.py
================================
Suite de pruebas exhaustivas para la función get_book_details que cubre:
- Entrada válida
- Cadenas vacías
- Formatos de año inválidos
- Títulos muy largos
- Caracteres especiales en los nombres de los autores

Autor: Generado con GitHub Copilot
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import utils
from utils import (
    get_book_details,
    validate_input,
    extract_book_data,
    prepare_books_for_display,
    print_books,
    show_books,
    render_book_line,
    BookDisplayData,
    MAX_TEXT_LENGTH,
    MIN_YEAR,
    CURRENT_YEAR
)
from exceptions import (
    MaxRetriesExceededError,
    UserCancelledError,
    DisplayError,
    InputTooLongError
)


# ====================
# PRUEBAS: get_book_details - ENTRADA VÁLIDA
# ====================

class TestGetBookDetailsEntradaValida:
    """Pruebas para get_book_details con entradas válidas."""
    
    @patch('builtins.input')
    def test_entrada_valida_basica(self, mock_input):
        """Debe aceptar entrada válida básica."""
        mock_input.side_effect = ['1984', 'George Orwell', '1949']
        
        title, author, year = get_book_details()
        
        assert title == '1984'
        assert author == 'George Orwell'
        assert year == 1949
    
    @patch('builtins.input')
    def test_entrada_con_espacios_al_inicio_y_final(self, mock_input):
        """Debe eliminar espacios al inicio y final."""
        mock_input.side_effect = ['  Dune  ', '  Frank Herbert  ', '1965']
        
        title, author, year = get_book_details()
        
        assert title == 'Dune'
        assert author == 'Frank Herbert'
        assert year == 1965
    
    @patch('builtins.input')
    def test_titulo_con_multiples_palabras(self, mock_input):
        """Debe aceptar títulos con múltiples palabras."""
        mock_input.side_effect = [
            'The Lord of the Rings',
            'J.R.R. Tolkien',
            '1954'
        ]
        
        title, author, year = get_book_details()
        
        assert title == 'The Lord of the Rings'
        assert author == 'J.R.R. Tolkien'
        assert year == 1954
    
    @patch('builtins.input')
    def test_anio_minimo_valido(self, mock_input):
        """Debe aceptar el año mínimo válido (MIN_YEAR)."""
        mock_input.side_effect = ['Ancient Book', 'Old Author', str(MIN_YEAR)]
        
        title, author, year = get_book_details()
        
        assert year == MIN_YEAR
    
    @patch('builtins.input')
    def test_anio_actual(self, mock_input):
        """Debe aceptar el año actual."""
        mock_input.side_effect = ['New Book', 'Modern Author', str(CURRENT_YEAR)]
        
        title, author, year = get_book_details()
        
        assert year == CURRENT_YEAR
    
    @patch('builtins.input')
    def test_titulo_longitud_maxima(self, mock_input):
        """Debe aceptar título con longitud máxima permitida."""
        titulo_maximo = 'A' * MAX_TEXT_LENGTH
        mock_input.side_effect = [titulo_maximo, 'Author', '2020']
        
        title, author, year = get_book_details()
        
        assert title == titulo_maximo
        assert len(title) == MAX_TEXT_LENGTH
    
    @patch('builtins.input')
    def test_autor_longitud_maxima(self, mock_input):
        """Debe aceptar autor con longitud máxima permitida."""
        autor_maximo = 'B' * MAX_TEXT_LENGTH
        mock_input.side_effect = ['Book Title', autor_maximo, '2020']
        
        title, author, year = get_book_details()
        
        assert author == autor_maximo
        assert len(author) == MAX_TEXT_LENGTH


# ====================
# PRUEBAS: get_book_details - CADENAS VACÍAS
# ====================

class TestGetBookDetailsCadenasVacias:
    """Pruebas para get_book_details con cadenas vacías."""
    
    @patch('builtins.input')
    def test_titulo_vacio(self, mock_input):
        """Debe rechazar título vacío y lanzar excepción después de reintentos."""
        mock_input.side_effect = ['', '', '']  # 3 intentos vacíos
        
        with pytest.raises(MaxRetriesExceededError):
            get_book_details()
    
    @patch('builtins.input')
    def test_titulo_solo_espacios(self, mock_input):
        """Debe rechazar título con solo espacios."""
        mock_input.side_effect = ['   ', '   ', '   ']  # 3 intentos con espacios
        
        with pytest.raises(MaxRetriesExceededError):
            get_book_details()
    
    @patch('builtins.input')
    def test_titulo_vacio_luego_valido(self, mock_input):
        """Debe aceptar entrada válida después de intentos vacíos."""
        mock_input.side_effect = [
            '',  # primer intento: vacío
            'Valid Title',  # segundo intento: válido
            'Valid Author',
            '2020'
        ]
        
        title, author, year = get_book_details()
        
        assert title == 'Valid Title'
        assert author == 'Valid Author'
        assert year == 2020
    
    @patch('builtins.input')
    def test_autor_vacio(self, mock_input):
        """Debe rechazar autor vacío."""
        mock_input.side_effect = [
            'Valid Title',
            '',  # autor vacío
            '',  # intento 2
            ''   # intento 3
        ]
        
        with pytest.raises(MaxRetriesExceededError):
            get_book_details()
    
    @patch('builtins.input')
    def test_autor_solo_espacios(self, mock_input):
        """Debe rechazar autor con solo espacios."""
        mock_input.side_effect = [
            'Valid Title',
            '   ',  # autor solo espacios
            '   ',
            '   '
        ]
        
        with pytest.raises(MaxRetriesExceededError):
            get_book_details()
    
    @patch('builtins.input')
    def test_autor_vacio_luego_valido(self, mock_input):
        """Debe aceptar autor válido después de intentos vacíos."""
        mock_input.side_effect = [
            'Valid Title',
            '',  # primer intento: vacío
            'Valid Author',  # segundo intento: válido
            '2020'
        ]
        
        title, author, year = get_book_details()
        
        assert title == 'Valid Title'
        assert author == 'Valid Author'
        assert year == 2020


# ====================
# PRUEBAS: get_book_details - FORMATOS DE AÑO INVÁLIDOS
# ====================

class TestGetBookDetailsAniosInvalidos:
    """Pruebas para get_book_details con formatos de año inválidos."""
    
    @patch('builtins.input')
    def test_anio_no_numerico(self, mock_input):
        """Debe rechazar año no numérico."""
        mock_input.side_effect = [
            'Book Title',
            'Author',
            'abc',  # año no numérico
            'xyz',
            'not-a-year'
        ]
        
        with pytest.raises(MaxRetriesExceededError):
            get_book_details()
    
    @patch('builtins.input')
    def test_anio_con_letras(self, mock_input):
        """Debe rechazar año con letras mezcladas."""
        mock_input.side_effect = [
            'Book Title',
            'Author',
            '20a0',
            '19b9',
            '2o20'
        ]
        
        with pytest.raises(MaxRetriesExceededError):
            get_book_details()
    
    @patch('builtins.input')
    def test_anio_decimal(self, mock_input):
        """Debe rechazar año con decimales."""
        mock_input.side_effect = [
            'Book Title',
            'Author',
            '2020.5',
            '1999.9',
            '2021.0'
        ]
        
        with pytest.raises(MaxRetriesExceededError):
            get_book_details()
    
    @patch('builtins.input')
    def test_anio_negativo(self, mock_input):
        """Debe rechazar año negativo."""
        mock_input.side_effect = [
            'Book Title',
            'Author',
            '-2020',
            '-1999',
            '-100'
        ]
        
        with pytest.raises(MaxRetriesExceededError):
            get_book_details()
    
    @patch('builtins.input')
    def test_anio_menor_al_minimo(self, mock_input):
        """Debe rechazar año menor al mínimo (MIN_YEAR)."""
        mock_input.side_effect = [
            'Book Title',
            'Author',
            str(MIN_YEAR - 1),
            '999',
            '500'
        ]
        
        with pytest.raises(MaxRetriesExceededError):
            get_book_details()
    
    @patch('builtins.input')
    def test_anio_mayor_al_actual(self, mock_input):
        """Debe rechazar año mayor al actual."""
        mock_input.side_effect = [
            'Book Title',
            'Author',
            str(CURRENT_YEAR + 1),
            str(CURRENT_YEAR + 10),
            '2200'
        ]
        
        with pytest.raises(MaxRetriesExceededError):
            get_book_details()
    
    @patch('builtins.input')
    def test_anio_cero(self, mock_input):
        """Debe rechazar año cero."""
        mock_input.side_effect = [
            'Book Title',
            'Author',
            '0',
            '00',
            '000'
        ]
        
        with pytest.raises(MaxRetriesExceededError):
            get_book_details()
    
    @patch('builtins.input')
    def test_anio_invalido_luego_valido(self, mock_input):
        """Debe aceptar año válido después de intentos inválidos."""
        mock_input.side_effect = [
            'Valid Title',
            'Valid Author',
            'abc',  # primer intento: no numérico
            '2020'  # segundo intento: válido
        ]
        
        title, author, year = get_book_details()
        
        assert title == 'Valid Title'
        assert author == 'Valid Author'
        assert year == 2020
    
    @patch('builtins.input')
    def test_anio_con_espacios(self, mock_input):
        """Debe manejar año con espacios (se eliminan al hacer strip)."""
        mock_input.side_effect = [
            'Book Title',
            'Author',
            '  2020  '  # espacios alrededor
        ]
        
        title, author, year = get_book_details()
        
        assert year == 2020


# ====================
# PRUEBAS: get_book_details - TÍTULOS MUY LARGOS
# ====================

class TestGetBookDetailsTitulosLargos:
    """Pruebas para get_book_details con títulos muy largos."""
    
    @patch('builtins.input')
    def test_titulo_excede_longitud_maxima(self, mock_input):
        """Debe rechazar título que excede longitud máxima."""
        titulo_largo = 'A' * (MAX_TEXT_LENGTH + 1)
        mock_input.side_effect = [
            titulo_largo,
            titulo_largo,
            titulo_largo
        ]
        
        with pytest.raises(MaxRetriesExceededError):
            get_book_details()
    
    @patch('builtins.input')
    def test_titulo_muy_largo(self, mock_input):
        """Debe rechazar título extremadamente largo (1000+ caracteres)."""
        titulo_muy_largo = 'A' * 1000
        mock_input.side_effect = [
            titulo_muy_largo,
            titulo_muy_largo,
            titulo_muy_largo
        ]
        
        with pytest.raises(MaxRetriesExceededError):
            get_book_details()
    
    @patch('builtins.input')
    def test_titulo_largo_luego_valido(self, mock_input):
        """Debe aceptar título válido después de rechazar uno largo."""
        titulo_largo = 'A' * (MAX_TEXT_LENGTH + 1)
        titulo_valido = 'Valid Title'
        mock_input.side_effect = [
            titulo_largo,  # primer intento: muy largo
            titulo_valido,  # segundo intento: válido
            'Valid Author',
            '2020'
        ]
        
        title, author, year = get_book_details()
        
        assert title == titulo_valido
        assert len(title) <= MAX_TEXT_LENGTH
    
    @patch('builtins.input')
    def test_autor_excede_longitud_maxima(self, mock_input):
        """Debe rechazar autor que excede longitud máxima."""
        autor_largo = 'B' * (MAX_TEXT_LENGTH + 1)
        mock_input.side_effect = [
            'Valid Title',
            autor_largo,
            autor_largo,
            autor_largo
        ]
        
        with pytest.raises(MaxRetriesExceededError):
            get_book_details()
    
    @patch('builtins.input')
    def test_autor_muy_largo(self, mock_input):
        """Debe rechazar autor extremadamente largo."""
        autor_muy_largo = 'B' * 1000
        mock_input.side_effect = [
            'Valid Title',
            autor_muy_largo,
            autor_muy_largo,
            autor_muy_largo
        ]
        
        with pytest.raises(MaxRetriesExceededError):
            get_book_details()
    
    @patch('builtins.input')
    def test_titulo_y_autor_en_limite(self, mock_input):
        """Debe aceptar título y autor exactamente en el límite."""
        titulo_limite = 'A' * MAX_TEXT_LENGTH
        autor_limite = 'B' * MAX_TEXT_LENGTH
        mock_input.side_effect = [titulo_limite, autor_limite, '2020']
        
        title, author, year = get_book_details()
        
        assert len(title) == MAX_TEXT_LENGTH
        assert len(author) == MAX_TEXT_LENGTH
    
    @patch('builtins.input')
    def test_titulo_un_caracter_sobre_limite(self, mock_input):
        """Debe rechazar título con un carácter sobre el límite."""
        titulo_limite_mas_uno = 'A' * (MAX_TEXT_LENGTH + 1)
        mock_input.side_effect = [
            titulo_limite_mas_uno,
            titulo_limite_mas_uno,
            titulo_limite_mas_uno
        ]
        
        with pytest.raises(MaxRetriesExceededError):
            get_book_details()


# ====================
# PRUEBAS: get_book_details - CARACTERES ESPECIALES EN AUTORES
# ====================

class TestGetBookDetailsCaracteresEspeciales:
    """Pruebas para get_book_details con caracteres especiales en nombres de autores."""
    
    @patch('builtins.input')
    def test_autor_con_apostrofe(self, mock_input):
        """Debe aceptar autor con apóstrofe."""
        mock_input.side_effect = [
            'Book Title',
            "O'Brien",
            '2020'
        ]
        
        title, author, year = get_book_details()
        
        assert author == "O'Brien"
    
    @patch('builtins.input')
    def test_autor_con_guion(self, mock_input):
        """Debe aceptar autor con guión."""
        mock_input.side_effect = [
            'Book Title',
            'Jean-Paul Sartre',
            '1943'
        ]
        
        title, author, year = get_book_details()
        
        assert author == 'Jean-Paul Sartre'
    
    @patch('builtins.input')
    def test_autor_con_punto(self, mock_input):
        """Debe aceptar autor con puntos (iniciales)."""
        mock_input.side_effect = [
            'The Hobbit',
            'J.R.R. Tolkien',
            '1937'
        ]
        
        title, author, year = get_book_details()
        
        assert author == 'J.R.R. Tolkien'
    
    @patch('builtins.input')
    def test_autor_con_tildes(self, mock_input):
        """Debe aceptar autor con tildes."""
        mock_input.side_effect = [
            'Cien años de soledad',
            'Gabriel García Márquez',
            '1967'
        ]
        
        title, author, year = get_book_details()
        
        assert author == 'Gabriel García Márquez'
    
    @patch('builtins.input')
    def test_autor_con_enie(self, mock_input):
        """Debe aceptar autor con ñ."""
        mock_input.side_effect = [
            'Book Title',
            'José Muñoz',
            '2000'
        ]
        
        title, author, year = get_book_details()
        
        assert author == 'José Muñoz'
    
    @patch('builtins.input')
    def test_titulo_con_dos_puntos(self, mock_input):
        """Debe aceptar título con dos puntos."""
        mock_input.side_effect = [
            'Book: A Story',
            'Author Name',
            '2020'
        ]
        
        title, author, year = get_book_details()
        
        assert title == 'Book: A Story'
    
    @patch('builtins.input')
    def test_titulo_con_signos_exclamacion_interrogacion(self, mock_input):
        """Debe aceptar título con signos de exclamación e interrogación."""
        mock_input.side_effect = [
            '¿Quién es? ¡Yo!',
            'Autor Español',
            '2015'
        ]
        
        title, author, year = get_book_details()
        
        assert title == '¿Quién es? ¡Yo!'
    
    @patch('builtins.input')
    def test_titulo_con_parentesis(self, mock_input):
        """Debe aceptar título con paréntesis."""
        mock_input.side_effect = [
            'Book Title (Extended Edition)',
            'Author',
            '2020'
        ]
        
        title, author, year = get_book_details()
        
        assert title == 'Book Title (Extended Edition)'
    
    @patch('builtins.input')
    def test_autor_con_numeros(self, mock_input):
        """Debe aceptar autor con números."""
        mock_input.side_effect = [
            'Book',
            'Author 2nd',
            '2020'
        ]
        
        title, author, year = get_book_details()
        
        assert author == 'Author 2nd'
    
    @patch('builtins.input')
    def test_autor_con_caracteres_unicode(self, mock_input):
        """Debe aceptar autor con diversos caracteres Unicode."""
        mock_input.side_effect = [
            'Book Title',
            'Müller, François & José',
            '2020'
        ]
        
        title, author, year = get_book_details()
        
        assert author == 'Müller, François & José'
    
    @patch('builtins.input')
    def test_titulo_con_simbolos_especiales(self, mock_input):
        """Debe aceptar título con símbolos especiales."""
        mock_input.side_effect = [
            'Book #1: The Beginning & The End',
            'Author',
            '2020'
        ]
        
        title, author, year = get_book_details()
        
        assert title == 'Book #1: The Beginning & The End'


# ====================
# PRUEBAS: CANCELACIÓN DE OPERACIÓN
# ====================

class TestGetBookDetailsCancelacion:
    """Pruebas para manejo de cancelación de operación."""
    
    @patch('builtins.input')
    def test_cancelacion_con_keyboard_interrupt(self, mock_input):
        """Debe lanzar UserCancelledError cuando el usuario cancela (Ctrl+C)."""
        mock_input.side_effect = KeyboardInterrupt()
        
        with pytest.raises(UserCancelledError):
            get_book_details()


# ====================
# PRUEBAS: FUNCIONES AUXILIARES
# ====================

class TestValidateInput:
    """Pruebas para la función validate_input."""
    
    def test_validacion_exitosa(self):
        """Debe retornar True para entrada válida."""
        result = validate_input("1984", lambda x: len(x) > 0)
        assert result is True
    
    def test_validacion_fallida(self):
        """Debe retornar False para entrada inválida."""
        result = validate_input("", lambda x: len(x) > 0)
        assert result is False
    
    def test_validacion_con_excepcion(self):
        """Debe retornar False si el validador lanza excepción."""
        def bad_validator(x):
            raise ValueError("Error")
        
        result = validate_input("test", bad_validator)
        assert result is False


class TestBookDisplayData:
    """Pruebas para la clase BookDisplayData."""
    
    def test_format_status_read(self):
        """Debe retornar '✓' para libro leído."""
        data = BookDisplayData(1, "Title", "Author", 2020, True)
        assert data.format_status() == "✓"
    
    def test_format_status_unread(self):
        """Debe retornar ' ' para libro no leído."""
        data = BookDisplayData(1, "Title", "Author", 2020, False)
        assert data.format_status() == " "
    
    def test_format_status_text_read(self):
        """Debe retornar '✅ Read' para libro leído."""
        data = BookDisplayData(1, "Title", "Author", 2020, True)
        assert data.format_status_text() == "✅ Read"
    
    def test_format_status_text_unread(self):
        """Debe retornar '📖 Unread' para libro no leído."""
        data = BookDisplayData(1, "Title", "Author", 2020, False)
        assert data.format_status_text() == "📖 Unread"


class TestExtractBookData:
    """Pruebas para la función extract_book_data."""
    
    def test_extraer_datos_completos(self):
        """Debe extraer todos los datos de un libro."""
        book = MagicMock()
        book.title = "1984"
        book.author = "George Orwell"
        book.year = 1949
        book.read = True
        
        data = extract_book_data(book, 1)
        
        assert data.index == 1
        assert data.title == "1984"
        assert data.author == "George Orwell"
        assert data.year == 1949
        assert data.read is True
    
    def test_extraer_datos_con_valores_por_defecto(self):
        """Debe usar valores por defecto si faltan atributos."""
        book = MagicMock(spec=[])  # Sin atributos
        
        data = extract_book_data(book, 5)
        
        assert data.index == 5
        assert data.title == "Unknown Title"
        assert data.author == "Unknown Author"
        assert data.year == 0
        assert data.read is False


class TestRenderBookLine:
    """Pruebas para la función render_book_line."""
    
    def test_render_estilo_cli_leido(self):
        """Debe renderizar correctamente en estilo CLI para libro leído."""
        data = BookDisplayData(1, "1984", "George Orwell", 1949, True)
        line = render_book_line(data, style="cli")
        
        assert line == "1. [✓] 1984 by George Orwell (1949)"
    
    def test_render_estilo_cli_no_leido(self):
        """Debe renderizar correctamente en estilo CLI para libro no leído."""
        data = BookDisplayData(2, "Dune", "Frank Herbert", 1965, False)
        line = render_book_line(data, style="cli")
        
        assert line == "2. [ ] Dune by Frank Herbert (1965)"
    
    def test_render_estilo_detailed_leido(self):
        """Debe renderizar correctamente en estilo detallado para libro leído."""
        data = BookDisplayData(1, "1984", "George Orwell", 1949, True)
        line = render_book_line(data, style="detailed")
        
        assert line == "1. 1984 by George Orwell (1949) - ✅ Read"
    
    def test_render_estilo_detailed_no_leido(self):
        """Debe renderizar correctamente en estilo detallado para libro no leído."""
        data = BookDisplayData(2, "Dune", "Frank Herbert", 1965, False)
        line = render_book_line(data, style="detailed")
        
        assert line == "2. Dune by Frank Herbert (1965) - 📖 Unread"


class TestPrepareBooksForDisplay:
    """Pruebas para la función prepare_books_for_display."""
    
    def test_preparar_lista_vacia(self):
        """Debe retornar lista vacía para entrada vacía."""
        result = prepare_books_for_display([])
        assert result == []
    
    def test_preparar_un_libro(self):
        """Debe preparar un libro para display."""
        book = MagicMock()
        book.title = "Test"
        book.author = "Author"
        book.year = 2020
        book.read = False
        
        result = prepare_books_for_display([book])
        
        assert len(result) == 1
        assert result[0].title == "Test"
    
    def test_preparar_varios_libros(self):
        """Debe preparar varios libros con índices correctos."""
        books = []
        for i in range(3):
            book = MagicMock()
            book.title = f"Book {i+1}"
            book.author = f"Author {i+1}"
            book.year = 2020 + i
            book.read = False
            books.append(book)
        
        result = prepare_books_for_display(books)
        
        assert len(result) == 3
        assert result[0].index == 1
        assert result[1].index == 2
        assert result[2].index == 3


# ====================
# PRUEBAS: INTEGRACIÓN
# ====================

class TestIntegracionGetBookDetails:
    """Pruebas de integración para get_book_details."""
    
    @patch('builtins.input')
    def test_flujo_completo_exitoso(self, mock_input):
        """Debe completar el flujo completo con datos válidos."""
        mock_input.side_effect = [
            'The Great Gatsby',
            'F. Scott Fitzgerald',
            '1925'
        ]
        
        title, author, year = get_book_details()
        
        assert title == 'The Great Gatsby'
        assert author == 'F. Scott Fitzgerald'
        assert year == 1925
        assert isinstance(title, str)
        assert isinstance(author, str)
        assert isinstance(year, int)
    
    @patch('builtins.input')
    def test_multiples_reintentos_hasta_exito(self, mock_input):
        """Debe aceptar entrada válida después de varios intentos."""
        mock_input.side_effect = [
            '',  # título vacío
            'Valid Title',  # título válido
            '   ',  # autor vacío
            'Valid Author',  # autor válido
            'abc',  # año inválido
            '2020'  # año válido
        ]
        
        title, author, year = get_book_details()
        
        assert title == 'Valid Title'
        assert author == 'Valid Author'
        assert year == 2020
    
    @patch('builtins.input')
    def test_datos_con_unicode_completo(self, mock_input):
        """Debe manejar correctamente datos con caracteres Unicode."""
        mock_input.side_effect = [
            'Crónicas de una muerte anunciada',
            'García Márquez, Gabriel José',
            '1981'
        ]
        
        title, author, year = get_book_details()
        
        assert 'Crónicas' in title
        assert 'García' in author
        assert 'José' in author
        assert year == 1981


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
