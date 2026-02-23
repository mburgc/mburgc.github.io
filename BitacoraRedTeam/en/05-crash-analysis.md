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

-   **WinDbg Preview for Windows:** The standard debugger for Windows.
-   **GDB + Pwndbg for Linux:** GDB with the Pwndbg extension for vulnerability analysis.
-   **Dump Collection:** Configure the system to save crash dumps.

## 5.3. 4.3 Memory Sanitizers

-   **AddressSanitizer (ASAN):** Detects memory errors such as buffer overflows and use-after-free.
-   **UndefinedBehaviorSanitizer (UBSAN):** Detects undefined behavior in C/C++.
-   **MemorySanitizer (MSAN):** Detects the use of uninitialized memory.
-   **ThreadSanitizer (TSAN):** Detects race conditions.

## 5.4. 4.4 Automated Classification and Triage

-   **CASR - Crash Analysis and Severity Reporter:** A suite of tools for automated crash classification.
-   **Crash Deduplication:** Grouping similar crashes to identify unique bugs.
-   **Crash Minimization:** Reducing a test case that causes a crash to the smallest possible input.

## 5.5. 4.5 Reachability Analysis

-   **DynamoRIO + drcov:** A binary instrumentation framework for generating code coverage.
-   **Intel Processor Trace (PT):** A hardware feature for tracing program execution.
-   **Frida:** A dynamic instrumentation framework for real-time tracing.
-   **rr - Record and Replay Debugging:** Records execution for deterministic replay.

## 5.6. 4.6 PoC (Proof of Concept) Development

-   **pwntools:** A Python framework for developing exploits and PoCs.

### Basic PoC - Stack Buffer Overflow

```python
#!/usr/bin/env python3
from pwn import *

# ... (PoC code)
```

## 5.7. 4.7 Capstone Project: Complete Analysis Pipeline

Scenario: Analyze crashes from a vulnerable test suite, classify the bugs, and create PoCs.

### Binary with ROP Gadgets

A special binary with ROP (Return-Oriented Programming) gadgets is provided to facilitate exploitation.

### Complete Exploit

It is demonstrated how to build a ROP chain to call a `win()` or `spawn_shell()` function.

```python
#!/usr/bin/env python3
from pwn import *

# ... (exploit code)
```
... (The rest of the chapter would follow the same structure)
