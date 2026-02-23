# Capítulo 3: Fuzzing

El fuzzing es una técnica automatizada de descubrimiento de vulnerabilidades que ha encontrado miles de bugs de seguridad críticos en software de producción. Este capítulo cubre los fundamentos del fuzzing, herramientas clave y metodologías para encontrar vulnerabilidades.

## 3.1. 2.1 Fundamentos de Fuzzing

**¿Qué es el Fuzzing?**

El fuzzing es el proceso de alimentar un programa con datos malformados, inesperados o aleatorios en un intento de provocar un crash o un comportamiento anómalo. Es una forma de prueba de caja negra o caja gris que no requiere acceso al código fuente.

**Tipos de Fuzzers:**

-   **Dumb Fuzzers:** Generan entradas aleatorias sin conocimiento del formato de entrada. Son simples pero ineficientes.
-   **Smart Fuzzers:** Tienen conocimiento del formato de entrada y generan entradas que son más propensas a provocar errores.
-   **Fuzzers Guiados por Cobertura:** (El más común hoy en día) Usan instrumentación para rastrear qué partes del código se ejecutan con una entrada dada. Luego, mutan las entradas para explorar nuevas rutas de código.

## 3.2. 2.2 AFL++ y Fuzzing Guiado por Cobertura

AFL++ es un fuzzer guiado por cobertura de última generación que ha encontrado un gran número de vulnerabilidades en software del mundo real.

**Cómo Funciona:**

1.  **Instrumentación:** El código fuente se compila con instrumentación especial que registra la cobertura de código.
2.  **Corpus Inicial:** El fuzzer comienza con un conjunto de entradas de prueba válidas (el corpus).
3.  **Mutación:** AFL++ muta las entradas del corpus de varias maneras (volteo de bits, aritmética, etc.).
4.  **Ejecución:** El programa instrumentado se ejecuta con la entrada mutada.
5.  **Análisis:** Si la entrada mutada explora una nueva ruta de código, se añade al corpus. Si provoca un crash, se guarda para su análisis.

## 3.3. 2.3 FuzzTest y Fuzzing In-Process

FuzzTest es un framework de fuzzing in-process de Google. A diferencia de AFL++, que ejecuta el programa en un proceso separado para cada entrada, FuzzTest ejecuta el fuzzer dentro del mismo proceso que el código que se está probando. Esto puede ser mucho más rápido para ciertos tipos de aplicaciones.

## 3.4. 2.4 Honggfuzz y Fuzzing de Protocolos

Honggfuzz es otro popular fuzzer guiado por cobertura. Es conocido por su rendimiento y sus características avanzadas, como el fuzzing persistente y el fuzzing de protocolos de red.

## 3.5. 2.5 Syzkaller y Fuzzing de Kernel

Syzkaller es un fuzzer especializado para encontrar vulnerabilidades en los kernels de los sistemas operativos. Utiliza un lenguaje de descripción de sistemas de llamadas para generar programas que ejercen las interfaces del kernel. Syzkaller ha sido extremadamente exitoso en la búsqueda de vulnerabilidades en el kernel de Linux.
... (El resto del capítulo seguiría la misma estructura)
