---
name: mensaje-commit
description: "generar mensajes de commit convencionales: úsalo al crear commits, escribir mensajes de commit o pedir ayuda con git commit"
---

# Mensaje de Commit Skill

Genera mensajes de commit siguiendo la especificación Conventional Commits.

## Formato

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

## Tipos

| Tipo | Cuándo usar |
|------|-------------|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de un bug |
| `docs` | Solo documentación |
| `style` | Formateo (sin cambios de código) |
| `refactor` | Cambio de código que no añade ni arregla |
| `perf` | Mejora de rendimiento |
| `test` | Añadir o actualizar pruebas |
| `chore` | Tareas de mantenimiento |

## Reglas

1. Línea de asunto con máximo 72 caracteres
2. Usar modo imperativo ("add" en vez de "added" o "adds")
3. No usar punto al final de la línea de asunto
4. Separar la línea de asunto del cuerpo con una línea en blanco
5. El cuerpo explica **qué** y **por qué**, no cómo
6. El mensaje de commit debe ser en español

## Ejemplos

Simple:
```
fix(auth): evitar bucle de redirección en sesiones expiradas
```

Con cuerpo:
```
feat(api): añadir limitación de tasa en endpoints públicos

- Limita las solicitudes a 100/minuto por IP
- Devuelve 429 con cabecera retry-after
- Configurable mediante la variable de entorno RATE_LIMIT_MAX

Cierra #234
```
