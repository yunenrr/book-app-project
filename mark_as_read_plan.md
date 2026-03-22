# Plan: Agregar Comando "Marcar como Leído"

## Problema y Enfoque
La aplicación de libros ya tiene la funcionalidad de marcar libros como leídos en la clase `BookCollection` (método `mark_as_read()`), pero no existe un comando CLI para acceder a esta funcionalidad. El objetivo es exponer este comando en la interfaz de línea de comandos.

## Análisis Actual
- **books.py**: Contiene `BookCollection` con método `mark_as_read()` ya implementado
- **book_app.py**: CLI principal que necesita el nuevo comando
- **Estructura de datos**: El atributo `read` ya existe en la clase `Book`
- **data.json**: Persiste el estado de lectura

## Decisiones
- Nombre del comando: `mark_read` (en inglés, para consistencia con otros comandos)
- El comando solicitará el título del libro y actualizará su estado
- Se actualizarán tests existentes para cubrir la nueva funcionalidad

## Tareas

1. **Agregar función handle_mark_read() en book_app.py**
   - Solicitar título del libro
   - Llamar a collection.mark_as_read()
   - Mostrar mensaje de éxito/error

2. **Actualizar show_help() en book_app.py**
   - Agregar línea para el nuevo comando en la ayuda

3. **Actualizar main() en book_app.py**
   - Agregar case para "mark_read"

4. **Actualizar tests (si existen)**
   - Agregar tests para el nuevo comando

5. **Verificar funcionamiento**
   - Ejecutar tests
   - Probar manualmente el comando
