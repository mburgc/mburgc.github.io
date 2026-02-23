# Capítulo 5: Análisis de Crashes

El análisis de crashes es el proceso de investigar por qué un programa ha fallado. Para los investigadores de seguridad, un crash es a menudo la primera indicación de una vulnerabilidad.

## 5.1. 4.1 Fundamentos del Análisis de Crashes

**Árbol de Decisión para Análisis de Crashes:**

Un árbol de decisión puede ayudar a guiar el proceso de análisis de crashes, desde la recopilación de información inicial hasta la determinación de la causa raíz.

**Suite de Pruebas Vulnerable:**

Tener una suite de pruebas con programas deliberadamente vulnerables es una excelente manera de practicar el análisis de crashes.

## 5.2. 4.2 Depuradores y Configuración

-   **WinDbg Preview para Windows:** El depurador de Windows es una herramienta poderosa para el análisis de crashes en Windows.
-   **GDB + Pwndbg para Linux:** GDB es el depurador estándar de GNU, y Pwndbg es una extensión que lo hace mucho más fácil de usar para la explotación de vulnerabilidades.
-   **Colección de Dumps:** Es crucial configurar el sistema operativo para que guarde "crash dumps" cuando un programa falla. Estos dumps se pueden analizar más tarde con un depurador.

## 5.3. 4.3 Sanitizadores de Memoria

Los sanitizadores de memoria son herramientas que instrumentan un programa en tiempo de compilación para detectar errores de memoria en tiempo de ejecución.

-   **AddressSanitizer (ASAN):** Detecta desbordamientos de búfer, uso después de liberación y otros errores de memoria.
-   **UndefinedBehaviorSanitizer (UBSAN):** Detecta comportamientos indefinidos en C/C++, como desbordamientos de enteros.
-   **MemorySanitizer (MSAN):** Detecta el uso de memoria no inicializada.
-   **ThreadSanitizer (TSAN):** Detecta condiciones de carrera.

## 5.4. 4.4 Clasificación y Triage Automatizado

-   **CASR - Crash Analysis and Severity Reporter:** Una herramienta que puede ayudar a clasificar y priorizar los crashes.
-   **Deduplicación de Crashes:** Es importante poder identificar qué crashes son duplicados del mismo bug subyacente.
-   **Minimización de Crashes:** El proceso de reducir un caso de prueba que provoca un crash a la entrada más pequeña posible.

## 5.5. 4.5 Análisis de Alcanzabilidad (Reachability Analysis)

El análisis de alcanzabilidad es el proceso de determinar qué partes de un programa se ejecutan con una entrada dada. Esto puede ser útil para entender cómo un atacante podría alcanzar una parte vulnerable del código.

-   **DynamoRIO + drcov:** Un framework de instrumentación binaria dinámica que se puede utilizar para el análisis de alcanzabilidad.
-   **Intel Processor Trace (PT):** Una característica de hardware en los procesadores Intel modernos que se puede utilizar para trazar la ejecución de un programa con muy poca sobrecarga.
-   **Frida:** Un framework de instrumentación dinámica que se puede utilizar para el tracing dinámico.
... (El resto del capítulo seguiría la misma estructura)
