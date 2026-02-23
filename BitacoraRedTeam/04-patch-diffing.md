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
... (El resto del capítulo seguiría la misma estructura)
