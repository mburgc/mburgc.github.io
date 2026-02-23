# Chapter 1: Introduction

## 1.1. Document Information

| Field           | Value                                   |
| --------------- | --------------------------------------- |
| Title           | Red Team Logbook                        |
| Version         | 1.0                                     |
| Classification  | Technical Reference Material            |
| Language        | English                                 |
| Purpose         | Educational and Defensive Research      |

## 1.2. Table of Contents

### 1.2.1. [Chapter 1: Vulnerability Classes](02-vulnerability-classes.md)

- **1.1 Memory Corruption Fundamentals**
  - 1.1.1 Stack Buffer Overflow
  - 1.1.2 Use-After-Free (UAF)
  - 1.1.3 Heap Buffer Overflow
  - 1.1.4 Out-of-Bounds Read
  - 1.1.5 Uninitialized Memory Use
  - 1.1.6 Reference Counting Errors
  - 1.1.7 Null Pointer Dereference
- **1.2 Logical Vulnerabilities and Race Conditions**
  - 1.2.1 Race Conditions
  - 1.2.2 TOCTOU Vulnerabilities
  - 1.2.3 Double‐Fetch Vulnerabilities
  - 1.2.4 Logical Flaws in Authentication
- **1.3 Type Confusion and Integers**
  - 1.3.1 Type Confusion in JIT
  - 1.3.2 Integer Overflow
  - 1.3.3 Parser Vulnerabilities
- **1.4 String and Format Vulnerabilities**
- **1.5 Driver and File System Vulnerabilities**
- **1.6 Impact Assessment and Classification**

### 1.2.2. [Chapter 2: Fuzzing](03-fuzzing.md)

- **2.1 Fuzzing Fundamentals**
- **2.2 AFL++ and Coverage-Guided Fuzzing**
- **2.3 FuzzTest and In‐Process Fuzzing**
- **2.4 Honggfuzz and Protocol Fuzzing**
- **2.5 Syzkaller and Kernel Fuzzing**

### 1.2.3. [Chapter 3: Patch Diffing](04-patch-diffing.md)

- **3.1 Patch Diffing Fundamentals**
- **3.2 Extracting Windows Patches**
- **3.3 Binary Diffing Tools**
- **3.4 Case Study Analysis**

### 1.2.4. [Chapter 4: Crash Analysis](05-crash-analysis.md)

- **4.1 Crash Analysis Fundamentals**
- **4.2 Debuggers and Configuration**
- **4.3 Memory Sanitizers**
- **4.4 Classification and Triage**
- **4.5 Exploitability Assessment**
