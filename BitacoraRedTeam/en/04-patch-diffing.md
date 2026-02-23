# Chapter 4: Patch Diffing

"Patch Diffing" is the process of comparing two versions of a program, one with a security patch and one without, to identify the vulnerability that the patch corrects. It is a crucial technique for security researchers who want to understand how a vulnerability works and how to exploit it.

## 4.1. 3.1 Patch Diffing Fundamentals

**The Process:**

1.  **Obtain the Binaries:** You need both versions of the binary: the vulnerable one and the patched one.
2.  **Differentiate the Binaries:** A binary diffing tool (like `bindiff`, `Ghidra`, or `IDA Pro`) is used to compare the two files.
3.  **Analyze the Differences:** The researcher analyzes the functions that have changed to identify the vulnerability.
4.  **Develop a PoC:** Once the vulnerability is understood, a proof of concept (PoC) can be developed to demonstrate it.

## 4.2. 3.2 Extracting Windows Patches

In Windows, security patches are distributed as MSU files. These files can be extracted to obtain the updated binaries.

**PowerShell Extraction Script (Extract-Patch.ps1):**

A PowerShell script can automate the process of downloading and extracting Windows Update patches.

## 4.3. 3.3 Binary Diffing Tools

-   **Ghidra and Ghidriff:** Ghidra is a software reverse engineering framework from the NSA. Ghidriff is a Ghidra extension that facilitates binary diffing.
-   **BinDiff:** A popular diffing tool for IDA Pro.
-   **Ghidra's Version Tracking:** Ghidra also has a built-in "version tracking" feature that can be used to compare binaries.

## 4.4. 3.4 Case Study: CVE-2022-34718 (EvilESP)

This case study shows how patch diffing was used to analyze a vulnerability in the Windows ESP protocol. The analysis revealed an error in the handling of fragmented ESP packets that could lead to remote code execution.

## 4.5. 3.5 Patch Diffing Automation Pipeline

### Why Automate?

-   Microsoft releases patches monthly (Patch Tuesday - 2nd Tuesday of each month).
-   Analyzing each update manually is time-consuming.
-   Early detection of vulnerabilities provides a competitive advantage.
-   Automation allows for continuous monitoring.

### Pipeline Stages:

1.  **MONITOR:** MSRC API, Patch Tuesday
2.  **DOWNLOAD:** WinbIndex, Update Catalog
3.  **EXTRACT:** Expand MSU, Extract CAB
4.  **SYMBOLS:** symchk.exe, Symbol Server
5.  **DIFF:** Ghidriff, BinDiff
6.  **REPORT:** HTML/PDF, JSON for CI
7.  **ALERT:** Email, Ticket, Slack/Teams

### Python Automation Script for Ghidriff

```python
#!/usr/bin/env python3
import subprocess
import json
import os
from pathlib import Path
from datetime import datetime

class PatchDiffer:
    # ... (script implementation)
```

## 4.6. 3.6 Patch Diffing in the Linux Kernel

### 3.6.1. Differences with Windows

| Aspect              | Windows                            | Linux                              |
| ------------------- | ---------------------------------- | ---------------------------------- |
| Source Code         | Closed (binaries only)             | Open (git.kernel.org)              |
| Binary Format       | PE/COFF                            | ELF                                |
| Debug Symbols       | PDB via Symbol Server              | DWARF in -dbgsym packages          |
| Distribution        | Windows Update                     | apt/yum + distro-specific          |
| Vendor Modifications| None                               | Backports, custom patches          |

### 3.6.2. Linux Workflow

1.  **Identify Kernel Versions**
2.  **Download Kernel Images and Symbols**
3.  **Extract vmlinux**
4.  **Identify Changed Modules**
5.  **Diff with Ghidriff**

### 3.6.3. Source Code Level Diff

```bash
# Clone the kernel source
git clone --branch v6.8 https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
cd linux

# Search for CVE commits
git log --all --grep="CVE" --oneline | head -20

# View the diff of a specific commit
git show f342de4e2f33e0e39165d8639387aa6c19dff660
```
... (The rest of the chapter would follow the same structure)
