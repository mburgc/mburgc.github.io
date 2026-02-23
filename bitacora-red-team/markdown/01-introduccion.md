---
title: "Capítulo 01: Introducción"
chapter: 01
description: "Introducción - Manual de Explotación del Kernel de Linux"
---

Desde el CRASH hasta el EXPLOIT
Explotación Moderna del Kernel de Linux
Marcelo Ernesto Burgos Cayupil

---

Bitácora Red Team
Explotación moderna del kernel de Linux
© 2026 Marcelo Ernesto Burgos Cayupil
Esta obra se distribuye bajo la licencia Creative Commons
Attribution-NonCommercial 4.0 International (CC BY-NC 4.0).
Se permite su distribución y reproducción no comercial
citando adecuadamente al autor.

---

Índice general
1. Introducción

### 1.1. Información del Documento
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

### 1.2. Índice de Contenidos . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

### 1.2.1.
Capítulo 1: Clases de Vulnerabilidades . . . . . . . . . . . . . . . . . . . . . .

### 1.2.2.
Capítulo 2: Fuzzing
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

### 1.2.3.
Capítulo 3: Patch Diffing
. . . . . . . . . . . . . . . . . . . . . . . . . . . . .

### 1.2.4.
Capítulo 4: Análisis de Crashes . . . . . . . . . . . . . . . . . . . . . . . . . .

2. Clases de Vulnerabilidades

### 2.1. 1.1 Fundamentos de Corrupción de Memoria . . . . . . . . . . . . . . . . . . . . . .

### 2.1.1.
### 1.1.1 Desbordamiento de Búfer en Pila ﴾Stack Buffer Overflow﴿. . . . . . . . .

### 2.1.2.
### 1.1.2 Uso Después de Liberación ﴾Use‐After‐Free / UAF﴿
. . . . . . . . . . . .

### 2.1.3.
### 1.1.3 Desbordamiento de Búfer en Heap ﴾Heap Buffer Overflow﴿. . . . . . . .

### 2.1.4.
### 1.1.4 Lectura Fuera de Límites ﴾Out‐of‐Bounds Read / Info Leak﴿. . . . . . . .

### 2.1.5.
### 1.1.5 Uso de Memoria No Inicializada ﴾Uninitialized Memory Use﴿. . . . . . .

### 2.1.6.
### 1.1.6 Errores de Conteo de Referencias ﴾Reference Counting Bugs﴿
. . . . . .

### 2.1.7.
### 1.1.7 Desreferencia de Puntero Nulo ﴾NULL Pointer Dereference﴿
. . . . . . .

### 2.1.8.
### 1.1.8 Conclusiones de Corrupción de Memoria
. . . . . . . . . . . . . . . . .

### 2.2. 1.2 Vulnerabilidades Lógicas y Condiciones de Carrera . . . . . . . . . . . . . . . . .

### 2.2.1.
### 1.2.1 Condiciones de Carrera ﴾Race Conditions﴿. . . . . . . . . . . . . . . . .

### 2.2.2.
### 1.2.2 Vulnerabilidades TOCTOU ﴾Time‐of‐Check Time‐of‐Use﴿. . . . . . . . .

### 2.2.3.
### 1.2.3 Vulnerabilidades Double‐Fetch . . . . . . . . . . . . . . . . . . . . . . .

### 2.2.4.
### 1.2.4 Fallas Lógicas en Autenticación . . . . . . . . . . . . . . . . . . . . . . .

### 2.2.5.
### 1.2.5 Escritura Arbitraria ﴾Write‐What‐Where﴿. . . . . . . . . . . . . . . . . .

### 2.2.6.
### 1.2.6 Mal Uso de Locking/RCU . . . . . . . . . . . . . . . . . . . . . . . . . .

### 2.2.7.
### 1.2.7 Conclusiones de Vulnerabilidades Lógicas . . . . . . . . . . . . . . . . .

### 2.3. 1.3 Confusión de Tipos y Enteros . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

### 2.3.1.
### 1.3.1 Confusión de Tipos en JIT . . . . . . . . . . . . . . . . . . . . . . . . . .

### 2.3.2.
### 1.3.2 Desbordamiento de Enteros
. . . . . . . . . . . . . . . . . . . . . . . .

### 2.3.3.
### 1.3.3 Vulnerabilidades de Parsers . . . . . . . . . . . . . . . . . . . . . . . . .

### 2.4. 1.4 Vulnerabilidades de Strings y Formato . . . . . . . . . . . . . . . . . . . . . . . .

### 2.5. 1.5 Vulnerabilidades de Drivers y Sistemas de Archivos . . . . . . . . . . . . . . . . .

### 2.5.1.
Vulnerabilidades de Manejadores IOCTL/Syscall . . . . . . . . . . . . . . . . .

### 2.5.2.
Vulnerabilidades de Sistemas de Archivos . . . . . . . . . . . . . . . . . . . .

### 2.5.3.
Bring Your Own Vulnerable Driver ﴾BYOVD﴿
. . . . . . . . . . . . . . . . . . .

### 2.6. 1.6 Evaluación de Impacto y Clasificación
. . . . . . . . . . . . . . . . . . . . . . . .

---

### ÍNDICE GENERAL
Bitácora Red Team
### 2.6.1.
Categorías de Impacto
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

### 2.6.2.
Factores de Explotabilidad
. . . . . . . . . . . . . . . . . . . . . . . . . . . .

### 2.6.3.
Sistema de Puntuación CVSS . . . . . . . . . . . . . . . . . . . . . . . . . . .

### 2.6.4.
Conclusiones del Capítulo 1
. . . . . . . . . . . . . . . . . . . . . . . . . . .

3. Fuzzing

### 3.1. 2.1 Fundamentos de Fuzzing . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

### 3.2. 2.2 AFL++ y Fuzzing Guiado por Cobertura . . . . . . . . . . . . . . . . . . . . . . .

### 3.3. 2.3 FuzzTest y Fuzzing In‐Process . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

### 3.4. 2.4 Honggfuzz y Fuzzing de Protocolos
. . . . . . . . . . . . . . . . . . . . . . . . .

### 3.5. 2.5 Syzkaller y Fuzzing de Kernel . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

### 3.6. 2.6 Configuración Práctica de AFL++ . . . . . . . . . . . . . . . . . . . . . . . . . . .

### 3.7. 2.7 Análisis de Crashes y Evaluación de Explotabilidad
. . . . . . . . . . . . . . . . .

### 3.7.1.
### 2.7.1 Caso de Estudio: Análisis de Heap Buffer Overflow
. . . . . . . . . . . .

### 3.7.2.
### 2.7.2 Caso de Estudio: Análisis de Use‐After‐Free . . . . . . . . . . . . . . . .

### 3.7.3.
### 2.7.3 Caso de Estudio: Integer Overflow →Heap Corruption . . . . . . . . . .

### 3.8. 2.8 Desarrollo de Harnesses de Fuzzing
. . . . . . . . . . . . . . . . . . . . . . . . .

### 3.8.1.
### 2.8.1 Ejemplo: Harness para Parser JSON
. . . . . . . . . . . . . . . . . . . .

### 3.8.2.
### 2.8.2 Principios de Diseño de Harness . . . . . . . . . . . . . . . . . . . . . .

### 3.8.3.
Conclusiones del Capítulo 2
. . . . . . . . . . . . . . . . . . . . . . . . . . .

4. Patch Diffing

### 4.1. 3.1 Fundamentos de Patch Diffing . . . . . . . . . . . . . . . . . . . . . . . . . . . .

### 4.2. 3.2 Extracción de Parches de Windows . . . . . . . . . . . . . . . . . . . . . . . . . .

### 4.2.1.
### 3.2.1 Script de Extracción PowerShell ﴾Extract‐Patch.ps1﴿. . . . . . . . . . . .

### 4.2.2.
### 3.2.2 Descarga de Símbolos ﴾PDB﴿. . . . . . . . . . . . . . . . . . . . . . . .

### 4.3. 3.3 Herramientas de Diffing Binario
. . . . . . . . . . . . . . . . . . . . . . . . . . .

### 4.3.1.
### 3.3.1 Instalación de Ghidra y Ghidriff . . . . . . . . . . . . . . . . . . . . . . .

### 4.3.2.
### 3.3.2 Flujo de Trabajo con Ghidriff
. . . . . . . . . . . . . . . . . . . . . . . .

### 4.3.3.
### 3.3.3 Version Tracking de Ghidra ﴾Alternativa GUI﴿. . . . . . . . . . . . . . . .

### 4.4. 3.4 Caso de Estudio: CVE‐2022‐34718 ﴾EvilESP﴿. . . . . . . . . . . . . . . . . . . . .

### 4.4.1.
### 3.4.1 Adquisición de Binarios para EvilESP . . . . . . . . . . . . . . . . . . . .

### 4.4.2.
### 3.4.2 Ejecutar Diff y Análisis . . . . . . . . . . . . . . . . . . . . . . . . . . . .

### 4.4.3.
### 3.4.3 Análisis de Código Vulnerable vs Parcheado . . . . . . . . . . . . . . . .

### 4.4.4.
### 3.4.4 Flujo de Ataque Visual
. . . . . . . . . . . . . . . . . . . . . . . . . . .

### 4.4.5.
### 3.4.5 Estructura de Paquetes ESP e IPv6
. . . . . . . . . . . . . . . . . . . . .

### 4.4.6.
### 3.4.6 Primitiva de Explotación . . . . . . . . . . . . . . . . . . . . . . . . . . .

### 4.4.7.
### 3.4.7 Resumen del Parche . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

### 4.4.8.
### 3.4.8 Lecciones del Caso de Estudio
. . . . . . . . . . . . . . . . . . . . . . .

### 4.5. 3.5 Pipeline de Automatización de Patch Diffing
. . . . . . . . . . . . . . . . . . . .

### 4.5.1.
### 3.5.1 Script de Automatización Python para Ghidriff
. . . . . . . . . . . . . .

### 4.5.2.
### 3.5.2 Automatización con Task Scheduler ﴾Windows﴿. . . . . . . . . . . . . .

### 4.5.3.
### 3.5.3 Integración con LLMs para Resumen . . . . . . . . . . . . . . . . . . . .

### 4.6. 3.6 Patch Diffing en Linux Kernel . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

### 4.6.1.
### 3.6.1 Diferencias con Windows . . . . . . . . . . . . . . . . . . . . . . . . . .

### 4.6.2.
### 3.6.2 Flujo de Trabajo para Linux . . . . . . . . . . . . . . . . . . . . . . . . .

### 4.6.3.
### 3.6.3 Diff a Nivel de Código Fuente
. . . . . . . . . . . . . . . . . . . . . . .

### 4.6.4.
### 3.6.4 Ejemplo: CVE‐2024‐1086 ﴾nf_tables UAF﴿. . . . . . . . . . . . . . . . . .

---

### ÍNDICE GENERAL
Bitácora Red Team
### 4.6.5.
### 3.6.5 Recursos para Linux Kernel . . . . . . . . . . . . . . . . . . . . . . . . .

### 4.7. 3.7 Caso de Estudio: 7‐Zip Path Traversal
. . . . . . . . . . . . . . . . . . . . . . . .

### 4.7.1.
### 3.7.1 Información del Caso . . . . . . . . . . . . . . . . . . . . . . . . . . . .

### 4.7.2.
### 3.7.2 Análisis del Parche . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

### 4.7.3.
### 3.7.3 Escenario de Ataque . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

### 4.7.4.
### 3.7.4 Checklist de Triage para Código de Validación de Paths . . . . . . . . . .

### 4.7.5.
Conclusiones del Capítulo 3
. . . . . . . . . . . . . . . . . . . . . . . . . . .

5. Análisis de Crashes

### 5.1. 4.1 Fundamentos del Análisis de Crashes
. . . . . . . . . . . . . . . . . . . . . . . .

### 5.1.1.
### 4.1.1 Árbol de Decisión para Análisis de Crashes
. . . . . . . . . . . . . . . .

### 5.1.2.
### 4.1.2 Selección de Herramientas por Escenario
. . . . . . . . . . . . . . . . .

### 5.1.3.
### 4.1.3 Suite de Pruebas Vulnerable
. . . . . . . . . . . . . . . . . . . . . . . .

### 5.2. 4.2 Depuradores y Configuración . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

### 5.2.1.
### 4.2.1 WinDbg Preview para Windows
. . . . . . . . . . . . . . . . . . . . . .

### 5.2.2.
### 4.2.2 GDB + Pwndbg para Linux
. . . . . . . . . . . . . . . . . . . . . . . . .

### 5.2.3.
### 4.2.3 Colección de Dumps
. . . . . . . . . . . . . . . . . . . . . . . . . . . . 100
### 5.2.4.
### 4.2.4 PageHeap y AppVerifier ﴾Windows﴿. . . . . . . . . . . . . . . . . . . . . 101
### 5.3. 4.3 Sanitizadores de Memoria
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 102
### 5.3.1.
### 4.3.1 AddressSanitizer ﴾ASAN﴿
. . . . . . . . . . . . . . . . . . . . . . . . . . 102
### 5.3.2.
### 4.3.2 UndefinedBehaviorSanitizer ﴾UBSAN﴿
. . . . . . . . . . . . . . . . . . . 104
### 5.3.3.
### 4.3.3 MemorySanitizer ﴾MSAN﴿. . . . . . . . . . . . . . . . . . . . . . . . . . 104
### 5.3.4.
### 4.3.4 ThreadSanitizer ﴾TSAN﴿. . . . . . . . . . . . . . . . . . . . . . . . . . . 104
### 5.3.5.
### 4.3.5 Matriz de Compatibilidad de Sanitizers
. . . . . . . . . . . . . . . . . . 105
### 5.3.6.
### 4.3.6 GWP‐ASan para Producción
. . . . . . . . . . . . . . . . . . . . . . . . 106
### 5.4. 4.4 Clasificación y Triage Automatizado
. . . . . . . . . . . . . . . . . . . . . . . . . 107
### 5.4.1.
### 4.4.1 CASR ‐ Crash Analysis and Severity Reporter
. . . . . . . . . . . . . . . 107
### 5.4.2.
### 4.4.2 Clases de Severidad de CASR . . . . . . . . . . . . . . . . . . . . . . . . 108
### 5.4.3.
### 4.4.3 Checklist de Triage Rápido
. . . . . . . . . . . . . . . . . . . . . . . . . 109
### 5.4.4.
### 4.4.4 Deduplicación de Crashes . . . . . . . . . . . . . . . . . . . . . . . . . . 110
### 5.4.5.
### 4.4.5 Detección de Timeouts y Hangs
. . . . . . . . . . . . . . . . . . . . . . 112
### 5.4.6.
### 4.4.6 Minimización de Crashes . . . . . . . . . . . . . . . . . . . . . . . . . . 112
### 5.5. 4.5 Análisis de Alcanzabilidad ﴾Reachability Analysis﴿. . . . . . . . . . . . . . . . . . 114
### 5.5.1.
### 4.5.1 DynamoRIO + drcov . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 114
### 5.5.2.
### 4.5.2 Intel Processor Trace ﴾PT﴿. . . . . . . . . . . . . . . . . . . . . . . . . . 115
### 5.5.3.
### 4.5.3 Frida para Tracing Dinámico
. . . . . . . . . . . . . . . . . . . . . . . . 115
### 5.5.4.
### 4.5.4 rr ‐ Record and Replay Debugging . . . . . . . . . . . . . . . . . . . . . 117
### 5.5.5.
### 4.5.5 Análisis de Taint ﴾Flujo de Datos﴿. . . . . . . . . . . . . . . . . . . . . . 118
### 5.5.6.
### 4.5.6 Plantilla de Reporte de Alcanzabilidad . . . . . . . . . . . . . . . . . . . 119
### 5.5.7.
6. COBERTURA DE EJECUCIÓN . . . . . . . . . . . . . . . . . . . . . . . . . . 120
### 5.5.8.
### 7. MITIGACIONES PRESENTES
. . . . . . . . . . . . . . . . . . . . . . . . . . 120
### 5.5.9.
### 4.6.2 Pipeline Automatizado Crash‐to‐PoC . . . . . . . . . . . . . . . . . . . . 123
### 5.5.10. 4.6.3 PoC para Servicios de Red . . . . . . . . . . . . . . . . . . . . . . . . . . 127
### 5.5.11. 4.6.4 Análisis de Crashes en Rust y Go . . . . . . . . . . . . . . . . . . . . . . 130
### 5.6. 4.7 Proyecto Capstone: Pipeline Completo de Análisis
. . . . . . . . . . . . . . . . . 131
### 5.6.1.
### 4.7.1 Escenario . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 131
### 5.6.2.
### 4.7.2 Binario con ROP Gadgets . . . . . . . . . . . . . . . . . . . . . . . . . . 131
### 5.6.3.
### 4.7.3 Exploit de Explotación Completo . . . . . . . . . . . . . . . . . . . . . . 134

---

### ÍNDICE GENERAL
Bitácora Red Team
### 5.6.4.
### 4.7.4 Generación del Reporte Final . . . . . . . . . . . . . . . . . . . . . . . . 137
### 5.6.5.
### 4.7.5 Checklist del Capstone
. . . . . . . . . . . . . . . . . . . . . . . . . . . 139
### 5.7. 4.8 Conclusiones del Capítulo 4
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . 140
### 5.7.1.
Principios Fundamentales . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 140
### 5.7.2.
Tabla de Herramientas Clave . . . . . . . . . . . . . . . . . . . . . . . . . . . 141
### 5.7.3.
Preguntas de Discusión . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 141
### 5.8. Documentación y Estándares . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 141
### 5.9. Herramientas Principales . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 141
### 5.10. Fuentes de Información de Vulnerabilidades
. . . . . . . . . . . . . . . . . . . . . . 142