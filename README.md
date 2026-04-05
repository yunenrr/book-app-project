# Book Collection App

Este es un proyecto educativo en Python para gestionar una colección de libros. Se usa como repositorio de práctica y aprendizaje basado en el curso: https://github.com/github/copilot-cli-for-beginners/tree/main

## Características

* 📚 Operaciones básicas (añadir, listar, eliminar, buscar libros)
* 🔍 Búsqueda avanzada por autor, rango de años y estado de lectura
* ⭐ Sistema de reseñas con calificaciones (1-5)
* ✅ Marcar libros como leídos/no leídos
* 💾 Almacenamiento persistente en JSON (data.json) con escrituras seguras

## Archivos principales

* `book_app.py` - Punto de entrada CLI
* `books.py` - Modelos de dominio (Book, Review) y BookCollection
* `storage.py` - Capa de persistencia y context managers para I/O
* `utils.py` - Utilidades de presentación y validación
* `exceptions.py` - Jerarquía de excepciones personalizadas
* `data.json` - Archivo de datos persistente
* `tests/` - Suite de pruebas (pytest)

## Instalación

```bash
# Clonar el repositorio
cd book-app-project

# Instalar dependencias mínimas para pruebas
pip install pytest

# Ejecutar pruebas
python -m pytest tests/ -v
```

## Uso (CLI)

Comandos básicos (la interfaz es interactiva en algunas acciones):

```bash
python book_app.py list      # Listar libros
python book_app.py add       # Añadir un libro (interactivo)
python book_app.py find      # Buscar por título
python book_app.py remove    # Eliminar un libro
python book_app.py read      # Marcar libro como leído
python book_app.py search    # Búsqueda avanzada
python book_app.py review    # Añadir reseña
python book_app.py help      # Mostrar ayuda
```

Ejemplo de flujo:

- Añadir un libro: ejecuta `python book_app.py add` y sigue las indicaciones para título, autor y año.
- Listar libros: `python book_app.py list`.

## Tests

La suite de pruebas usa pytest. Ejecutar:

```bash
python -m pytest tests/ -v
```

Asegurarse de que las pruebas pasen antes de proponer cambios.
