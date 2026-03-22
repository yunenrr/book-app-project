# Plan: Agregar Funciones de Búsqueda a la Aplicación de Libros

## Problema y Enfoque
La aplicación actual solo permite buscar por autor (`find`). Se necesita expandir las capacidades de búsqueda para permitir que los usuarios encuentren libros por título y año, facilitando la exploración de la colección.

## Análisis Actual
- **books.py**: 
  - Tiene `find_by_author()` que busca por autor
  - Tiene `find_book_by_title()` que busca un libro (uso interno)
  - Necesita métodos adicionales para búsqueda por título y año

- **book_app.py**:
  - Tiene `handle_find()` para búsqueda por autor
  - Necesita nuevos handlers para otras búsquedas
  - Necesita actualizar `show_help()`

## Decisiones de Diseño
- **Criterios**: Búsqueda por título, autor y año (3 comandos separados)
- **Comandos nuevos**: 
  - `search_title` - busca libros por título (búsqueda parcial, case-insensitive)
  - `search_year` - busca libros por año de publicación
  - Se mantiene `find` para búsqueda por autor (renombrar a `search_author` para consistencia o mantener?)
- **Búsqueda**: Case-insensitive, búsqueda parcial (no exacta)
- **Mensajes**: Mostrar resultados con formato consistente

## Implementación

### 1. Agregar métodos en BookCollection (books.py)
- `search_by_title(title: str) -> List[Book]` - búsqueda parcial de título
- `search_by_year(year: int) -> List[Book]` - búsqueda exacta de año

### 2. Agregar handlers en book_app.py
- `handle_search_title()` - solicita título y llama al método
- `handle_search_year()` - solicita año y llama al método
- Opción: Renombrar `handle_find()` a `handle_search_author()` o mantenerlo para compatibilidad

### 3. Actualizar CLI (book_app.py)
- Actualizar `show_help()` con nuevos comandos
- Actualizar `main()` con nuevos cases

### 4. Actualizar/Agregar Tests
- Tests para `search_by_title()`
- Tests para `search_by_year()`
- Tests para handlers CLI

### 5. Verificación
- Ejecutar todos los tests
- Probar manualmente cada comando

## Notas
- La búsqueda por título será parcial (ej: buscar "Hobbit" encontrará "The Hobbit")
- Mantener compatibilidad con comando `find` existente
