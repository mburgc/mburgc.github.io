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

## 3.6. 2.6 Configuración Práctica de AFL++

### Instalación Paso a Paso

```bash
# Instalar dependencias de compilación
sudo apt update
sudo apt install -y build-essential gcc-13-plugin-dev cpio python3-dev 
    libcapstone-dev pkg-config libglib2.0-dev libpixman-1-dev 
    automake autoconf python3-pip ninja-build cmake git wget meson

# Instalar LLVM 19 (verificar última versión en https://apt.llvm.org/)
wget https://apt.llvm.org/llvm.sh
chmod +x llvm.sh
sudo ./llvm.sh 19 all

# Verificar instalación de LLVM
clang-19 --version
llvm-config-19 --version

# Instalar Rust (requerido para algunos componentes de AFL++)
curl --proto '=https' --tlsv1.2 -sSf "https://sh.rustup.rs" | sh
source ~/.cargo/env

# Compilar e instalar AFL++
mkdir -p ~/soft && cd ~/soft
git clone --depth 1 https://github.com/AFLplusplus/AFLplusplus.git
cd AFLplusplus
make distrib
sudo make install

# Verificar instalación
which afl-fuzz
afl-fuzz --version
```

### Compilación de Target con Instrumentación

```bash
# Compilar programa C/C++ con instrumentación AFL++
CC=/usr/local/bin/afl-clang-fast 
CXX=/usr/local/bin/afl-clang-fast++ 
cmake ..
make -j$(nproc)

# Habilitar sanitizers para mejor detección de bugs
export AFL_USE_ASAN=1
export AFL_USE_UBSAN=1
export ASAN_OPTIONS="detect_leaks=1:abort_on_error=1:symbolize=1"
```

### Ejecución del Fuzzer

```bash
# Configurar sistema para fuzzing óptimo
echo core | sudo tee /proc/sys/kernel/core_pattern
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Crear corpus de semillas
mkdir -p seeds
for i in {0..4}; do
    dd if=/dev/urandom of=seeds/seed_$i bs=64 count=10 2>/dev/null
done

# Ejecutar fuzzer
afl-fuzz -i seeds/ -o findings/ -m none -d -- ./target_binary @@

# Fuzzing paralelo (múltiples instancias)
# Terminal 1: Instancia Master
afl-fuzz -i seeds/ -o findings/ -M Master -- ./target @@

# Terminal 2+: Instancias Slave
afl-fuzz -i seeds/ -o findings/ -S Slave1 -- ./target @@
afl-fuzz -i seeds/ -o findings/ -S Slave2 -- ./target @@

# Verificar estado
afl-whatsup findings/
```

## 3.7. 2.7 Análisis de Crashes y Evaluación de Explotabilidad

El análisis de crashes es el proceso de determinar si un crash descubierto por fuzzing representa una vulnerabilidad explotable. Esta sección cubre las herramientas y metodologías para triage sistemático de crashes.

### Árbol de Decisión para Análisis de Crashes

```
                      CRASH RECIBIDO
                            │
                            ▼
                  ┌───────────────────────┐
                  │ ¿Código fuente        │
                  │   disponible?         │
                  └───────────────────────┘
                       │                    │
                      Sí                    No
                       │                    │
                       ▼                    ▼
         ┌─────────────────────┐    ┌─────────────────────┐
         │ Recompilar con      │    │ Usar depurador        │
         │ ASAN + UBSAN        │    │ (GDB/WinDbg)          │
         └─────────────────────┘    └─────────────────────┘
                       │                    │
                       ▼                    ▼
         ┌─────────────────────┐    ┌─────────────────────┐
         │ Ejecutar crash      │    │ Analizar registros    │
         │ Obtener reporte     │    │ y memoria             │
         └─────────────────────┘    └─────────────────────┘
                       │                    │
                       └────────┬───────────┘
                                ▼
                  ┌───────────────────────────┐
                  │ Clasificar vulnerabilidad │
                  │ con CASR                  │
                  └───────────────────────────┘
```

### 3.7.1. 2.7.1 Caso de Estudio: Análisis de Heap Buffer Overflow

**Escenario:** El fuzzing descubrió un crash en un parser de imágenes. Analicemos paso a paso.

**Código Vulnerable:**

```c
// vuln_parser.c - Parser de imágenes vulnerable
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

void build_huffman_table(uint8_t *input, size_t size) {
    if (size < 8) return;

    uint32_t table_size = *(uint32_t*)input;
    uint8_t *codes = input + 4;
    uint8_t *table = malloc(256);
    memcpy(table, codes, table_size);
    printf("Built Huffman table with %u codes\n", table_size);
    free(table);
}
```

**Salida de ASAN:**

```
==37160==ERROR: AddressSanitizer: heap-buffer-overflow on address
0x511000000140 at pc 0x56d6a37d0f62 bp 0x7ffd9f024440 sp 0x7ffd9f023c00
WRITE of size 512 at 0x511000000140 thread T0
```

**Interpretación:**

| Campo | Valor | Significado |
|-------|-------|-------------|
| Tipo de Bug | heap-buffer-overflow | Desbordamiento de heap |
| Operación | WRITE of size 512 | Escribiendo 512 bytes |
| Ubicación | vuln_parser.c:16 | Línea del bug |
| Asignación | 256-byte buffer | Búfer asignado |
| Overflow | 512 - 256 = 256 | Cantidad de overflow |

**Evaluación: EXPLOITABLE** - Atacante controla tamaño y datos del overflow.

### 3.7.2. 2.7.2 Caso de Estudio: Análisis de Use-After-Free

**Código Vulnerable:**

```c
typedef struct {
    char *name;
    void (*process)(void);
} Handler;

Handler *handler = NULL;

void unregister_handler(void) {
    if (handler) {
        free(handler);
        // BUG: Falta handler = NULL
    }
}

void call_handler(void) {
    if (handler) {
        handler->process(); // UAF!
    }
}
```

**Estrategia de Explotación:**
1. Liberar handler
2. Heap grooming: asignar objetos del mismo tamaño
3. Reclamar memoria liberada con datos controlados
4. Trigger UAF → ejecución de código

**Evaluación: EXPLOITABLE**

### 3.7.3. 2.7.3 Caso de Estudio: Integer Overflow → Heap Corruption

**Código Vulnerable:**

```c
void process_image(uint32_t width, uint32_t height, uint8_t *data) {
    size_t buffer_size = width * height * 4; // overflow!
    uint8_t *buffer = malloc(buffer_size);
    for (size_t i = 0; i < width * height; i++) {
        buffer[i] = data[i]; // massive overflow
    }
}
```

**Cadena:** Integer overflow → malloc(0) → loop con bounds grandes → heap corruption

**Evaluación: EXPLOITABLE**

## 3.8. 2.8 Desarrollo de Harnesses de Fuzzing

### 3.8.1. 2.8.1 Ejemplo: Harness para Parser JSON

```c
// fuzz_json.c
#include <json-c/json.h>
#include <stdint.h>
#include <stddef.h>

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    const char *data1 = (const char *)data;
    json_tokener *tok = json_tokener_new();
    json_object *obj = json_tokener_parse_ex(tok, data1, size);
    if (obj) {
        json_object_to_json_string_ext(obj, JSON_C_TO_STRING_PRETTY);
        json_object_put(obj);
    }
    json_tokener_free(tok);
    return 0;
}
```

**Compilación:**

```bash
clang-19 -g -fsanitize=address,fuzzer -I./json-c fuzz_json.c json-c/libjson-c.a -o fuzz_json
./fuzz_json corpus/ -max_total_time=300
```

### 3.8.2. 2.8.2 Principios de Diseño de Harness

| Principio | Descripción | Impacto |
|----------|------------|--------|
| Ejecución In-Process | LLVMFuzzerTestOneInput sin fork | 10-100x más rápido |
| Target Directo de API | Llamar funciones core | Evita parsing args |
| Maximización de Cobertura | Ejercitar múltiples caminos | Encuentra más bugs |
| Cleanup Apropiado | Liberar memoria | Previene OOM |
| Compatible Sanitizers | ASAN/UBSAN | Mejor detección |

### 3.8.3. Conclusiones del Capítulo 2

1. **El fuzzing encuentra vulnerabilidades reales** - No solo crashes teóricos.

2. **Fuzzing guiado por cobertura es poderoso** - AFL++, Honggfuzz, FuzzTest.

3. **Sanitizers son esenciales** - ASAN, UBSAN detectan bugs sutiles.

4. **El tiempo importa** - Muchos bugs requieren horas/días.

5. **Calidad del corpus afecta resultados** - Entradas válidas alcanzan código profundo.

6. **Parsers son objetivos principales** - Image, protocol, file format parsers.

**Preguntas de Discusión:**

1. ¿Por qué in-process es más rápido que wrappers basados en archivos?

2. ¿Cómo afecta la calidad del corpus a la penetración del fuzzer?
3. ¿Cuáles son riesgos de over-mocking en harnesses?
4. ¿Cómo determinar si fuzzing llegó a rendimientos decrecientes?
