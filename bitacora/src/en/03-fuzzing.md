# Chapter 3: Fuzzing

Fuzzing is an automated vulnerability discovery technique that has found thousands of critical security bugs in production software. This chapter covers the fundamentals of fuzzing, key tools, and methodologies for finding vulnerabilities.

## 3.1. 2.1 Fuzzing Fundamentals

**What is Fuzzing?**

Fuzzing is the process of feeding a program with malformed, unexpected, or random data in an attempt to provoke a crash or anomalous behavior. It is a form of black-box or gray-box testing that does not require access to the source code.

**Types of Fuzzers:**

-   **Dumb Fuzzers:** Generate random inputs without knowledge of the input format. They are simple but inefficient.
-   **Smart Fuzzers:** Have knowledge of the input format and generate inputs that are more likely to cause errors.
-   **Coverage-Guided Fuzzers:** (The most common today) Use instrumentation to track which parts of the code are executed with a given input. Then, they mutate the inputs to explore new code paths.

## 3.2. 2.2 AFL++ and Coverage-Guided Fuzzing

AFL++ is a state-of-the-art coverage-guided fuzzer that has found a large number of vulnerabilities in real-world software.

**How it Works:**

1.  **Instrumentation:** The source code is compiled with special instrumentation that records code coverage.
2.  **Initial Corpus:** The fuzzer starts with a set of valid test inputs (the corpus).
3.  **Mutation:** AFL++ mutates the corpus inputs in various ways (bit flipping, arithmetic, etc.).
4.  **Execution:** The instrumented program is run with the mutated input.
5.  **Analysis:** If the mutated input explores a new code path, it is added to the corpus. If it causes a crash, it is saved for analysis.

## 3.3. 2.3 FuzzTest and In-Process Fuzzing

FuzzTest is an in-process fuzzing framework from Google. Unlike AFL++, which runs the program in a separate process for each input, FuzzTest runs the fuzzer within the same process as the code being tested. This can be much faster for certain types of applications.

## 3.4. 2.4 Honggfuzz and Protocol Fuzzing

Honggfuzz is another popular coverage-guided fuzzer. It is known for its performance and advanced features, such as persistent fuzzing and network protocol fuzzing.

## 3.5. 2.5 Syzkaller and Kernel Fuzzing

Syzkaller is a specialized fuzzer for finding vulnerabilities in operating system kernels. It uses a system call description language to generate programs that exercise the kernel interfaces. Syzkaller has been extremely successful in finding vulnerabilities in the Linux kernel.

## 3.6. 2.6 Practical AFL++ Configuration

### Step-by-Step Installation

```bash
# Install build dependencies
sudo apt update
sudo apt install -y build-essential gcc-13-plugin-dev cpio python3-dev 
    libcapstone-dev pkg-config libglib2.0-dev libpixman-1-dev 
    automake autoconf python3-pip ninja-build cmake git wget meson

# Install LLVM 19 (check for the latest version at https://apt.llvm.org/)
wget https://apt.llvm.org/llvm.sh
chmod +x llvm.sh
sudo ./llvm.sh 19 all

# Verify LLVM installation
clang-19 --version
llvm-config-19 --version

# Install Rust (required for some AFL++ components)
curl --proto '=https' --tlsv1.2 -sSf "https://sh.rustup.rs" | sh
source ~/.cargo/env

# Compile and install AFL++
mkdir -p ~/soft && cd ~/soft
git clone --depth 1 https://github.com/AFLplusplus/AFLplusplus.git
cd AFLplusplus
make distrib
sudo make install

# Verify installation
which afl-fuzz
afl-fuzz --version
```

### Target Compilation with Instrumentation

```bash
# Compile C/C++ program with AFL++ instrumentation
CC=/usr/local/bin/afl-clang-fast 
CXX=/usr/local/bin/afl-clang-fast++ 
cmake ..
make -j$(nproc)

# Enable sanitizers for better bug detection
export AFL_USE_ASAN=1
export AFL_USE_UBSAN=1
export ASAN_OPTIONS="detect_leaks=1:abort_on_error=1:symbolize=1"
```

### Fuzzer Execution

```bash
# Configure the system for optimal fuzzing
echo core | sudo tee /proc/sys/kernel/core_pattern
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Create seed corpus
mkdir -p seeds
for i in {0..4}; do
    dd if=/dev/urandom of=seeds/seed_$i bs=64 count=10 2>/dev/null
done

# Run the fuzzer
afl-fuzz -i seeds/ -o findings/ -m none -d -- ./target_binary @@

# Parallel fuzzing (multiple instances)
# Terminal 1: Master instance
afl-fuzz -i seeds/ -o findings/ -M Master -- ./target @@

# Terminal 2+: Slave instances
afl-fuzz -i seeds/ -o findings/ -S Slave1 -- ./target @@
afl-fuzz -i seeds/ -o findings/ -S Slave2 -- ./target @@

# Check status
afl-whatsup findings/
```

## 3.7. 2.7 Crash Analysis and Exploitability Assessment

Crash analysis is the process of determining whether a crash discovered by fuzzing represents an exploitable vulnerability. This section covers the tools and methodologies for systematic crash triage.

### Decision Tree for Crash Analysis

```
                      CRASH RECEIVED
                            │
                            ▼
                  ┌───────────────────────┐
                  │ Source code           │
                  │   available?          │
                  └───────────────────────┘
                       │                    │
                      Yes                   No
                       │                    │
                       ▼                    ▼
         ┌─────────────────────┐    ┌─────────────────────┐
         │ Recompile with      │    │ Use debugger        │
         │ ASAN + UBSAN        │    │ (GDB/WinDbg)          │
         └─────────────────────┘    └─────────────────────┘
                       │                    │
                       ▼                    ▼
         ┌─────────────────────┐    ┌─────────────────────┐
         │ Execute crash       │    │ Analyze registers   │
         │ Get report          │    │ and memory            │
         └─────────────────────┘    └─────────────────────┘
                       │                    │
                       └────────┬───────────┘
                                ▼
                  ┌───────────────────────────┐
                  │ Classify vulnerability    │
                  │ with CASR                 │
                  └───────────────────────────┘
```

### 3.7.1. 2.7.1 Case Study: Heap Buffer Overflow Analysis

**Scenario:** Fuzzing discovered a crash in an image parser. Let's analyze step by step.

**Vulnerable Code:**

```c
// vuln_parser.c - Vulnerable image parser
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

**ASAN Output:**

```
==37160==ERROR: AddressSanitizer: heap-buffer-overflow on address
0x511000000140 at pc 0x56d6a37d0f62 bp 0x7ffd9f024440 sp 0x7ffd9f023c00
WRITE of size 512 at 0x511000000140 thread T0
```

**Interpretation:**

| Field | Value | Meaning |
|-------|-------|----------|
| Bug Type | heap-buffer-overflow | Heap overflow |
| Operation | WRITE of size 512 | Writing 512 bytes |
| Location | vuln_parser.c:16 | Bug line |
| Allocation | 256-byte buffer | Buffer allocated |
| Overflow | 512 - 256 = 256 | Overflow amount |

**Assessment: EXPLOITABLE** - Attacker controls both overflow size and data.

### 3.7.2. 2.7.2 Case Study: Use-After-Free Analysis

**Vulnerable Code:**

```c
typedef struct {
    char *name;
    void (*process)(void);
} Handler;

Handler *handler = NULL;

void unregister_handler(void) {
    if (handler) {
        free(handler);
        // BUG: Missing handler = NULL
    }
}

void call_handler(void) {
    if (handler) {
        handler->process(); // UAF!
    }
}
```

**Exploitation Strategy:**
1. Free handler
2. Heap grooming: allocate objects of same size
3. Reclaim freed memory with controlled data
4. Trigger UAF → code execution

**Assessment: EXPLOITABLE**

### 3.7.3. 2.7.3 Case Study: Integer Overflow → Heap Corruption

**Vulnerable Code:**

```c
void process_image(uint32_t width, uint32_t height, uint8_t *data) {
    size_t buffer_size = width * height * 4; // overflow!
    uint8_t *buffer = malloc(buffer_size);
    for (size_t i = 0; i < width * height; i++) {
        buffer[i] = data[i]; // massive overflow
    }
}
```

**Chain:** Integer overflow → malloc(0) → loop with large bounds → heap corruption

**Assessment: EXPLOITABLE**

## 3.8. 2.8 Developing Fuzzing Harnesses

### 3.8.1. 2.8.1 Example: JSON Parser Harness

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

**Compilation:**

```bash
clang-19 -g -fsanitize=address,fuzzer -I./json-c fuzz_json.c json-c/libjson-c.a -o fuzz_json
./fuzz_json corpus/ -max_total_time=300
```

### 3.8.2. 2.8.2 Harness Design Principles

| Principle | Description | Impact |
|-----------|------------|--------|
| In-Process Execution | LLVMFuzzerTestOneInput without fork | 10-100x faster |
| Direct API Target | Call core functions | Avoids arg parsing |
| Coverage Maximization | Exercise multiple paths | Finds more bugs |
| Proper Cleanup | Free memory | Prevents OOM |
| Sanitizer Compatible | ASAN/UBSAN | Better detection |

### 3.8.3. Chapter 2 Conclusions

1. **Fuzzing finds real vulnerabilities** - Not just theoretical crashes.

2. **Coverage-guided fuzzing is powerful** - AFL++, Honggfuzz, FuzzTest.

3. **Sanitizers are essential** - ASAN, UBSAN detect subtle bugs.

4. **Time matters** - Many bugs require hours/days.

5. **Corpus quality affects results** - Valid inputs reach deep code.

6. **Parsers are primary targets** - Image, protocol, file format parsers.

**Discussion Questions:**

1. Why is in-process faster than file-based wrappers?

2. How does corpus quality affect fuzzer penetration?
3. What are the risks of over-mocking in harnesses?
4. How to determine if fuzzing has reached diminishing returns?
