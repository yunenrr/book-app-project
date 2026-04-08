---
name: lista-verificacion-codigo
description: "lista de verificación de la calidad del código del equipo: úsese para revisar la calidad del código Python, errores, problemas de seguridad y buenas prácticas"
---

# Skill lista de Verificación de Código

Aplica esta lista de verificación al revisar código Python.

## Lista de Verificación de Calidad de Código

- [ ] Todas las funciones tienen anotaciones de tipo
- [ ] No usar cláusulas except genéricas (sin especificar la excepción)
- [ ] No usar argumentos por defecto mutables
- [ ] Usar gestores de contexto para la E/S de archivos
- [ ] Las funciones tienen menos de 50 líneas
- [ ] Los nombres de variables y funciones siguen PEP 8 (snake_case)

## Lista de Verificación de Validación de Entrada

- [ ] La entrada del usuario se valida antes de procesarla
- [ ] Se manejan casos extremos (cadenas vacías, None, valores fuera de rango)
- [ ] Los mensajes de error son claros y útiles

## Lista de Verificación de Pruebas

- [ ] El nuevo código tiene pruebas pytest correspondientes
- [ ] Se cubren casos extremos
- [ ] Las pruebas usan nombres descriptivos

## Formato de Salida

Presenta los hallazgos como:

```
## Lista de Verificación de Código: [archivo]

### Calidad de Código
- [APROBADO/FALLA] Descripción del hallazgo

### Validación de Entrada
- [APROBADO/FALLA] Descripción del hallazgo

### Pruebas
- [APROBADO/FALLA] Descripción del hallazgo

### Resumen
[X] elementos requieren atención antes de fusionar
```
