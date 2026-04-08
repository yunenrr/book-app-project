---
name: auditor-seguridad
description: "Revisión de código enfocada en la seguridad que verifica las 10 principales vulnerabilidades de OWASP (Proyecto Abierto de Seguridad en Aplicaciones Web)"
---
# Auditoría de seguridad

Realizar una auditoría de seguridad verificando:

## Vulnerabilidades de inyección
- Inyección SQL (concatenación de cadenas en consultas)
- Inyección de comandos (comandos de shell no saneados)
- Inyección LDAP
- Inyección XPath

## Problemas de autenticación
- Credenciales codificadas en el código
- Requisitos de contraseña débiles
- Falta de limitación de tasa
- Fallos en la gestión de sesiones

## Datos sensibles
- Contraseñas en texto plano
- Claves API en el código
- Registro de información sensible
- Falta de cifrado

## Control de acceso
- Falta de comprobaciones de autorización
- Referencias directas a objetos inseguras
- Vulnerabilidades de recorrido de rutas (path traversal)

## Salida
Para cada problema encontrado, proporcionar:
1. Archivo y número de línea
2. Tipo de vulnerabilidad
3. Severidad (CRITICAL/HIGH/MEDIUM/LOW)
4. Corrección recomendada