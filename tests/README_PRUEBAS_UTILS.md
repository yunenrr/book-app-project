# Documentación de Pruebas - utils.py

## 📋 Resumen

Se han creado **60 pruebas exhaustivas** para el archivo `utils.py`, con especial énfasis en la función `get_book_details()`.

## 📁 Archivo de Prueba: `test_utils.py`

### 🎯 Cobertura Total

**60 pruebas** organizadas en 10 clases que cubren:

#### ✅ **Entrada Válida (7 pruebas)**
- ✅ Entrada básica válida
- ✅ Entrada con espacios al inicio y final (trim)
- ✅ Títulos con múltiples palabras
- ✅ Año mínimo válido (MIN_YEAR = 1000)
- ✅ Año actual (CURRENT_YEAR)
- ✅ Título en longitud máxima permitida (200 caracteres)
- ✅ Autor en longitud máxima permitida (200 caracteres)

**Ejemplo de prueba:**
```python
@patch('builtins.input')
def test_entrada_valida_basica(self, mock_input):
    mock_input.side_effect = ['1984', 'George Orwell', '1949']
    title, author, year = get_book_details()
    assert title == '1984'
    assert author == 'George Orwell'
    assert year == 1949
```

#### ✅ **Cadenas Vacías (6 pruebas)**
- ✅ Título vacío (lanza MaxRetriesExceededError)
- ✅ Título solo espacios (lanza MaxRetriesExceededError)
- ✅ Título vacío seguido de entrada válida
- ✅ Autor vacío (lanza MaxRetriesExceededError)
- ✅ Autor solo espacios (lanza MaxRetriesExceededError)
- ✅ Autor vacío seguido de entrada válida

**Validación:**
- Se rechaza cualquier entrada vacía o con solo espacios
- Se permite hasta 3 reintentos antes de lanzar excepción
- Se valida que `strip()` elimina espacios correctamente

#### ✅ **Formatos de Año Inválidos (9 pruebas)**
- ✅ Año no numérico (texto)
- ✅ Año con letras mezcladas (20a0, 19b9)
- ✅ Año con decimales (2020.5)
- ✅ Año negativo (-2020)
- ✅ Año menor al mínimo (< 1000)
- ✅ Año mayor al actual (> CURRENT_YEAR)
- ✅ Año cero
- ✅ Año inválido seguido de válido (recuperación)
- ✅ Año con espacios (se eliminan correctamente)

**Validaciones de año:**
```python
- Debe ser numérico (solo dígitos)
- Rango válido: MIN_YEAR (1000) a CURRENT_YEAR (2026)
- No se aceptan decimales, negativos, ni texto
```

#### ✅ **Títulos Muy Largos (7 pruebas)**
- ✅ Título excede longitud máxima (+1 carácter)
- ✅ Título muy largo (1000+ caracteres)
- ✅ Título largo seguido de válido
- ✅ Autor excede longitud máxima
- ✅ Autor muy largo (1000+ caracteres)
- ✅ Título y autor exactamente en el límite (200 caracteres)
- ✅ Título con un carácter sobre el límite

**Límite de longitud:**
```python
MAX_TEXT_LENGTH = 200 caracteres
- Títulos y autores deben tener entre 1 y 200 caracteres
- Se rechaza cualquier entrada > 200 caracteres
```

#### ✅ **Caracteres Especiales en Nombres de Autores (11 pruebas)**
- ✅ Autor con apóstrofe (O'Brien)
- ✅ Autor con guión (Jean-Paul Sartre)
- ✅ Autor con puntos/iniciales (J.R.R. Tolkien)
- ✅ Autor con tildes (García Márquez)
- ✅ Autor con ñ (José Muñoz)
- ✅ Título con dos puntos (Book: A Story)
- ✅ Título con signos de exclamación/interrogación (¿Quién es? ¡Yo!)
- ✅ Título con paréntesis (Extended Edition)
- ✅ Autor con números (Author 2nd)
- ✅ Autor con caracteres Unicode (Müller, François & José)
- ✅ Título con símbolos especiales (#, &)

**Caracteres especiales soportados:**
```
- Apóstrofes: '
- Guiones: -
- Puntos: .
- Tildes: á, é, í, ó, ú
- Eñe: ñ
- Paréntesis: ( )
- Dos puntos: :
- Signos: ¿ ? ¡ ! # &
- Unicode: ü, ö, à, è, etc.
```

#### ✅ **Cancelación de Operación (1 prueba)**
- ✅ Cancelación con Ctrl+C (KeyboardInterrupt → UserCancelledError)

#### ✅ **Funciones Auxiliares (3 pruebas)**
- ✅ `validate_input()` - validación exitosa
- ✅ `validate_input()` - validación fallida
- ✅ `validate_input()` - manejo de excepciones

#### ✅ **BookDisplayData (4 pruebas)**
- ✅ `format_status()` para libro leído (✓)
- ✅ `format_status()` para libro no leído ( )
- ✅ `format_status_text()` para libro leído (✅ Read)
- ✅ `format_status_text()` para libro no leído (📖 Unread)

#### ✅ **extract_book_data (2 pruebas)**
- ✅ Extracción de datos completos de un libro
- ✅ Uso de valores por defecto si faltan atributos

#### ✅ **render_book_line (4 pruebas)**
- ✅ Renderizado estilo CLI para libro leído
- ✅ Renderizado estilo CLI para libro no leído
- ✅ Renderizado estilo detallado para libro leído
- ✅ Renderizado estilo detallado para libro no leído

#### ✅ **prepare_books_for_display (3 pruebas)**
- ✅ Preparar lista vacía
- ✅ Preparar un libro
- ✅ Preparar varios libros con índices correctos

#### ✅ **Integración (3 pruebas)**
- ✅ Flujo completo exitoso
- ✅ Múltiples reintentos hasta éxito
- ✅ Datos con Unicode completo

## 📊 Resultados de Ejecución

```
============= 60 passed in 1.20s =============
Total del proyecto: 213 passed in 4.23s
```

✅ **100% de pruebas pasando**
✅ **Todos los casos solicitados cubiertos**

## 🎯 Tabla de Cobertura por Categoría

| Categoría | Pruebas | Estado |
|-----------|---------|--------|
| Entrada válida | 7 | ✅ |
| Cadenas vacías | 6 | ✅ |
| Formatos de año inválidos | 9 | ✅ |
| Títulos muy largos | 7 | ✅ |
| Caracteres especiales | 11 | ✅ |
| Cancelación | 1 | ✅ |
| Funciones auxiliares | 3 | ✅ |
| BookDisplayData | 4 | ✅ |
| extract_book_data | 2 | ✅ |
| render_book_line | 4 | ✅ |
| prepare_books_for_display | 3 | ✅ |
| Integración | 3 | ✅ |

## 🚀 Ejecución de Pruebas

### Ejecutar todas las pruebas de utils:
```bash
pytest tests/test_utils.py -v
```

### Ejecutar categorías específicas:
```bash
# Solo pruebas de entrada válida
pytest tests/test_utils.py::TestGetBookDetailsEntradaValida -v

# Solo pruebas de cadenas vacías
pytest tests/test_utils.py::TestGetBookDetailsCadenasVacias -v

# Solo pruebas de años inválidos
pytest tests/test_utils.py::TestGetBookDetailsAniosInvalidos -v

# Solo pruebas de títulos largos
pytest tests/test_utils.py::TestGetBookDetailsTitulosLargos -v

# Solo pruebas de caracteres especiales
pytest tests/test_utils.py::TestGetBookDetailsCaracteresEspeciales -v
```

### Ejecutar con salida detallada:
```bash
pytest tests/test_utils.py -vv --tb=long
```

## 🔧 Técnicas de Testing Utilizadas

### 1. **Mocking de Input**
Se utiliza `@patch('builtins.input')` para simular entrada del usuario:
```python
@patch('builtins.input')
def test_entrada_valida_basica(self, mock_input):
    mock_input.side_effect = ['1984', 'George Orwell', '1949']
    title, author, year = get_book_details()
```

### 2. **side_effect para Múltiples Inputs**
Simula secuencias de entrada (reintentos):
```python
mock_input.side_effect = [
    '',  # primer intento vacío
    'Valid Title',  # segundo intento válido
    'Valid Author',
    '2020'
]
```

### 3. **Verificación de Excepciones**
```python
with pytest.raises(MaxRetriesExceededError):
    get_book_details()
```

### 4. **Simulación de Cancelación**
```python
mock_input.side_effect = KeyboardInterrupt()
with pytest.raises(UserCancelledError):
    get_book_details()
```

## 🔍 Casos de Prueba Especiales

### Caso 1: Recuperación de Errores
```python
# Usuario comete errores pero finalmente ingresa datos válidos
mock_input.side_effect = [
    '',  # Error: título vacío
    'Valid Title',  # OK
    '   ',  # Error: autor vacío
    'Valid Author',  # OK
    'abc',  # Error: año no numérico
    '2020'  # OK
]
```

### Caso 2: Límites Exactos
```python
# Título exactamente en MAX_TEXT_LENGTH (200)
titulo_limite = 'A' * 200  # OK
titulo_largo = 'A' * 201   # ERROR
```

### Caso 3: Unicode Completo
```python
# Soporte completo para caracteres internacionales
mock_input.side_effect = [
    'Crónicas de una muerte anunciada',
    'García Márquez, Gabriel José',
    '1981'
]
```

## 📝 Constantes del Sistema

Las pruebas utilizan las siguientes constantes definidas en `utils.py`:

```python
CURRENT_YEAR = datetime.now().year  # 2026
MIN_YEAR = 1000
MAX_TEXT_LENGTH = 200
MAX_RETRIES = 3
```

## 🎓 Buenas Prácticas Implementadas

- ✅ **Organización por clases** - Pruebas agrupadas por funcionalidad
- ✅ **Nombres descriptivos** - Nombres en español claros y específicos
- ✅ **Docstrings completos** - Cada prueba explica qué verifica
- ✅ **Mocking apropiado** - Se mockea `input()` para evitar interacción manual
- ✅ **Cobertura exhaustiva** - Todos los casos límite y normales
- ✅ **Pruebas atómicas** - Cada prueba verifica un solo comportamiento
- ✅ **Verificación de tipos** - Se valida el tipo de retorno
- ✅ **Manejo de errores** - Se verifican excepciones apropiadas

## 🏆 Resumen de Validaciones

### ✅ Validaciones de Título
- No vacío
- No solo espacios
- Longitud ≤ 200 caracteres
- Soporta caracteres especiales y Unicode

### ✅ Validaciones de Autor
- No vacío
- No solo espacios
- Longitud ≤ 200 caracteres
- Soporta caracteres especiales (O'Brien, Jean-Paul, etc.)
- Soporta Unicode completo

### ✅ Validaciones de Año
- Solo dígitos (numérico)
- Rango: 1000 ≤ año ≤ CURRENT_YEAR
- No decimales
- No negativos
- Se eliminan espacios

### ✅ Sistema de Reintentos
- Máximo 3 intentos por campo
- Mensajes de error claros
- Recuperación de errores
- Cancelación con Ctrl+C

## 🎯 Conclusión

El archivo `test_utils.py` proporciona una cobertura **completa y exhaustiva** de la función `get_book_details()` y sus funciones auxiliares. Todas las especificaciones solicitadas están cubiertas:

✅ **Entrada válida** - 7 pruebas  
✅ **Cadenas vacías** - 6 pruebas  
✅ **Formatos de año inválidos** - 9 pruebas  
✅ **Títulos muy largos** - 7 pruebas  
✅ **Caracteres especiales en autores** - 11 pruebas  

El conjunto de pruebas garantiza que `get_book_details()` maneja correctamente todos los escenarios posibles, desde entradas válidas hasta casos límite y errores.
