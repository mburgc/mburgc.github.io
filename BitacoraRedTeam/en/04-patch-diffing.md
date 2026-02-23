# Chapter 4: Patch Diffing

"Patch Diffing" is the process of comparing two versions of a program, one with a security patch and one without, to identify the vulnerability that the patch corrects. It is a crucial technique for security researchers who want to understand how a vulnerability works and how to exploit it.

## 4.1. Patch Diffing Fundamentals

**The Process:**

1.  **Obtain the Binaries:** You need both versions of the binary: the vulnerable one and the patched one.
2.  **Differentiate the Binaries:** A binary diffing tool (like `bindiff`, `Ghidra`, or `IDA Pro`) is used to compare the two files.
3.  **Analyze the Differences:** The researcher analyzes the functions that have changed to identify the vulnerability.
4.  **Develop a PoC:** Once the vulnerability is understood, a proof of concept (PoC) can be developed to demonstrate it.

## 4.2. Extracting Windows Patches

In Windows, security patches are distributed as MSU files. These files can be extracted to obtain the updated binaries.

**PowerShell Extraction Script (Extract-Patch.ps1):**

A PowerShell script can automate the process of downloading and extracting Windows Update patches.

## 4.3. Binary Diffing Tools

-   **Ghidra and Ghidriff:** Ghidra is a software reverse engineering framework from the NSA. Ghidriff is a Ghidra extension that facilitates binary diffing.
-   **BinDiff:** A popular diffing tool for IDA Pro.
-   **Ghidra's Version Tracking:** Ghidra also has a built-in "version tracking" feature that can be used to compare binaries.

## 4.4. Case Study: CVE-2022-34718 (EvilESP)

This case study shows how patch diffing was used to analyze a vulnerability in the Windows ESP protocol. The analysis revealed an error in the handling of fragmented ESP packets that could lead to remote code execution.

### CVE Information:

| Attribute | Value |
|----------|-------|
| CVE | CVE-2022-34718 |
| Name | "EvilESP" |
| Component | tcpip.sys (Windows TCP/IP Driver) |
| Type | Remote Code Execution (RCE) |
| CVSS | 9.8 (Critical) |
| Vector | Network, unauthenticated (with IPsec enabled) |
| Versions | Windows Server 2012-2022, Windows 10/11 |
| Patch | September 2022 (KB5017308, KB5017305) |

### Prerequisites for Exploitation:

| Prerequisite | Description |
|---------------|-------------|
| IPv6 enabled | Default on Windows |
| IPsec enabled and SA established | |
| Attacker knows SPI + HMAC key | From the victim |
| Attacker can send IPv6 packets | To the victim |

### 4.4.1. Acquiring Binaries for EvilESP

```powershell
# Create working directory
mkdir C:\EvilESP-Analysis
cd C:\EvilESP-Analysis

# Get vulnerable tcpip.sys (pre-September 2022)
# WinbIndex: https://winbindex.m417z.com/ → tcpip.sys → KB5016616

# Get patched tcpip.sys (September 2022+)
# WinbIndex → KB5017308 (Server 2022) or KB5017305 (Win 10/11)

# Download symbols
$symchk = "C:\Program Files (x86)\Windows Kits\10\Debuggers\x64\symchk.exe"
& $symchk tcpip_vulnerable.sys /s "SRV*.\Symbols*https://msdl.microsoft.com/download/symbols"
```

### 4.4.2. Running Diff and Analysis

```powershell
ghidriff tcpip_vulnerable.sys tcpip_patched.sys \
    --symbols-path .\Symbols \
    --max-section-funcs 5000 \
    --output tcpip_diff

# Expected: Only 2 functions changed
# - IppReceiveEsp
# - Ipv6pReassembleDatagram
```

### 4.4.3. Vulnerable vs Patched Code Analysis

**Function 1: IppReceiveEsp**

Vulnerable Code:
```c
void IppReceiveEsp(longlong param_1) {
    iVar3 = IppReceiveEspNbl(...);

    // BUG: Only checks 0 (success) or 0x105 (pending)
    if ((iVar3 == 0) || (iVar3 == 0x105)) {
        *(undefined4 *)((longlong)param_1 + 0x2c) = 0x3b;
        return;
    }
}
```

Patched Code:
```c
void IppReceiveEsp(longlong param_1) {
    iVar3 = IppReceiveEspNbl(...);

    // FIX 1: Complete range verification
    if ((iVar3 != 0) && (1 < (uint)(iVar3 - 0x2b))) {
        // FIX 2: Discard invalid packets
        if ((iVar3 != 0x105) && (puVar3 != NULL)) {
            IppDiscardReceivedPackets(
                (longlong)puVar3, 6, param_1, 0, 0, 0, 0xe0004148);
            return;
        }
    }
}
```

**Function 2: Ipv6pReassembleDatagram**

Vulnerable Code:
```c
void Ipv6pReassembleDatagram(...) {
    uVar11 = *(int *)(param_2 + 0x8c) + (uint)*(ushort *)(param_2 + 0x88);
    // BUG 1: No 16-bit overflow check
    // BUG 2: No nextheader_offset validation

    if (uVar1 < uVar13) {
        memcpy(puVar5 + 5, *(void **)(param_2 + 0x80),
               (ulonglong)*(ushort *)(param_2 + 0x88));
    }
}
```

Patched Code:
```c
void Ipv6pReassembleDatagram(...) {
    uVar11 = *(int *)(param_2 + 0x8c) + (uint)*(ushort *)(param_2 + 0x88);

    // FIX 1: Check 16-bit overflow
    if (uVar14 < 0x10001) {
        // FIX 2: Validate nextheader_offset
        if (*(ushort *)(param_2 + 0xbc) <= uVar13) {
            // FIX 3: Check final size
            if (uVar14 + 0x28 < *(uint *)(lVar4 + 0x18)) {
                // Log failure
            }
        }
    }
}
```

### 4.4.4. Attack Flow

1. Attacker creates malicious IPv6 packets with ESP header and fragments causing overflow
2. Packet 1: Fragment with offset=0, M=1
3. Packet 2: Fragment with offset=24, M=0 (triggers reassembly)
4. IppReceiveEsp() doesn't correctly validate return code
5. Ipv6pReassembleDatagram() doesn't check overflow or nextheader_offset
6. memcpy OOB → memory corruption → RCE or BSOD

### 4.4.5. ESP Packet Structure

**ESP Header (RFC 4303):**
- SPI (4 bytes)
- Sequence Number (4 bytes)
- Payload Data (variable)
- Padding + Pad Length + Next Header

**IPv6 Fragment Header:**
- Next Header (1 byte)
- Fragment Offset (13 bits) + Flags
- Identification (4 bytes)

### 4.4.6. Exploitation Primitive

| Aspect | Details |
|--------|---------|
| Type | Out-of-bounds write |
| Size | Variable |
| Offset Control | Via nextheader_offset |
| Trigger | Remote, requires IPsec SA |
| Prerequisite | IPv6 enabled, IPsec running |

### 4.4.7. Patch Summary

| Function | Vulnerability | Fix |
|----------|---------------|-----|
| IppReceiveEsp | Missing validation | Range check |
| IppReceiveEsp | Continue on error | IppDiscardReceivedPackets |
| Ipv6pReassembleDatagram | Integer overflow | Check: uVar14 < 0x10001 |
| Ipv6pReassembleDatagram | OOB offset | Check: offset <= buffer |

### 4.4.8. Lessons

1. Binary diffing is effective: 10,000+ functions → only 2 changed
2. Protocol knowledge is essential
3. Simple bugs have high impact (CVSS 9.8)
4. Multi-function vulnerabilities are common
5. Prerequisites limit real risk
6. Patches reveal trigger conditions

## 4.5. Patch Diffing Automation Pipeline

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

## 4.6. Patch Diffing in the Linux Kernel

### 4.6.1. Differences from Windows

| Aspect              | Windows                            | Linux                              |
| ------------------- | ---------------------------------- | ---------------------------------- |
| Source Code         | Closed (binaries only)             | Open (git.kernel.org)              |
| Binary Format       | PE/COFF                            | ELF                                |
| Debug Symbols       | PDB via Symbol Server              | DWARF in -dbgsym packages          |
| Distribution        | Windows Update                     | apt/yum + distro-specific          |
| Vendor Modifications| None                               | Backports, custom patches          |

### 4.6.2. Linux Workflow

1.  **Identify Kernel Versions**
2.  **Download Kernel Images and Symbols**
3.  **Extract vmlinux**
4.  **Identify Changed Modules**
5.  **Diff with Ghidriff**

### 4.6.3. Source Code Level Diff

```bash
# Clone the kernel source
git clone --branch v6.8 https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
cd linux

# Search for CVE commits
git log --all --grep="CVE" --oneline | head -20

# View the diff of a specific commit
git show f342de4e2f33e0e39165d8639387aa6c19dff660
```

### 4.6.4. Example: CVE-2024-1086 (nf_tables UAF)

| Attribute | Value |
|----------|-------|
| CVE | CVE-2024-1086 |
| Component | nf_tables (Netfilter subsystem) |
| Type | Use-After-Free → LPE |
| CVSS | 7.8 (High) |
| Affected | Linux 3.15 - 6.8 |
| Public Exploit | Yes (~99% success rate) |

**Bug Analysis:**
- Mask-based validation allowed values like NF_DROP | extra_bits
- & NF_VERDICT_MASK passed through "decorated" verdicts
- Type confusion → UAF → LPE
- Fix: Changed from mask validation to exact match

### 4.6.5. Linux Kernel Resources

| Resource | URL | Usefulness |
|----------|-----|------------|
| syzbot | syzkaller.appspot.com | Reproducers, auto-bisection |
| Ubuntu Security Notices | ubuntu.com/security/notices | Distro advisories |
| kernel.org | git.kernel.org | Official source code |

## 4.7. Case Study: 7-Zip Path Traversal

### 4.7.1. Case Information

| Attribute | Value |
|----------|-------|
| Software | 7-Zip File Archiver |
| Affected Versions | 24.09 and earlier |
| Type | Path Traversal via Symlink (CWE-22) |
| Impact | Arbitrary File Write → potential RCE |
| CVSS | 7.8 (High) |

### 4.7.2. Patch Analysis

File: `CPP/7zip/UI/Common/ArchiveExtractCallback.cpp`

**Change 1: IsSafePath with WSL Parameter**
```c
// BEFORE: bool IsSafePath(const UString &path)
// AFTER: static bool IsSafePath(const UString &path, bool isWSL)
```

**Change 2: WSL-Aware Detection**
```c
// BEFORE: IsAbsolute = NName::IsAbsolutePath(path);
// AFTER: IsAbsolute = isWSL ? IS_PATH_SEPAR(path[0]) : NName::IsAbsolutePath(path);
```

### 4.7.3. Attack Scenario

1. Create file with WSL symlink: `link -> /mnt/c/Users/Public/Desktop`
2. 7-Zip 24.09: IsSafePath() without isWSL=true → classifies as "relative"
3. Symlink created outside extraction directory
4. → Arbitrary File Write → RCE via DLL hijacking

### 4.7.4. Path Validation Checklist

**Search:** IsSafePath, ValidatePath, IsAbsolute, IsRelative, symlinks

**Verify:**
- Is cross-platform detection correct?
- Are WSL/Linux symlinks handled with proper semantics?
- Is normalization done before validation?

## 4.8. Chapter 4 Conclusions

1. **The patch is often the only source of truth** when CVE details are limited.

2. **Tools automate but don't replace human analysis** - Ghidriff finds changed functions, you understand why.

3. **Symbols are force multipliers** - With PDBs you see `IppValidatePacketLength`; without them, you see `sub_1400A2F40`.

4. **Fix patterns reveal vulnerability classes:**
   - Bounds checks → overflow/OOB
   - Initialization → uninitialized memory
   - Locks → race condition
   - Input validation → input validation flaw

5. **Patch diffing finds variants** - When analyzing a fix, similar bugs in nearby code are often discovered.

6. **Cross-platform analysis requires knowledge of both semantics** - As seen in 7-Zip.

7. **Automation transforms analysis from reactive to proactive**.

### Discussion Questions:

1. CVE-2022-34718 requires IPsec SA but received CVSS 9.8. How should prerequisites affect rating?

2. EvilESP bug spanned two functions. How could you detect cross-function vulnerabilities?

3. IPv6 fragmentation is a recurring source of errors. What makes it prone to bugs?

4. 7-Zip fix added multiple changes. How do you determine which corrects the core vulnerability?
