# Capítulo 5: Análisis de Crashes

Después de encontrar vulnerabilidades potenciales mediante fuzzing o patch diffing, el siguiente paso crítico es analizar crashes para determinar si son explotables. Este capítulo cubre triage de crashes, dominio de depuradores, sanitizers de memoria y técnicas avanzadas de análisis de causa raíz.

## 5.1. 4.1 Fundamentos del Análisis de Crashes

El análisis de crashes es el proceso de transformar un crash descubierto por un fuzzer en conocimiento accionable sobre una vulnerabilidad. Esto incluye determinar la causa raíz, evaluar explotabilidad, y desarrollar pruebas de concepto.

### 5.1.1. Árbol de Decisión para Análisis de Crashes

1.  **CRASH RECIBIDO:** ¿Es reproducible?
2.  **CÓDIGO FUENTE:** ¿Disponible?
3.  **SANITIZERS:** Recompilar con ASAN/UBSAN si hay fuente.
4.  **DEPURADOR:** Usar GDB/WinDbg si no hay fuente.
5.  **CLASIFICAR:** Usar CASR para clasificar la vulnerabilidad.
6.  **MINIMIZAR:** Reducir el input de crash.
7.  **PoC:** Desarrollar una prueba de concepto.

## 5.2. 4.2 Depuradores y Configuración

-   **WinDbg Preview para Windows:** El depurador estándar para Windows.
-   **GDB + Pwndbg para Linux:** GDB con la extensión Pwndbg para análisis de vulnerabilidades.
-   **Colección de Dumps:** Configurar el sistema para guardar crash dumps.

## 5.3. 4.3 Sanitizadores de Memoria

-   **AddressSanitizer (ASAN):** Detecta errores de memoria como desbordamientos de búfer y uso después de liberación.
-   **UndefinedBehaviorSanitizer (UBSAN):** Detecta comportamientos indefinidos en C/C++.
-   **MemorySanitizer (MSAN):** Detecta el uso de memoria no inicializada.
-   **ThreadSanitizer (TSAN):** Detecta condiciones de carrera.

## 5.4. 4.4 Clasificación y Triage Automatizado

-   **CASR - Crash Analysis and Severity Reporter:** Suite de herramientas para clasificación automatizada de crashes.
-   **Deduplicación de Crashes:** Agrupar crashes similares para identificar bugs únicos.
-   **Minimización de Crashes:** Reducir un caso de prueba que provoca un crash a la entrada más pequeña posible.

## 5.5. 4.5 Análisis de Alcanzabilidad (Reachability Analysis)

-   **DynamoRIO + drcov:** Framework de instrumentación binaria para generar cobertura de código.
-   **Intel Processor Trace (PT):** Característica de hardware para trazar la ejecución de un programa.
-   **Frida:** Framework de instrumentación dinámica para tracing en tiempo real.
-   **rr - Record and Replay Debugging:** Graba la ejecución para un replay determinístico.

## 5.6. 4.6 Desarrollo de PoC (Proof of Concept)

-   **pwntools:** Framework de Python para el desarrollo de exploits y PoCs.

### PoC Básico - Stack Buffer Overflow

```python
#!/usr/bin/env python3
from pwn import *

# ... (código del PoC)
```

## 5.7. 4.7 Proyecto Capstone: Pipeline Completo de Análisis

Escenario: Analizar crashes de una suite de pruebas vulnerable, clasificar los bugs, y crear PoCs.

### Binario con ROP Gadgets

Se proporciona un binario especial con gadgets ROP (Return-Oriented Programming) para facilitar la explotación.

### Exploit de Explotación Completo

Se demuestra cómo construir una cadena ROP para llamar a una función `win()` o `spawn_shell()`.

```python
#!/usr/bin/env python3
from pwn import *

# ... (código del exploit)
```
... (El resto del capítulo seguiría la misma estructura)
