---
title: "Capítulo 03: Fuzzing"
chapter: 03
description: "Fuzzing - Manual de Explotación del Kernel de Linux"
---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
Observaciones
Mientras no es una vulnerabilidad per se, BYOVD es ampliamente usado en cadenas de explotación
y representa un riesgo significativo de abuso de drivers legítimos firmados.
### 2.6.
### 1.6 Evaluación de Impacto y Clasificación
Comprender cómo evaluar y clasificar vulnerabilidades por su impacto real y explotabilidad es fun‐
damental para la priorización de parches y respuesta a incidentes.
### 2.6.1.
Categorías de Impacto
Ejecución Remota de Código ﴾RCE﴿‐ Definición: Atacante puede ejecutar código arbitrario en el
sistema objetivo remotamente ‐ Impacto: Máxima severidad ‐ compromiso completo del sistema
posible ‐ Ejemplos: CVE‐2024‐27130 ﴾QNAP﴿, CVE‐2024‐2883 ﴾Chrome ANGLE﴿, CVE‐2023‐4863
﴾libWebP﴿
Escalada de Privilegios Local ﴾LPE﴿‐ Definición: Atacante con acceso limitado puede obtener
privilegios más altos ‐ Impacto: Alta severidad ‐ permite persistencia, evasión de defensas, movi‐
miento lateral ‐ Ejemplos: CVE‐2024‐26218 ﴾Windows Kernel TOCTOU﴿, CVE‐2022‐0847 ﴾Dirty Pipe﴿
Divulgación de Información ‐ Definición: Atacante puede leer datos a los que no debería tener
acceso ‐ Impacto: Media a Alta ‐ frecuentemente encadenada con otros bugs para bypass de ASLR
‐ Ejemplos: Fugas de format string, lecturas de memoria no inicializada
Denegación de Servicio ﴾DoS﴿‐ Definición: Atacante puede hacer un servicio no disponible sin
ganar ejecución de código ‐ Impacto: Baja a Media ‐ interrumpe disponibilidad sin comprometer
confidencialidad/integridad ‐ Ejemplos: CVE‐2024‐27316 ﴾HTTP/2 CONTINUATION﴿, bombas de
descompresión
### 2.6.2.
Factores de Explotabilidad
Factor
Bajo
Alto
Complejidad de Ataque
Requiere preparación
compleja
Explotable repetidamente
con mínimo esfuerzo
Vector de Ataque
Requiere acceso físico
Explotable remotamente
sobre red
Privilegios Requeridos
Requiere acceso
administrativo
Sin autenticación necesaria
Interacción de Usuario
Víctima debe realizar acción
Completamente
automatizado

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
### 2.6.3.
Sistema de Puntuación CVSS
Componentes del Score Base ﴾Cualidades Intrínsecas﴿: ‐ Vector de Ataque ﴾AV﴿: Red/Adyacente/Local/Físico
‐ Complejidad de Ataque ﴾AC﴿: Baja/Alta ‐ Privilegios Requeridos ﴾PR﴿: Ninguno/Bajo/Alto ‐ In‐
teracción de Usuario ﴾UI﴿: Ninguna/Requerida ‐ Alcance ﴾S﴿: Sin Cambio/Con Cambio ‐ Impacto
a Confidencialidad ﴾C﴿, Integridad ﴾I﴿, Disponibilidad ﴾A﴿: Ninguno/Bajo/Alto
Rangos de Score: | Rango | Severidad | |——‐|———–| | 0.0 | Ninguna | | 0.1‐3.9 | Baja | | 4.0‐6.9 |
Media | | 7.0‐8.9 | Alta | | 9.0‐10.0 | Crítica |
### 2.6.4.
Conclusiones del Capítulo 1
1. La corrupción de memoria sigue siendo prevalente: A pesar de décadas de investigación,
los bugs de corrupción de memoria continúan afectando software, especialmente en bases
de código C/C++.
2. La defensa en profundidad es esencial: Cada ejemplo real muestra atacantes evadiendo
múltiples mecanismos de protección ﴾DEP, ASLR, CET, safe‐linking﴿.
3. Las mitigaciones modernas elevan la barrera pero no eliminan el riesgo: Mientras tec‐
nologías como CET shadow stack y safe‐linking hacen la explotación más difícil, atacantes
determinados continúan encontrando bypasses.
4. Las causas raíz son similares, pero los contextos difieren: Bugs de stack, heap y UAF com‐
parten causas raíz comunes ﴾verificación inadecuada de límites, gestión de tiempo de vida﴿
pero requieren diferentes técnicas de explotación.
5. Los componentes legacy permanecen vulnerables: Vulnerabilidades de años de antigüedad
en parsers de office y manejadores de archivos continúan siendo explotadas debido a ciclos
de parcheo lentos.
6. Las vulnerabilidades lógicas no requieren corrupción de memoria: Bypasses de autentica‐
ción, fallas TOCTOU y primitivas de escritura arbitraria pueden ser igualmente impactantes.
7. User namespaces expanden la superficie de ataque: Muchas vulnerabilidades del kernel
se vuelven explotables desde contextos no privilegiados cuando user namespaces otorgan
capacidades como CAP_NET_ADMIN.

---

Capítulo 3
Fuzzing
El fuzzing es una técnica automatizada de descubrimiento de vulnerabilidades que ha encontrado
miles de bugs de seguridad críticos en software de producción. Este capítulo cubre los fundamentos
del fuzzing, herramientas clave y metodologías para encontrar vulnerabilidades.
### 3.1.
### 2.1 Fundamentos de Fuzzing
Qué es el Fuzzing
El fuzzing es una técnica de prueba de software que involucra proporcionar datos inválidos, inespe‐
rados o aleatorios como entrada a un programa. El objetivo es encontrar crashes, assertions fallidos,
fugas de memoria y otros comportamientos anómalos que puedan indicar vulnerabilidades de se‐
guridad.
Por Qué el Fuzzing es Efectivo
Automatización: Puede probar millones de entradas por hora
Cobertura: Explora casos extremos que las pruebas manuales nunca alcanzarían
Reproducibilidad: Las entradas que causan crashes se guardan para análisis
Escalabilidad: Puede ejecutarse continuamente durante días/semanas
Tipos de Fuzzing
Tipo
Descripción
Ejemplo
Caja Negra
Sin conocimiento del código interno
Mutación aleatoria de
entradas
Caja Blanca
Conocimiento completo del código
Ejecución simbólica
Caja Gris
Instrumentación de cobertura
AFL++, libFuzzer
Guiado por
Cobertura
Mide qué código se ejecuta
AFL++, Honggfuzz
Guiado por
Gramática
Conoce la estructura del formato
Syzkaller ﴾syscalls﴿

---

### CAPÍTULO 3. FUZZING
Bitácora Red Team
### 3.2.
### 2.2 AFL++ y Fuzzing Guiado por Cobertura
Descripción General
AFL++ ﴾American Fuzzy Lop Plus Plus﴿es uno de los fuzzers más efectivos y ampliamente utilizados.
Usa instrumentación de cobertura para guiar la mutación de entradas hacia nuevos caminos de
código.
Componentes Clave de AFL++
1. Instrumentación de Cobertura: Compilador modificado que inserta código para rastrear qué
bloques básicos se ejecutan
2. Motor de Mutación: Aplica transformaciones inteligentes a las entradas
3. Gestión de Corpus: Mantiene conjunto mínimo de entradas que maximizan cobertura
4. Detección de Crashes: Identifica y guarda entradas que causan fallos
Caso de Estudio: AFL++ Encontrando CVE‐2024‐47606 ﴾GStreamer﴿
Campo
Detalle
Método de Descubrimiento
Campañas de fuzzing continuas con AFL++
Objetivo
Demuxer QuickTime de GStreamer ﴾qtdemux﴿
Superficie de Ataque
Archivos MP4/MOV procesados por navegadores,
reproductores, apps de mensajería
El Proceso de Descubrimiento
1. Corpus de Semillas: Archivos MP4 válidos de datasets públicos
2. Instrumentación: Compilado con AFL++ y AddressSanitizer
3. Estrategia de Mutación: Structure‐aware ﴾entendiendo átomos MP4﴿
4. Resultado: Crash de heap buffer overflow después de ~48 horas de fuzzing
Por Qué el Fuzzing lo Encontró
Combinación de Entrada Rara: Requería valores específicos de tamaño de extensión Theora
que subdesbordaran
Limitación de Análisis Estático: Conversión signed‐to‐unsigned enterrada en lógica de par‐
sing compleja
Falla de Code Review: Aritmética de enteros parecía correcta sin considerar valores negativos
Brecha de Testing Automatizado: Pruebas unitarias no cubrían extensiones Theora malfor‐
madas
Insight Clave
El fuzzing sobresale en encontrar casos extremos en parsers complejos que los humanos nunca
probarían manualmente. La combinación de: ‐ Mutación guiada por cobertura ﴾AFL++ explorando
nuevos caminos de código﴿‐ AddressSanitizer ﴾detectando corrupción de memoria inmediatamen‐
te﴿‐ Fuzzing persistente ﴾ejecutándose por días/semanas﴿
…lo hace más efectivo que las pruebas manuales para esta clase de vulnerabilidad.

---

### CAPÍTULO 3. FUZZING
Bitácora Red Team
### 3.3.
### 2.3 FuzzTest y Fuzzing In‐Process
Descripción General
FuzzTest es un framework de fuzzing in‐process estilo unit‐test de Google que integra fuzzing con
GoogleTest. Es ideal para fuzzear funciones C++ individuales directamente.
Características Clave
Integración con GoogleTest: Se escribe TEST y FUZZ_TEST lado a lado en el mismo archivo
Fuzzing guiado por cobertura bajo el capó: Estilo libFuzzer pero oculta código boilerplate
de harness
Ideal para bibliotecas y lógica core: Parsers, decoders, helpers de crypto
Perfecto para CI: El mismo binario puede ejecutar tests determinísticos rápidos o campañas
de fuzz largas
Ventajas de FuzzTest
Aspecto
FuzzTest
AFL++/Honggfuzz
Target
Funciones individuales
Programas completos
Integración
GoogleTest nativo
Harness separado
Uso
Unit tests →fuzz tests
Binarios standalone
### CI/CD
Excelente
Requiere setup adicional
Observaciones
FuzzTest es particularmente útil para equipos que ya tienen suites de unit tests y quieren añadir
fuzzing de manera incremental a sus flujos de trabajo existentes.
### 3.4.
### 2.4 Honggfuzz y Fuzzing de Protocolos
Descripción General
Honggfuzz es un fuzzer desarrollado por Google con soporte excelente para fuzzing de protocolos
de red y aplicaciones multi‐hilo. Ofrece cobertura asistida por hardware usando Intel PT.
Características Distintivas
Multi‐hilo nativo: Maneja targets multi‐hilo sin problemas
Cobertura Hardware: Usa Intel Processor Trace para cobertura de bajo overhead
Modo Persistente: Mantiene el proceso vivo entre iteraciones
Detección de Feedback: Detecta crashes, timeouts, memory errors
Caso de Estudio: Fuzzing de Implementaciones TLS

---

### CAPÍTULO 3. FUZZING
Bitácora Red Team
Aspecto
Desafío
Solución
Protocolo Stateful
Debe completar handshake
antes de llegar a lógica
profunda
Harness que simula estado de
conexión
Operaciones Criptográficas
Valores aleatorios, firmas,
MACs
Seeds con datos criptográficos
válidos
Múltiples Versiones
### TLS 1.0, 1.1, 1.2, 1.3
Configurar target para versión
específica
Extensiones
ALPN, SNI, session tickets
Corpus con variedad de
extensiones
Bugs Reales Encontrados por Fuzzing de Protocolos
De OpenSSL y otras implementaciones TLS: ‐ Buffer overflows en parsing de certificados: Manejo
de extensiones X.509 ‐ Use‐after‐free en reanudación de sesión: Gestión de lifetime de tickets
‐ Integer overflows en capa de registro: Cálculos de longitud ‐ Bugs de confusión de estado:
Ordenamiento inesperado de mensajes
Observaciones
El fuzzing de protocolos es más desafiante que el fuzzing de formatos de archivo debido a la natura‐
leza stateful de los protocolos, pero es altamente efectivo para encontrar bugs en implementaciones
de red.
### 3.5.
### 2.5 Syzkaller y Fuzzing de Kernel
Descripción General
Syzkaller es un fuzzer de syscalls del kernel desarrollado por Google. Es responsable de encontrar
miles de bugs del kernel Linux y se usa activamente en el desarrollo del kernel.
Características Clave
Conocimiento de Syscalls: Entiende las signatures de syscalls y sus argumentos
Generación de Programas: Crea secuencias de syscalls válidas y semi‐válidas
Gestión de VMs: Ejecuta targets en VMs para aislamiento
Reproducción: Genera programas C reproducibles para crashes encontrados
Arquitectura de Syzkaller
┌─────────────────────────────────────────────────────────────┐
│
Manager (syz-manager)
│
│
- Coordina múltiples VMs
│
│
- Gestiona corpus de programas
│
│
- Rastrea cobertura de código
│
└─────────────────────────────────────────────────────────────┘
│

---

### CAPÍTULO 3. FUZZING
Bitácora Red Team
┌────────────────────┼────────────────────┐
▼
▼
▼
┌─────────┐
┌─────────┐
┌─────────┐
│
### VM1
│
│
### VM2
│
│
### VM3
│
│fuzzer
│
│fuzzer
│
│fuzzer
│
│executor│
│executor│
│executor│
└─────────┘
└─────────┘
└─────────┘
Subsistemas del Kernel Frecuentemente Fuzzeados
Subsistema
Superficie de Ataque
Bugs Comunes
Netfilter
Reglas de firewall, NAT
UAF, race conditions
io_uring
Async I/O
Race conditions, memory leaks
### USB
Descriptores de dispositivo
OOB reads, tipo confusions
Filesystems
Imágenes de disco
Integer overflows, NULL derefs
Network
Paquetes, sockets
Buffer overflows, state confusion
Caso de Estudio: Syzkaller y CVE‐2022‐32250 ﴾Netfilter UAF﴿
Campo
Detalle
Target
net/netfilter/nf_tables_api.c
Tiempo de Descubrimiento
~72 horas desde introducción del código
Causa Raíz
Error de conteo de referencias en expresiones stateful
Impacto
Escalada de privilegios local a root
Cómo Syzkaller Encontró el Bug:
Syzkaller genera secuencias de syscalls que interactúan con el subsistema netfilter:
socket(AF_NETLINK, SOCK_RAW, NETLINK_NETFILTER) →fd
sendmsg(fd, { type: NFT_MSG_NEWTABLE, ... })
sendmsg(fd, { type: NFT_MSG_NEWCHAIN, data: [chain_with_stateful_expr] })
sendmsg(fd, { type: NFT_MSG_NEWRULE, data: [rule_that_frees_expr] })
// Resultado: Uso de expresión liberada →Crash UAF
Por Qué Syzkaller lo Encontró:
1. Cobertura de Syscalls: Prueba todas las operaciones netfilter sistemáticamente
2. Exploración de Secuencias: Prueba millones de ordenamientos de syscalls
3. Rastreo de Estado: Mantiene estado del kernel a través de operaciones
4. Integración KASAN: Detección inmediata de corrupción de memoria
5. Reproducibilidad: Genera reproducers C mínimos para desarrolladores
Impacto Real: El bug permitía escalada de privilegios local desde cualquier usuario a root en siste‐
mas con user namespaces no privilegiados ﴾default en Ubuntu, Debian﴿. Exploit público disponible
en semanas.
Observaciones

---

### CAPÍTULO 3. FUZZING
Bitácora Red Team
Syzkaller ha transformado la seguridad del kernel Linux al encontrar bugs de manera sistemática
antes de que sean explotados. Es una herramienta esencial para cualquier investigador de seguridad
de kernel.
### 3.6.
### 2.6 Configuración Práctica de AFL++
Instalación Paso a Paso
# Instalar dependencias de compilación
sudo apt update
sudo apt install -y build-essential gcc-13-plugin-dev cpio python3-dev \
libcapstone-dev pkg-config libglib2.0-dev libpixman-1-dev \
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
Compilación de Target con Instrumentación
# Compilar programa C/C++ con instrumentación AFL++
CC=/usr/local/bin/afl-clang-fast \
CXX=/usr/local/bin/afl-clang-fast++ \
cmake ..
make -j$(nproc)
# Habilitar sanitizers para mejor detección de bugs

---

### CAPÍTULO 3. FUZZING
Bitácora Red Team
export AFL_USE_ASAN=1
export AFL_USE_UBSAN=1
export ASAN_OPTIONS="detect_leaks=1:abort_on_error=1:symbolize=1"
Ejecución del Fuzzer
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
### 3.7.
### 2.7 Análisis de Crashes y Evaluación de Explotabilidad
El análisis de crashes es el proceso de determinar si un crash descubierto por fuzzing represen‐
ta una vulnerabilidad explotable. Esta sección cubre las herramientas y metodologías para triage
sistemático de crashes.
Árbol de Decisión para Análisis de Crashes
┌─────────────────────────────────────────────────────────────┐
│
### CRASH RECIBIDO
│
└─────────────────────────────────────────────────────────────┘
│
▼
┌───────────────────────┐
│¿Código fuente
│
│
disponible?
│
└───────────────────────┘

---

### CAPÍTULO 3. FUZZING
Bitácora Red Team
│
│
Sí
No
│
│
▼
▼
┌─────────────────────┐
┌─────────────────────┐
│Recompilar con
│
│Usar depurador
│
### │ASAN + UBSAN
│
│(GDB/WinDbg)
│
└─────────────────────┘
└─────────────────────┘
│
│
▼
▼
┌─────────────────────┐
┌─────────────────────┐
│Ejecutar crash
│
│Analizar registros
│
│Obtener reporte
│
│y memoria
│
└─────────────────────┘
└─────────────────────┘
│
│
└────────┬───────────┘
▼
┌───────────────────────────┐
│Clasificar vulnerabilidad │
│con CASR
│
└───────────────────────────┘
### 3.7.1.
### 2.7.1 Caso de Estudio: Análisis de Heap Buffer Overflow
Escenario: El fuzzing descubrió un crash en un parser de imágenes. Analicemos paso a paso.
Código Vulnerable:
// vuln_parser.c - Parser de imágenes vulnerable
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
void build_huffman_table(uint8_t *input, size_t size) {
if (size < 8) return;
uint32_t table_size = *(uint32_t*)input;
// Controlado por atacante
uint8_t *codes = input + 4;
uint8_t *table = malloc(256);
// Asignación fija de 256 bytes
// VULNERABILIDAD: Sin verificación de límites en table_size
// Puede escribir más allá del búfer de 256 bytes
memcpy(table, codes, table_size);
// ¡Heap buffer overflow!

---

### CAPÍTULO 3. FUZZING
Bitácora Red Team
printf("Built Huffman table with
%u codes\n", table_size);
free(table);
}
Compilación con ASAN:
clang-19 -g -O0 -fsanitize=address -o vuln_parser_asan vuln_parser.c
Creación de Input Malicioso:
#!/usr/bin/env python3
import struct
# table_size = 512 (causa overflow de 256 bytes)
payload = struct.pack('<I', 512)
# Tamaño: 512 bytes
payload += b'A' * 512
# Datos de overflow
with open('crash_heap_overflow.bin', 'wb') as f:
f.write(payload)
Salida de ASAN:
==37160==ERROR: AddressSanitizer: heap-buffer-overflow on address
0x511000000140 at pc 0x56d6a37d0f62 bp 0x7ffd9f024440 sp 0x7ffd9f023c00
WRITE of size 512 at 0x511000000140 thread T0
#0 0x56d6a37d0f61 in __asan_memcpy
#1 0x56d6a38147f5 in build_huffman_table vuln_parser.c:16:5
#2 0x56d6a38148fe in main vuln_parser.c:37:5
0x511000000140 is located 0 bytes after 256-byte region
[0x511000000040,0x511000000140) allocated by thread T0 here:
#1 0x56d6a38147df in build_huffman_table vuln_parser.c:12:22
Interpretación del Reporte ASAN:
Campo
Valor
Significado
Tipo de Bug
heap-buffer-overflow
Desbordamiento de heap
Operación
WRITE of size 512
Escribiendo 512 bytes
Ubicación
vuln_parser.c:16
Línea del bug
Asignación
256‐byte buffer at line 12
Búfer asignado
Overflow
512 ‐ 256 = 256 bytes
Cantidad de overflow
Clasificación de Explotabilidad:
# Usar CASR para clasificación automática
casr-san --stdout -- ./vuln_parser_asan crash_heap_overflow.bin
# Resultado esperado:
# "Type": "EXPLOITABLE",
# "ShortDescription": "heap-buffer-overflow(write)",
Evaluación de Explotabilidad: EXPLOITABLE

---

### CAPÍTULO 3. FUZZING
Bitácora Red Team
Razonamiento: 1. Atacante controla tamaño: table_size viene del input 2. Atacante controla
datos: codes array content 3. Corrupción de heap posible: Puede sobrescribir objetos adyacentes
4. Ruta de explotación: Overflow →Corromper puntero de función o vtable →Hijack de control
flow →RCE
Ejemplo Real Similar: CVE‐2023‐4863 ﴾libWebP Heap Buffer Overflow﴿
### 3.7.2.
### 2.7.2 Caso de Estudio: Análisis de Use‐After‐Free
Código Vulnerable:
// vuln_uaf.c - Use-After-Free vulnerability
typedef struct {
char *name;
void (*process)(void);
// Puntero de función
} Handler;
Handler *handler = NULL;
void register_handler(char *name) {
handler = malloc(sizeof(Handler));
handler->name = strdup(name);
handler->process = default_handler;
}
void unregister_handler(void) {
if (handler) {
free(handler->name);
free(handler);
// BUG: ¡Debería establecer handler = NULL aquí!
}
}
void call_handler(void) {
if (handler) {
handler->process();
// UAF: handler ya fue liberado
}
}
Salida de ASAN:
==38664==ERROR: AddressSanitizer: heap-use-after-free on address
0x502000000010 at pc 0x617b2245a953 bp 0x7ffe92f7c160 sp 0x7ffe92f7c158
READ of size 8 at 0x502000000010 thread T0
#0 0x617b2245a952 in call_handler vuln_uaf.c:44:50
0x502000000010 freed by thread T0 here:
#1 0x617b2245a86a in unregister_handler vuln_uaf.c:29:9

---

### CAPÍTULO 3. FUZZING
Bitácora Red Team
previously allocated by thread T0 here:
#1 0x617b2245a7a5 in register_handler vuln_uaf.c:21:15
Estrategia de Explotación:
┌─────────────────────────────────────────────────────────────┐
│
### EXPLOTACIÓN UAF
│
├─────────────────────────────────────────────────────────────┤
│
│
│
### 1. LIBERACIÓN
│
│
unregister_handler() libera handler
│
│
pero handler sigue apuntando a memoria liberada
│
│
│
│
### 2. HEAP GROOMING
│
│
Atacante realiza asignaciones del mismo tamaño
│
│
for (i = 0; i < 1000; i++) {
│
│
Handler *fake = malloc(sizeof(Handler));
│
│
fake->process = evil_handler;
│
│
}
│
│
│
│
### 3. RECLAMAR MEMORIA
│
│
Una de las nuevas asignaciones ocupa la memoria
│
│
liberada, sobrescribiendo handler->process
│
│
│
│
### 4. DISPARAR UAF
│
│
call_handler() →handler->process()
│
│
Ejecuta evil_handler en lugar de default_handler
│
│
│
│
5. RESULTADO: Ejecución de código arbitrario
│
└─────────────────────────────────────────────────────────────┘
Evaluación de Explotabilidad: EXPLOITABLE
Nota Importante: Las herramientas automáticas como CASR pueden clasificar esto como
NOT_EXPLOITABLE porque ASAN detecta la lectura del puntero de función antes de la llamada. El
análisis manual demuestra que el control de flujo es hijackable.
### 3.7.3.
### 2.7.3 Caso de Estudio: Integer Overflow →Heap Corruption
Código Vulnerable:
// vuln_intoverflow.c - Integer overflow leading to heap corruption
void process_image(uint32_t width, uint32_t height, uint8_t *data) {
// Integer overflow: 65536 * 65536 = 0 (32-bit overflow)

---

### CAPÍTULO 3. FUZZING
Bitácora Red Team
size_t pixel_count = width * height;
size_t buffer_size = pixel_count * 4;
printf("Allocating
%zu bytes for
%ux %u image\n",
buffer_size, width, height);
uint8_t *buffer = malloc(buffer_size);
// malloc(0) = tiny buffer
// Loop usa bounds "correctos" pero buffer es tiny
for (size_t i = 0; i < (size_t)width * height; i++) {
buffer[i * 4] = data[i
% 1024];
// Massive overflow!
}
free(buffer);
}
int main(void) {
// Dimensiones controladas por atacante
uint32_t width = 0x10000;
// 65536
uint32_t height = 0x10000;
// 65536
// width * height = 0x100000000 →overflow a 0
uint8_t fake_data[1024];
memset(fake_data, 'A', sizeof(fake_data));
process_image(width, height, fake_data);
return 0;
}
Salida de UBSAN + ASAN:
vuln_intoverflow.c:7:32: runtime error: unsigned integer overflow:
65536 * 65536 cannot be represented in type 'uint32_t'
==39011==ERROR: AddressSanitizer: heap-buffer-overflow on address
0x502000000014 at pc 0x5fa5104bd933
WRITE of size 1 at 0x502000000014 thread T0
#0 0x5fa5104bd932 in process_image vuln_intoverflow.c:17:23
0x502000000014 is located 3 bytes after 1-byte region
[0x502000000010,0x502000000011) allocated by:
#1 malloc() returned 1 byte (due to malloc(0))
Cadena de Explotación:
┌───────────────────────────────────────────────────────────┐
│
1. Integer Overflow
│
│
width * height = 0x10000 * 0x10000 = 0
│
│
(overflow de 32 bits, envuelve a 0)
│

---

### CAPÍTULO 3. FUZZING
Bitácora Red Team
│
│
│
2. Bajo-allocación
│
│
malloc(0) asigna chunk tiny
│
│
│
│
3. Loop con bounds originales
│
│
Loop itera 4 mil millones de veces
│
│
(usando valor sin overflow de 64-bit)
│
│
│
│
4. Heap Corruption
│
│
Escribe mucho más allá del buffer asignado
│
│
Corrompe metadatos de heap y objetos adyacentes
│
└───────────────────────────────────────────────────────────┘
Evaluación de Explotabilidad: EXPLOITABLE
Ejemplo Real Similar: CVE‐2024‐38063 ﴾Windows TCP/IP Integer Underflow RCE﴿
### 3.8.
### 2.8 Desarrollo de Harnesses de Fuzzing
Un harness de fuzzing es el código que conecta el fuzzer con el target API. Un harness bien diseñado
es crítico para fuzzing efectivo.
Harness Malo vs Harness Bueno:
// HARNESS MALO: Lento, ineficiente
int main(int argc, char **argv) {
FILE *f = fopen(argv[1], "rb");
// I/O de archivo cada iteración
// ... leer archivo ...
// ... llamar API target ...
fclose(f);
return 0;
}
// HARNESS BUENO: Rápido, in-process
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
// Buffer de memoria directo, sin I/O
// Se llama miles de veces por segundo en el mismo proceso
target_api(data, size);
return 0;
}
### 3.8.1.
### 2.8.1 Ejemplo: Harness para Parser JSON
// fuzz_json.c - Harness para fuzzing de json-c
#include <json-c/json.h>