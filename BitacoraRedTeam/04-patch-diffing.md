# Capítulo 4: Patch Diffing

El "Patch Diffing" es el proceso de comparar dos versiones de un programa, una con un parche de seguridad y otra sin él, para identificar la vulnerabilidad que el parche corrige. Es una técnica crucial para los investigadores de seguridad que quieren entender cómo funciona una vulnerabilidad y cómo explotarla.

## 4.1. 3.1 Fundamentos de Patch Diffing

**El Proceso:**

1.  **Obtener los Binarios:** Se necesitan las dos versiones del binario: la vulnerable y la parcheada.
2.  **Diferenciar los Binarios:** Se utiliza una herramienta de "diffing" binario (como `bindiff`, `Ghidra`, o `IDA Pro`) para comparar los dos archivos.
3.  **Analizar las Diferencias:** El investigador analiza las funciones que han cambiado para identificar la vulnerabilidad.
4.  **Desarrollar un PoC:** Una vez que se entiende la vulnerabilidad, se puede desarrollar una prueba de concepto (PoC) para demostrarla.

## 4.2. 3.2 Extracción de Parches de Windows

En Windows, los parches de seguridad se distribuyen como archivos MSU. Estos archivos se pueden extraer para obtener los binarios actualizados.

**Script de Extracción PowerShell (Extract-Patch.ps1):**

Un script de PowerShell puede automatizar el proceso de descarga y extracción de parches de Windows Update.

## 4.3. 3.3 Herramientas de Diffing Binario

-   **Ghidra y Ghidriff:** Ghidra es un framework de ingeniería inversa de software de la NSA. Ghidriff es una extensión de Ghidra que facilita el "diffing" de binarios.
-   **BinDiff:** Una popular herramienta de "diffing" para IDA Pro.
-   **Version Tracking de Ghidra:** Ghidra también tiene una función de "version tracking" incorporada que se puede utilizar para comparar binarios.

## 4.4. 3.4 Caso de Estudio: CVE-2022-34718 (EvilESP)

Este caso de estudio muestra cómo se utilizó el "patch diffing" para analizar una vulnerabilidad en el protocolo ESP de Windows. El análisis reveló un error en el manejo de paquetes ESP fragmentados que podía llevar a la ejecución remota de código.

### Información del CVE:

| Atributo | Valor |
|----------|-------|
| CVE | CVE-2022-34718 |
| Nombre | "EvilESP" |
| Componente | tcpip.sys (Windows TCP/IP Driver) |
| Tipo | Remote Code Execution (RCE) |
| CVSS | 9.8 (Crítico) |
| Vector | Red, sin autenticación (con IPsec habilitado) |
| Versiones | Windows Server 2012-2022, Windows 10/11 |
| Parche | Septiembre 2022 (KB5017308, KB5017305) |

### Prerrequisitos para Explotación:

| Prerrequisito | Descripción |
|---------------|-------------|
| IPv6 habilitado | Default en Windows |
| IPsec habilitado y SA establecida | |
| Atacante conoce SPI + clave HMAC | De la víctima |
| Atacante puede enviar paquetes IPv6 | A la víctima |

### 4.4.1. Adquisición de Binarios para EvilESP

```powershell
# Crear directorio de trabajo
mkdir C:\EvilESP-Analysis
cd C:\EvilESP-Analysis

# Obtener tcpip.sys vulnerable (pre-Septiembre 2022)
# WinbIndex: https://winbindex.m417z.com/ → tcpip.sys → KB5016616

# Obtener tcpip.sys parcheado (Septiembre 2022+)
# WinbIndex → KB5017308 (Server 2022) o KB5017305 (Win 10/11)

# Descargar símbolos
$symchk = "C:\Program Files (x86)\Windows Kits\10\Debuggers\x64\symchk.exe"
& $symchk tcpip_vulnerable.sys /s "SRV*.\Symbols*https://msdl.microsoft.com/download/symbols"
```

### 4.4.2. Ejecutar Diff y Análisis

```powershell
ghidriff tcpip_vulnerable.sys tcpip_patched.sys \
    --symbols-path .\Symbols \
    --max-section-funcs 5000 \
    --output tcpip_diff

# Esperado: Solo 2 funciones cambiadas
# - IppReceiveEsp
# - Ipv6pReassembleDatagram
```

### 4.4.3. Análisis de Código Vulnerable vs Parcheado

**Función 1: IppReceiveEsp**

Código Vulnerable:
```c
void IppReceiveEsp(longlong param_1) {
    iVar3 = IppReceiveEspNbl(...);

    // BUG: Solo verifica 0 (éxito) o 0x105 (pendiente)
    if ((iVar3 == 0) || (iVar3 == 0x105)) {
        *(undefined4 *)((longlong)param_1 + 0x2c) = 0x3b;
        return;
    }
}
```

Código Parcheado:
```c
void IppReceiveEsp(longlong param_1) {
    iVar3 = IppReceiveEspNbl(...);

    // FIX 1: Verificación de rango completa
    if ((iVar3 != 0) && (1 < (uint)(iVar3 - 0x2b))) {
        // FIX 2: Descartar paquetes inválidos
        if ((iVar3 != 0x105) && (puVar3 != NULL)) {
            IppDiscardReceivedPackets(
                (longlong)puVar3, 6, param_1, 0, 0, 0, 0xe0004148);
            return;
        }
    }
}
```

**Función 2: Ipv6pReassembleDatagram**

Código Vulnerable:
```c
void Ipv6pReassembleDatagram(...) {
    uVar11 = *(int *)(param_2 + 0x8c) + (uint)*(ushort *)(param_2 + 0x88);
    // BUG 1: Sin verificación de overflow de 16 bits
    // BUG 2: Sin validación de nextheader_offset

    if (uVar1 < uVar13) {
        memcpy(puVar5 + 5, *(void **)(param_2 + 0x80),
               (ulonglong)*(ushort *)(param_2 + 0x88));
    }
}
```

Código Parcheado:
```c
void Ipv6pReassembleDatagram(...) {
    uVar11 = *(int *)(param_2 + 0x8c) + (uint)*(ushort *)(param_2 + 0x88);

    // FIX 1: Verificar overflow de 16 bits
    if (uVar14 < 0x10001) {
        // FIX 2: Validar nextheader_offset
        if (*(ushort *)(param_2 + 0xbc) <= uVar13) {
            // FIX 3: Verificar tamaño final
            if (uVar14 + 0x28 < *(uint *)(lVar4 + 0x18)) {
                // Registrar fallo
            }
        }
    }
}
```

### 4.4.4. Flujo de Ataque

1. Atacante crea paquetes IPv6 maliciosos con header ESP y fragmentos que causan overflow
2. Paquete 1: Fragment con offset=0, M=1
3. Paquete 2: Fragment con offset=24, M=0 (dispara reensamblaje)
4. IppReceiveEsp() no valida correctamente el código de resultado
5. Ipv6pReassembleDatagram() no verifica overflow ni nextheader_offset
6. memcpy OOB → corrupción de memoria → RCE o BSOD

### 4.4.5. Estructura de Paquetes ESP

**ESP Header (RFC 4303):**
- SPI (4 bytes)
- Sequence Number (4 bytes)
- Payload Data (variable)
- Padding + Pad Length + Next Header

**IPv6 Fragment Header:**
- Next Header (1 byte)
- Fragment Offset (13 bits) + Flags
- Identification (4 bytes)

### 4.4.6. Primitiva de Explotación

| Aspecto | Detalles |
|---------|----------|
| Tipo | Out-of-bounds write |
| Tamaño | Variable |
| Control de Offset | Via nextheader_offset |
| Trigger | Remoto, requiere IPsec SA |
| Prerrequisito | IPv6 enabled, IPsec corriendo |

### 4.4.7. Resumen del Parche

| Función | Vulnerabilidad | Fix |
|---------|---------------|-----|
| IppReceiveEsp | Validación faltante | Verificación de rango |
| IppReceiveEsp | Error continuo | IppDiscardReceivedPackets |
| Ipv6pReassembleDatagram | Integer overflow | Check: uVar14 < 0x10001 |
| Ipv6pReassembleDatagram | OOB offset | Check: offset <= buffer |

### 4.4.8. Lecciones

1. Binary diffing es efectivo: 10,000+ funciones → solo 2 cambiaron
2. Conocimiento de protocolos es esencial
3. Bugs simples tienen alto impacto (CVSS 9.8)
4. Vulnerabilidades multi-función son comunes
5. Prerrequisitos limitan el riesgo real
6. Parches revelan las condiciones de trigger

## 4.5. 3.5 Pipeline de Automatización de Patch Diffing

### ¿Por Qué Automatizar?

-   Microsoft libera parches mensualmente (Patch Tuesday - 2do martes de cada mes)
-   Analizar cada actualización manualmente consume mucho tiempo
-   Detección temprana de vulnerabilidades provee ventaja competitiva
-   La automatización permite monitoreo continuo

### Etapas del Pipeline:

1.  **MONITOREAR:** MSRC API, Patch Tuesday
2.  **DESCARGAR:** WinbIndex, Update Catalog
3.  **EXTRAER:** Expand MSU, Extract CAB
4.  **SÍMBOLOS:** symchk.exe, Symbol Server
5.  **DIFF:** Ghidriff, BinDiff
6.  **REPORTE:** HTML/PDF, JSON para CI
7.  **ALERTA:** Email, Ticket, Slack/Teams

### Script de Automatización Python para Ghidriff

```python
#!/usr/bin/env python3
import subprocess
import json
import os
from pathlib import Path
from datetime import datetime

class PatchDiffer:
    # ... (implementación del script)
```

## 4.6. 3.6 Patch Diffing en Linux Kernel

### 3.6.1. Diferencias con Windows

| Aspecto             | Windows                            | Linux                              |
| ------------------- | ---------------------------------- | ---------------------------------- |
| Código Fuente       | Cerrado (solo binarios)            | Abierto (git.kernel.org)           |
| Formato Binario     | PE/COFF                            | ELF                                |
| Símbolos Debug      | PDB via Symbol Server              | DWARF en paquetes -dbgsym          |
| Distribución        | Windows Update                     | apt/yum + distro-specific          |
| Modificaciones Vendor| Ninguna                            | Backports, parches custom          |

### 3.6.2. Flujo de Trabajo para Linux

1.  **Identificar Versiones de Kernel**
2.  **Descargar Imágenes de Kernel y Símbolos**
3.  **Extraer vmlinux**
4.  **Identificar Módulos Cambiados**
5.  **Diff con Ghidriff**

### 3.6.3. Diff a Nivel de Código Fuente

```bash
# Clonar fuente del kernel
git clone --branch v6.8 https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
cd linux

# Buscar commits de CVE
git log --all --grep="CVE" --oneline | head -20

# Ver diff de commit específico
git show f342de4e2f33e0e39165d8639387aa6c19dff660
```
... (El resto del capítulo seguiría la misma estructura)



### 3.6.4. Ejemplo: CVE-2024-1086 (nf_tables UAF)

| Atributo | Valor |
|----------|-------|
| CVE | CVE-2024-1086 |
| Componente | nf_tables (subsistema Netfilter) |
| Tipo | Use-After-Free → LPE |
| CVSS | 7.8 (Alto) |
| Afecta | Linux 3.15 - 6.8 |
| Exploit Público | Sí (~99% success rate) |

**Análisis del Bug:**
- Validación basada en máscara permitía valores como NF_DROP | extra_bits
- & NF_VERDICT_MASK dejaba pasar verdicts "decorados"
- Type confusion → UAF → LPE
- Fix: Cambiar de validación por máscara a coincidencia exacta

### 3.6.5. Recursos para Linux Kernel

| Recurso | URL | Utilidad |
|---------|-----|----------|
| syzbot | syzkaller.appspot.com | Reproducers, bisección automática |
| Ubuntu Security Notices | ubuntu.com/security/notices | Advisories de distro |
| kernel.org | git.kernel.org | Código fuente oficial |

## 4.7. Caso de Estudio: 7-Zip Path Traversal

### 4.7.1. Información del Caso

| Atributo | Valor |
|----------|-------|
| Software | 7-Zip File Archiver |
| Versiones Afectadas | 24.09 y anteriores |
| Tipo | Path Traversal via Symlink (CWE-22) |
| Impacto | Arbitrary File Write → RCE potencial |
| CVSS | 7.8 (Alto) |

### 4.7.2. Análisis del Parche

Archivo: `CPP/7zip/UI/Common/ArchiveExtractCallback.cpp`

**Cambio 1: IsSafePath con Parámetro WSL**
```c
// ANTES: bool IsSafePath(const UString &path)
// DESPUÉS: static bool IsSafePath(const UString &path, bool isWSL)
```

**Cambio 2: Detección WSL-Aware**
```c
// ANTES: IsAbsolute = NName::IsAbsolutePath(path);
// DESPUÉS: IsAbsolute = isWSL ? IS_PATH_SEPAR(path[0]) : NName::IsAbsolutePath(path);
```

### 4.7.3. Escenario de Ataque

1. Crear archivo con symlink WSL: `link -> /mnt/c/Users/Public/Desktop`
2. 7-Zip 24.09: IsSafePath() sin isWSL=true → clasifica como "relativo"
3. Symlink creado fuera del directorio de extracción
4. → Arbitrary File Write → RCE via DLL hijacking

### 4.7.4. Checklist de Validación de Paths

**Buscar:** IsSafePath, ValidatePath, IsAbsolute, IsRelative, symlinks

**Verificar:**
- ¿Detección cross-plataforma correcta?
- ¿Symlinks WSL/Linux con semántica adecuada?
- ¿Normalización antes de validación?

## 4.8. Conclusiones del Capítulo 4

1. **El parche es frecuentemente la única fuente de verdad** cuando los detalles del CVE son limitados.

2. **Las herramientas automatizan pero no reemplazan el análisis humano** - Ghidriff encuentra funciones cambiadas, tú entiendes por qué.

3. **Los símbolos son multiplicadores de fuerza** - Con PDBs ves `IppValidatePacketLength`; sin ellos, ves `sub_1400A2F40`.

4. **Patrones de corrección revelan clases de vulnerabilidad:**
   - Bounds checks → overflow/OOB
   - Inicialización → memoria no inicializada
   - Locks → race condition
   - Validación de input → input validation flaw

5. **El patch diffing encuentra variantes** - Al analizar un fix, frecuentemente se descubren bugs similares en código cercano.

6. **El análisis cross-plataforma requiere conocimiento de ambas semánticas** - Como se vio en 7-Zip.

7. **La automatización transforma el análisis de reactivo a proactivo**.

### Preguntas de Discusión:

1. CVE-2022-34718 requiere IPsec SA pero recibió CVSS 9.8. ¿Cómo deberían los prerrequisitos afectar el rating?

2. El bug de EvilESP abarcó dos funciones. ¿Cómo podrían detectar vulnerabilidades cross-función?

3. La fragmentación IPv6 es fuente recurrente. ¿Qué hace que sea propensa a errores?

4. El fix de 7-Zip añadió múltiples cambios. ¿Cómo determinas cuál corrige la vulnerabilidad core?