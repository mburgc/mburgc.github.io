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
