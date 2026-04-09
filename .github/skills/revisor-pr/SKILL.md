---
name: revisor-pr
description: "Lista de verificación de revisión de PR según el estándar del equipo"
---

# Revisor PR

Revisar los cambios de código según los estándares del equipo:

## Lista de comprobación de seguridad
- [ ] No hay secretos ni claves de API incrustadas en el código
- [ ] Validación de entrada en todos los datos de usuario
- [ ] No usar bloques `except` sin especificar la excepción
- [ ] No registrar datos sensibles

## Calidad de Código
- [ ] Funciones con menos de 50 líneas
- [ ] No usar `print` en código de producción
- [ ] Anotaciones de tipo en funciones públicas
- [ ] Usar gestores de contexto para operaciones de E/S de archivos
- [ ] No dejar TODOs sin referencia a un issue

## Pruebas
- [ ] El código nuevo tiene pruebas
- [ ] Casos límite cubiertos
- [ ] No hay pruebas omitidas sin explicación

## Documentación
- [ ] Cambios en la API documentados
- [ ] Cambios que rompen compatibilidad documentados
- [ ] README actualizado si es necesario

## Formato de salida
Proporcionar resultados como:
- ✅ PASS: Elementos que están bien
- ⚠️ WARN: Elementos que podrían mejorarse
- ❌ FAIL: Elementos que deben corregirse antes de la fusión