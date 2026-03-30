# 📋 Lista de Verificación de Calidad - Book Collection App

**Fecha de revisión:** 2026-03-29  
**Versión:** 0.1.0  
**Revisado por:** GitHub Copilot CLI

---

## 🔴 CRÍTICO - Problemas que deben corregirse inmediatamente

### 🐛 **books.py**

- [ ] **Líneas 264-276: Duplicación completa de función `search()`**
  - **Problema:** El método `search()` está duplicado completamente en el archivo
  - **Impacto:** Causará error de sintaxis, código no se ejecutará
  - **Ubicación:** Líneas 264-303
  - **Solución:** Eliminar la duplicación (líneas 264-276 o 277-303)

### 🐛 **utils.py**

- [ ] **Línea 92: Validación permite strings de solo espacios en autor**
  ```python
  lambda x: 0 < len(x) <= MAX_TEXT_LENGTH
  ```
  - **Problema:** No usa `.strip()`, acepta `"     "` como válido
  - **Impacto:** Datos inválidos en la base de datos
  - **Solución:** Cambiar a `lambda x: 0 < len(x.strip()) <= MAX_TEXT_LENGTH`

- [ ] **Línea 96: Conversión `int()` sin manejo de excepciones**
  ```python
  year: int = int(_get_validated_input(...))
  ```
  - **Problema:** Si la validación falla, `int()` puede lanzar `ValueError` no capturado
  - **Impacto:** Crash de la aplicación
  - **Solución:** Envolver en try-except o asegurar que la lambda siempre valide correctamente

### 🛡️ **books.py**

- [ ] **Líneas 48-49: IndexError potencial con reviews vacías**
  ```python
  if self.reviews and isinstance(self.reviews[0], dict):
  ```
  - **Problema:** No verifica que `self.reviews` tenga elementos antes de acceder a `[0]`
  - **Impacto:** Posible crash si `self.reviews = []`
  - **Solución:** Cambiar a `if self.reviews and len(self.reviews) > 0 and isinstance(self.reviews[0], dict):`

---

## 🟡 ALTO - Problemas importantes que afectan funcionalidad

### 🔒 **utils.py**

- [ ] **Línea 46: Sin escape después de MAX_RETRIES**
  ```python
  raise ValueError(f"Failed to get valid input after {MAX_RETRIES} attempts.")
  ```
  - **Problema:** Lanza excepción que puede crashear la app
  - **Impacto:** Usuario no puede volver al menú principal
  - **Solución:** Retornar valor especial o permitir cancelación

- [ ] **Línea 86: Inconsistencia strip() entre título y autor**
  ```python
  # Título valida DESPUÉS de strip pero retorna SIN strip
  lambda x: isinstance(x, str) and 0 < len(x.strip()) <= MAX_TEXT_LENGTH
  ```
  - **Problema:** Valida longitud post-strip pero retorna pre-strip
  - **Impacto:** Almacena espacios innecesarios
  - **Solución:** Aplicar `.strip()` al valor de retorno

- [ ] **Línea 98: No valida overflow de números grandes**
  ```python
  lambda x: x.isdigit() and MIN_YEAR <= int(x) <= CURRENT_YEAR
  ```
  - **Problema:** Entrada como `"9999999999999999999"` puede causar error
  - **Impacto:** Crash al convertir números muy grandes
  - **Solución:** Validar con try-except en la lambda

### 🔄 **books.py**

- [ ] **Líneas 110-139: Tipo de retorno inconsistente en `add_book()`**
  ```python
  def add_book(...) -> Optional[Book]:
      # Retorna str en múltiples lugares
      return "Book title cannot be empty."  # línea 121
      return f"Book '{title}' by {author} already exists"  # línea 128
      return book  # línea 136
  ```
  - **Problema:** Tipo declarado `Optional[Book]` pero retorna `str` en errores
  - **Impacto:** Confusión en uso de API, errores de tipo
  - **Solución:** Cambiar a `Optional[Book]` y lanzar excepciones, o cambiar tipo a `Union[Book, str]`

- [ ] **Retorno inconsistente en múltiples métodos**
  - `mark_as_read()`: retorna `str` (declarado `str` ✓)
  - `remove_book()`: retorna `str` (declarado `str` ✓)
  - `add_review()`: retorna `Optional[Review]` pero retorna `str` en errores
  - `remove_review()`: retorna `str` (sin tipo declarado ✗)
  
  **Solución:** Unificar estrategia de manejo de errores en toda la clase

### 📝 **book_app.py**

- [ ] **Línea 207-209: Comando 'help' hardcoded fuera del patrón Command**
  ```python
  if command_name == "help":
      self.ui.show_help(self.get_help_info())
  ```
  - **Problema:** No sigue el patrón Command consistente
  - **Impacto:** Inconsistencia arquitectural
  - **Solución:** Crear `HelpCommand` class

- [ ] **Línea 148: Uso directo de `print()` en vez de UI**
  ```python
  print(f"No books found by {author}.")
  ```
  - **Problema:** FindCommand usa `print()` directo en vez de `self.ui`
  - **Impacto:** Inconsistencia en formato de salida
  - **Solución:** Usar `self.ui.print_error()` o `self.ui.print_section()`

---

## 🟠 MEDIO - Mejoras recomendadas

### 🎨 **utils.py**

- [ ] **Línea 11: Type hint incompatible con Python < 3.9**
  ```python
  VALID_CHOICES: set[str] = {"1", "2", "3", "4", "5"}
  ```
  - **Problema:** `set[str]` solo funciona en Python 3.9+
  - **pyproject.toml dice `>=3.10`** así que está OK, pero podría ser más explícito
  - **Solución:** Usar `Set[str]` de `typing` para compatibilidad o documentar requisito

- [ ] **Línea 86: `isinstance(x, str)` redundante**
  ```python
  lambda x: isinstance(x, str) and ...
  ```
  - **Problema:** `input()` siempre retorna `str`
  - **Impacto:** Código innecesario
  - **Solución:** Eliminar check redundante

### 🔍 **books.py**

- [ ] **Línea 45-46: Validación de año hardcoded**
  ```python
  if self.year < 1000 or self.year > 2100:
  ```
  - **Problema:** Límites arbitrarios (¿por qué 1000 y 2100?)
  - **Impacto:** No permite manuscritos antiguos ni libros futuros
  - **Solución:** Usar constantes configurables o ampliar rango

- [ ] **Línea 97: Método `_remove_from_indexes()` puede lanzar ValueError**
  ```python
  self._author_index[author_key].remove(book)
  ```
  - **Problema:** Si el libro no está en la lista, `remove()` lanza excepción
  - **Impacto:** Crash si índices están desincronizados
  - **Solución:** Usar `if book in list:` o try-except

### 📦 **storage.py**

- [ ] **Línea 43: Bare except clause**
  ```python
  except:
      if os.path.exists(temp_path):
  ```
  - **Problema:** Captura todas las excepciones incluyendo `KeyboardInterrupt`
  - **Impacto:** Dificulta debugging
  - **Solución:** Especificar excepciones: `except Exception:`

### 🧪 **tests/test_books.py**

- [ ] **Líneas 3: Path manipulation hacky**
  ```python
  sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
  ```
  - **Problema:** Manipulación manual del path del sistema
  - **Impacto:** Frágil, puede fallar en diferentes entornos
  - **Solución:** Usar estructura de paquete apropiada o pytest plugins

---

## 🟢 BAJO - Mejoras opcionales y best practices

### 📚 **book_app.py**

- [ ] **Línea 97-100: Validación de año permite 0**
  ```python
  year = int(year_str) if year_str else 0
  if year < 0:
  ```
  - **Problema:** Permite año 0, que no es válido históricamente
  - **Impacto:** Datos semánticamente incorrectos
  - **Solución:** Validar `year > 0` o tener política clara para "sin año"

- [ ] **Sin comando exit/quit**
  - **Problema:** No hay forma clara de salir de la aplicación
  - **Impacto:** Experiencia de usuario subóptima
  - **Solución:** Agregar `ExitCommand` o `QuitCommand`

### 🔐 **utils.py**

- [ ] **Línea 44: Logging puede exponer datos sensibles**
  ```python
  logger.error(f"Input error: {e}")
  ```
  - **Problema:** Podría logear entrada del usuario
  - **Impacto:** Potencial fuga de información
  - **Solución:** Logear sin detalles de entrada o sanitizar

### 📄 **books.py**

- [ ] **Línea 102-108: `save_books()` retorna `Optional[str]` confuso**
  - **Problema:** Retorna `None` en éxito, `str` en error
  - **Impacto:** API poco intuitiva (None = success)
  - **Solución:** Cambiar a `bool` (True=success) o lanzar excepciones

- [ ] **Línea 292: Búsqueda ineficiente para autor**
  ```python
  results = [b for b in results if b.author.lower() == author.lower()]
  ```
  - **Problema:** No usa `_author_index` existente
  - **Impacto:** Performance O(n) en vez de O(1)
  - **Solución:** Usar índice cuando solo se busca por autor

### 📖 **README.md**

- [ ] **Documentación incompleta**
  - No hay sección de instalación de dependencias
  - No explica estructura del proyecto
  - No documenta formato de data.json
  - No incluye ejemplos de uso completos

### 🏗️ **Arquitectura General**

- [ ] **No hay manejo de configuración**
  - Paths hardcoded (`DATA_FILE = "data.json"`)
  - Constantes esparcidas en múltiples archivos
  - **Solución:** Crear archivo `config.py` centralizado

- [ ] **No hay logging configuration**
  - Logging configurado en múltiples lugares
  - Niveles inconsistentes
  - **Solución:** Configuración centralizada de logging

---

## 📊 Resumen de Problemas

| Severidad | Cantidad | Porcentaje |
|-----------|----------|------------|
| 🔴 Crítico | 4 | 15% |
| 🟡 Alto | 8 | 31% |
| 🟠 Medio | 7 | 27% |
| 🟢 Bajo | 7 | 27% |
| **TOTAL** | **26** | **100%** |

---

## 🎯 Prioridades Recomendadas

### Sprint 1: Correcciones Críticas (Urgente)
1. ✅ Eliminar duplicación de función `search()` en books.py
2. ✅ Arreglar validación de espacios en autor (utils.py:92)
3. ✅ Proteger conversión int() (utils.py:96)
4. ✅ Fix IndexError en reviews (books.py:48)

### Sprint 2: Correcciones Importantes (Esta semana)
5. ✅ Unificar tipos de retorno en BookCollection
6. ✅ Mejorar manejo de errores en validación
7. ✅ Crear HelpCommand para consistencia
8. ✅ Fix overflow en validación de año

### Sprint 3: Mejoras de Calidad (Próxima semana)
9. ⚪ Eliminar bare except clauses
10. ⚪ Mejorar documentación README
11. ⚪ Optimizar búsquedas con índices
12. ⚪ Agregar comando exit/quit

### Sprint 4: Refactoring (Futuro)
13. ⚪ Centralizar configuración
14. ⚪ Mejorar estructura de tests
15. ⚪ Unified logging configuration

---

## 🔧 Herramientas Recomendadas

Para mantener calidad del código a futuro:

- **Linters:** `pylint`, `flake8`
- **Type checking:** `mypy`
- **Formateo:** `black`, `isort`
- **Security:** `bandit`
- **Coverage:** `pytest-cov`

---

## 📝 Notas Adicionales

- El proyecto usa **Command Pattern** correctamente en general
- Buena separación de responsabilidades (UI, Storage, Business Logic)
- Type hints presentes en la mayoría del código
- Tests básicos existen pero podrían expandirse
- Falta CI/CD pipeline

---

**Generado por:** GitHub Copilot CLI  
**Última actualización:** 2026-03-29
