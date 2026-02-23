# Capítulo 1: Introducción

## 1.1. Información del Documento

| Campo           | Valor                                   |
| --------------- | --------------------------------------- |
| Título          | Bitácora Red Team                       |
| Versión         | 1.0                                     |
| Clasificación   | Material Técnico de Referencia          |
| Idioma          | Español                                 |
| Propósito       | Educativo e Investigación Defensiva     |

## 1.2. Índice de Contenidos

### 1.2.1. [Capítulo 1: Clases de Vulnerabilidades](02-clases-vulnerabilidades.md)

- **1.1 Fundamentos de Corrupción de Memoria**
  - 1.1.1 Desbordamiento de Búfer en Pila
  - 1.1.2 Uso Después de Liberación (UAF)
  - 1.1.3 Desbordamiento de Búfer en Heap
  - 1.1.4 Lectura Fuera de Límites
  - 1.1.5 Uso de Memoria No Inicializada
  - 1.1.6 Errores de Conteo de Referencias
  - 1.1.7 Desreferencia de Puntero Nulo
- **1.2 Vulnerabilidades Lógicas y Condiciones de Carrera**
  - 1.2.1 Condiciones de Carrera
  - 1.2.2 Vulnerabilidades TOCTOU
  - 1.2.3 Vulnerabilidades Double‐Fetch
  - 1.2.4 Fallas Lógicas en Autenticación
- **1.3 Confusión de Tipos y Enteros**
  - 1.3.1 Confusión de Tipos en JIT
  - 1.3.2 Desbordamiento de Enteros
  - 1.3.3 Vulnerabilidades de Parsers
- **1.4 Vulnerabilidades de Strings y Formato**
- **1.5 Vulnerabilidades de Drivers y Sistemas de Archivos**
- **1.6 Evaluación de Impacto y Clasificación**

### 1.2.2. [Capítulo 2: Fuzzing](03-fuzzing.md)

- **2.1 Fundamentos de Fuzzing**
- **2.2 AFL++ y Fuzzing Guiado por Cobertura**
- **2.3 FuzzTest y Fuzzing In‐Process**
- **2.4 Honggfuzz y Fuzzing de Protocolos**
- **2.5 Syzkaller y Fuzzing de Kernel**

### 1.2.3. [Capítulo 3: Patch Diffing](04-patch-diffing.md)

- **3.1 Fundamentos de Patch Diffing**
- **3.2 Extracción de Parches de Windows**
- **3.3 Herramientas de Diffing Binario**
- **3.4 Análisis de Casos de Estudio**

### 1.2.4. [Capítulo 4: Análisis de Crashes](05-analisis-crashes.md)

- **4.1 Fundamentos del Análisis de Crashes**
- **4.2 Depuradores y Configuración**
- **4.3 Sanitizadores de Memoria**
- **4.4 Clasificación y Triage**
- **4.5 Evaluación de Explotabilidad**
