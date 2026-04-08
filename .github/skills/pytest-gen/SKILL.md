---
name: pytest-gen
description: "Genera pruebas pytest completas - úsalo al generar pruebas, crear suites de prueba o probar código Python"
---

# Generación de pruebas con pytest

Al generar pruebas, sigue esta estructura.

## Organización de pruebas

- Agrupa las pruebas por la función bajo prueba
- Usa `@pytest.mark.parametrize` para múltiples entradas
- Usa fixtures para configuraciones compartidas
- Sigue el patrón arrange/act/assert

## Requisitos de cobertura

- Ruta feliz (uso esperado)
- Casos límite (cadenas vacías, None, valores límite)
- Casos de error (entrada inválida, archivo no encontrado, tipos incorrectos)
- Integración (funciones trabajando juntas)

## Plantilla

```python
import pytest
from module_under_test import function_to_test


@pytest.fixture
def sample_data():
    """Proporciona datos de prueba compartidos."""
    return {"key": "value"}


class TestFunctionName:
    """Pruebas para `function_to_test`."""

    def test_happy_path(self, sample_data):
        result = function_to_test(valid_input)
        assert result == expected_output

    def test_empty_input(self):
        result = function_to_test("")
        assert result == expected_for_empty

    @pytest.mark.parametrize("input_val,expected", [
        ("valid", True),
        ("", False),
        (None, False),
    ])
    def test_various_inputs(self, input_val, expected):
        assert function_to_test(input_val) == expected
```
