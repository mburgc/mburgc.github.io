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
... (The rest of the chapter would follow the same structure)
