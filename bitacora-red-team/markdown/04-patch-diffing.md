---
title: "Capítulo 04: Patch Diffing"
chapter: 04
description: "Patch Diffing - Manual de Explotación del Kernel de Linux"
---

### CAPÍTULO 3. FUZZING
Bitácora Red Team
#include <stdint.h>
#include <stddef.h>
int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
const char *data1 = (const char *)data;
json_tokener *tok = json_tokener_new();
json_object *obj = json_tokener_parse_ex(tok, data1, size);
if (obj) {
// Ejercitar diferentes funciones API para aumentar cobertura
json_object_to_json_string_ext(obj,
### JSON_C_TO_STRING_PRETTY | JSON_C_TO_STRING_SPACED);
if (json_object_is_type(obj, json_type_object)) {
json_object_object_foreach(obj, key, val) {
(void)json_object_get_type(val);
(void)json_object_get_string(val);
}
}
if (json_object_is_type(obj, json_type_array)) {
size_t len = json_object_array_length(obj);
for (size_t i = 0; i < len; i++) {
json_object_array_get_idx(obj, i);
}
}
json_object_put(obj);
// Liberar objeto
}
json_tokener_free(tok);
// Cleanup
return 0;
}
Compilación y Ejecución:
# Compilar harness con libFuzzer y sanitizers
clang-19 -g -fsanitize=address,fuzzer \
-I./json-c \
fuzz_json.c \
json-c/libjson-c.a \
-o fuzz_json
# Crear corpus de semillas con archivos JSON válidos
mkdir -p corpus
echo '{"name": "test", "value": 42}' > corpus/valid1.json
echo '[1, 2, 3, {"nested": "object"}]' > corpus/valid2.json
# Ejecutar fuzzer

---

### CAPÍTULO 3. FUZZING
Bitácora Red Team
./fuzz_json corpus/ -max_total_time=300 -print_final_stats=1
### 3.8.2.
### 2.8.2 Principios de Diseño de Harness
Principio
Descripción
Impacto
Ejecución In‐Process
LLVMFuzzerTestOneInput ‐ sin
overhead fork/exec
10‐100x más rápido
Target Directo de API
Llamar funciones core, no CLI
Evita parsing de
argumentos
Maximización de Cobertura
Ejercitar múltiples caminos de
código
Encuentra más bugs
Cleanup Apropiado
Liberar memoria asignada
Previene OOM
Compatible con Sanitizers
Funciona con ASAN/UBSAN
Mejor detección de bugs
Preguntas de Discusión del Capítulo:
1. ¿Por qué un harness in‐process es órdenes de magnitud más rápido que un wrapper basado
en archivos?
2. ¿Cómo afecta la calidad del corpus de semillas a la penetración del fuzzer en la lógica profunda
del target?
3. ¿Cuáles son los riesgos de “over‐mocking” en un harness ﴾bypass de demasiada inicialización﴿?
4. ¿Cómo determinar si una campaña de fuzzing ha llegado a rendimientos decrecientes?
### 3.8.3.
Conclusiones del Capítulo 2
1. El fuzzing encuentra vulnerabilidades reales: No solo crashes teóricos, sino bugs explota‐
bles en software de producción.
2. El fuzzing guiado por cobertura es poderoso: AFL++, Honggfuzz y FuzzTest exploran inte‐
ligentemente caminos de código en lugar de mutación aleatoria.
3. Los sanitizers son esenciales: ASAN, UBSAN convierten bugs sutiles en crashes inmediatos.
4. El tiempo importa: Muchos bugs requieren horas/días de fuzzing para ser descubiertos.
5. La calidad del corpus de semillas afecta resultados: Comenzar con entradas válidas ayuda
a alcanzar caminos de código más profundos.
6. Los parsers son objetivos principales: Image parsers, protocol parsers, file format parsers
son frecuentemente fuzzeados con gran éxito.

---

Capítulo 4
Patch Diffing
El patch diffing es una técnica poderosa de investigación de vulnerabilidades que analiza las dife‐
rencias entre versiones vulnerables y parcheadas de software. Este capítulo cubre los fundamentos,
herramientas y metodologías para identificar vulnerabilidades mediante análisis de parches.
### 4.1.
### 3.1 Fundamentos de Patch Diffing
Qué es el Patch Diffing
El patch diffing es la técnica de comparar una versión vulnerable de un binario con una versión
parcheada para identificar cambios relacionados con seguridad. Al analizar qué corrigió el vendor,
podemos:
1. Identificar la ubicación de la vulnerabilidad: ¿Dónde en el código estaba el bug?
2. Entender la causa raíz: ¿Qué error de programación llevó al bug?
3. Desarrollar técnicas de explotación: ¿Cómo puede ser disparado y explotado el bug?
4. Encontrar bugs variantes: ¿Hay bugs similares en código relacionado?
Por Qué Importa el Patch Diffing
Beneficio
Descripción
Única Fuente de Verdad
Sin detalles de CVE o PoC, el parche revela qué
estaba roto
Descubrimiento de Variantes
Mientras analizas una corrección, puedes encontrar
bugs adicionales cercanos
Desarrollo de Habilidades
Provee práctica enfocada en reversing con targets
conocidos
Insight del Vendor
Aprende cómo diferentes vendors abordan
correcciones de seguridad
Desafíos del Patch Diffing

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
Desafío
Descripción
Asimetría
Pequeños cambios en código fuente pueden afectar
drásticamente binarios compilados
Encontrar Cambios de Seguridad
Los parches frecuentemente agrupan correcciones de
seguridad con features y bugfixes
Reducción de Ruido
Debe distinguirse cambios relevantes para seguridad de
actualizaciones benignas
Limitaciones de Herramientas
Ninguna herramienta automatiza perfectamente el
proceso; el análisis humano es esencial
### 4.2.
### 3.2 Extracción de Parches de Windows
Estructura de Actualizaciones de Windows
Las actualizaciones de Windows vienen en varios formatos:
Tipo
Descripción
Consideración para Diffing
Cumulative
Update
Contiene todas las
correcciones anteriores
Grande, muchos cambios a filtrar
Security
Update
Solo correcciones de
seguridad específicas
Más pequeño, más enfocado
Delta
Update
Solo cambios desde
última actualización
Requiere base + delta
Servicing
Stack
Actualiza el instalador
mismo
Raramente relevante para seguridad
Formato WIM+PSF ﴾Windows 11 24H2+﴿
Las actualizaciones más recientes de Windows usan un nuevo formato:
Componente
Contenidos
¿Se Pueden Extraer Binarios?
.psf
Parches delta binarios
No ‐ requiere archivos base
.wim
Manifiestos, catálogos
No ‐ sin binarios dentro
SSU-*.cab
Binarios de Servicing Stack
Solo archivos SSU
*.msix
Paquetes de apps UWP
Binarios de apps únicamente
Fuentes para Obtener Binarios
1. WinbIndex ﴾winbindex.m417z.com﴿: Base de datos de binarios de Windows indexados por
versión y KB
2. Microsoft Update Catalog: Descargar paquetes .msu directamente
3. Microsoft Symbol Server: Descargar binarios específicos por timestamp/size
4. Sistemas Parcheados: Copiar directamente de sistemas con parches instalados

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
### 4.2.1.
### 3.2.1 Script de Extracción PowerShell ﴾Extract‐Patch.ps1﴿
Script completo para extraer binarios de actualizaciones de Windows:
<#
### .SYNOPSIS
Extrae binarios de parches de actualizaciones Windows.
### .DESCRIPTION
Este script automatiza la extracción de binarios de archivos .msu o .cab,
o puede descargar directamente desde WinbIndex para KBs específicos.
.PARAMETER PatchPath
Ruta a archivo .msu o .cab (o directorio con CABs extraídos)
.PARAMETER UseWinbIndex
Switch para descargar binarios directamente desde WinbIndex
.PARAMETER KBNumber
Número KB para WinbIndex (ej: "KB5041565")
.PARAMETER TargetBinaries
Lista de binarios específicos a extraer (ej: @("ntoskrnl.exe","tcpip.sys"))
### .EXAMPLE
.\Extract-Patch.ps1 -PatchPath "C:\Updates\windows11-kb5041565.msu"
### .EXAMPLE
.\Extract-Patch.ps1 -UseWinbIndex -KBNumber "KB5041565" `
-TargetBinaries @("tcpip.sys","ntdll.dll")
#>
param(
[Parameter(Mandatory=$false)]
[string]$PatchPath,
[Parameter(Mandatory=$false)]
[switch]$UseWinbIndex,
[Parameter(Mandatory=$false)]
[string]$KBNumber,
[Parameter(Mandatory=$false)]
[string[]]$TargetBinaries = @(
"ntoskrnl.exe",
"win32kfull.sys",
"win32kbase.sys",
"tcpip.sys",
"ntdll.dll",

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
"afd.sys",
"http.sys"
)
)
$ErrorActionPreference = "Stop"
$extractDir = ".\binaries"
$tempDir = ".\temp_extract"
function Extract-FromMSU {
param([string]$MsuPath)
Write-Host "[*] Extrayendo MSU: $MsuPath"
# Crear directorio temporal
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
# Expandir MSU
expand -F:* $MsuPath $tempDir
# Encontrar y expandir CABs anidados
$cabs = Get-ChildItem $tempDir -Filter "*.cab" -Recurse
foreach ($cab in $cabs) {
Write-Host "[*] Procesando CAB: $($cab.Name)"
$cabExtract = Join-Path $tempDir $cab.BaseName
New-Item -ItemType Directory -Force -Path $cabExtract | Out-Null
expand -F:* $cab.FullName $cabExtract
}
# Buscar binarios objetivo
foreach ($binary in $TargetBinaries) {
$found = Get-ChildItem $tempDir -Filter $binary -Recurse | Select-Object -First 1
if ($found) {
$destPath = Join-Path $extractDir $binary
Copy-Item $found.FullName $destPath -Force
Write-Host "[+] Extraído: $binary -> $destPath"
} else {
Write-Host "[-] No encontrado: $binary"
}
}
}
function Get-FromWinbIndex {
param([string]$KB)
Write-Host "[*] Consultando WinbIndex para $KB..."
# Nota: WinbIndex no tiene API formal; usar scraping o descargas directas

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
# Esta es una implementación simplificada
$baseUrl = "https://winbindex.m417z.com"
foreach ($binary in $TargetBinaries) {
Write-Host "[*] Buscando $binary..."
# Formato esperado del URL de descarga de WinbIndex
# Los URLs reales requieren hash del archivo
try {
# Buscar en el sitio web (ejemplo simplificado)
$searchUrl = "$baseUrl/?file=$binary"
Write-Host "[*] Consultar manualmente: $searchUrl"
Write-Host "[*] Descargar versión vulnerable y parcheada manualmente"
} catch {
Write-Host "[-] Error buscando $binary : $_"
}
}
Write-Host ""
Write-Host "=== INSTRUCCIONES MANUALES ==="
Write-Host "1. Visitar https://winbindex.m417z.com/"
Write-Host "2. Buscar cada binario: $($TargetBinaries -join ', ')"
Write-Host "3. Filtrar por versión Windows y KB"
Write-Host "4. Descargar versión vulnerable (pre-$KB) y parcheada ($KB)"
Write-Host "5. Guardar en: $extractDir"
}
# Crear directorio de salida
New-Item -ItemType Directory -Force -Path $extractDir | Out-Null
if ($UseWinbIndex) {
if (-not $KBNumber) {
Write-Error "Debe especificar -KBNumber cuando usa -UseWinbIndex"
}
Get-FromWinbIndex -KB $KBNumber
}
elseif ($PatchPath) {
if ($PatchPath -like "*.msu") {
Extract-FromMSU -MsuPath $PatchPath
}
elseif ($PatchPath -like "*.cab") {
# Expandir CAB directamente
expand -F:* $PatchPath $tempDir
# Buscar binarios
foreach ($binary in $TargetBinaries) {
$found = Get-ChildItem $tempDir -Filter $binary -Recurse | Select-Object -First 1
if ($found) {

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
Copy-Item $found.FullName (Join-Path $extractDir $binary) -Force
Write-Host "[+] Extraído: $binary"
}
}
}
else {
Write-Error "Formato no soportado. Use .msu o .cab"
}
}
else {
Write-Host "Uso: .\Extract-Patch.ps1 -PatchPath <ruta.msu>"
Write-Host "
o: .\Extract-Patch.ps1 -UseWinbIndex -KBNumber KB5041565"
}
# Limpiar
if (Test-Path $tempDir) {
Remove-Item $tempDir -Recurse -Force
}
Write-Host ""
Write-Host "[*] Binarios extraídos en: $extractDir"
Get-ChildItem $extractDir | Format-Table Name, Length, LastWriteTime
### 4.2.2.
### 3.2.2 Descarga de Símbolos ﴾PDB﴿
Los símbolos son críticos para análisis de calidad:
# Configurar Symbol Server
$env:_NT_SYMBOL_PATH = "SRV*C:\Symbols*https://msdl.microsoft.com/download/symbols"
# Usar symchk.exe (parte del SDK de Windows)
$symchk = "C:\Program Files (x86)\Windows Kits\10\Debuggers\x64\symchk.exe"
# Descargar símbolos para todos los binarios en un directorio
& $symchk /r "C:\patch-analysis\binaries" /s $env:_NT_SYMBOL_PATH
# O para un archivo específico
& $symchk "C:\patch-analysis\binaries\tcpip.sys" /s $env:_NT_SYMBOL_PATH
# Verificar símbolos descargados
Get-ChildItem "C:\Symbols" -Recurse -Filter "*.pdb" |
Select-Object Name, Length, FullName |
Format-Table
Impacto de los Símbolos en el Análisis:
Con Símbolos
Sin Símbolos
IppValidatePacketLength
sub_1400A2F40

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
Con Símbolos
Sin Símbolos
TcpipNlProcessPacket
sub_14003B120
NdisGetDataBuffer
sub_EXTERN_892
Variables con nombres
Offsets + registros
Tipos de datos
Tamaños genéricos
### 4.3.
### 3.3 Herramientas de Diffing Binario
Opciones de Herramientas
Herramienta
Pros
Contras
Mejor Para
Ghidra + Ghidriff
Gratis,
open‐source,
automatiza‐
ble
Decompilador
menos pulido que
Hex‐Rays
Investigadores con
presupuesto limitado,
automatización
IDA Pro + Diaphora
IDA estándar
de la
industria,
Diaphora
gratis
IDA Pro es caro
﴾$1,000+﴿
Investigadores
profesionales con licencia
### IDA
IDA Pro + BinDiff
Diffing
binario
clásico
BinDiff 8 solo
soporta IDA 8.x
Usuarios legacy de IDA
Ghidriff
Ghidriff es la herramienta recomendada para este curso debido a su accesibilidad:
Completamente gratis y open‐source
Excelente soporte multi‐arquitectura
Reportes automatizados en Markdown/JSON
Soporte Docker para análisis reproducible
Análisis headless perfecto para CI/CD
### 4.3.1.
### 3.3.1 Instalación de Ghidra y Ghidriff
Requisitos Previos: ‐ Ghidra 11.4+ ﴾requiere Java JDK 21+﴿‐ Python 3.10+
Windows ‐ Instalación Paso a Paso:
# 1. Instalar Java JDK 21
# Descargar desde: https://adoptium.net/temurin/releases/
# O usar winget:
winget install EclipseAdoptium.Temurin.21.JDK

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
# Verificar instalación
java -version
# openjdk version "21.0.2" ...
# 2. Descargar e instalar Ghidra
$ghidraUrl = "https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_11.4.2_build
Invoke-WebRequest -Uri $ghidraUrl -OutFile "$env:USERPROFILE\Downloads\ghidra.zip"
# Extraer a directorio permanente
Expand-Archive "$env:USERPROFILE\Downloads\ghidra.zip" -DestinationPath "C:\Tools\"
Rename-Item "C:\Tools\ghidra_11.4.2_PUBLIC" "C:\Tools\Ghidra"
# Configurar variable de entorno (REQUERIDA para Ghidriff)
[Environment]::SetEnvironmentVariable("GHIDRA_INSTALL_DIR", "C:\Tools\Ghidra", "User")
$env:GHIDRA_INSTALL_DIR = "C:\Tools\Ghidra"
# 3. Instalar Ghidriff via pip
pip install ghidriff
# 4. Verificar instalación
ghidriff --version
# ghidriff 0.8.x (versión puede variar)
# 5. Primer análisis (inicializa Ghidra - puede tardar varios minutos)
ghidriff C:\Windows\System32\notepad.exe C:\Windows\System32\write.exe -o test_diff
# Si hay errores de memoria, ajustar:
ghidriff ... --max-ram-percent 70
Linux ‐ Instalación:
# 1. Instalar Java
sudo apt update
sudo apt install -y openjdk-21-jdk
export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))
echo "export JAVA_HOME=$JAVA_HOME" >> ~/.bashrc
# 2. Descargar Ghidra
mkdir -p ~/tools && cd ~/tools
wget https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_11.4.2_build/ghidra_1
unzip ghidra_11.4.2_PUBLIC_20250826.zip
export GHIDRA_INSTALL_DIR=~/tools/ghidra_11.4.2_PUBLIC
echo "export GHIDRA_INSTALL_DIR=$GHIDRA_INSTALL_DIR" >> ~/.bashrc
# 3. Instalar Ghidriff en entorno virtual
sudo apt install -y python3 python3-pip python3-venv
python3 -m venv ~/ghidriff-env
source ~/ghidriff-env/bin/activate
pip install ghidriff

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
# 4. Verificar
ghidriff --help
### 4.3.2.
### 3.3.2 Flujo de Trabajo con Ghidriff
Proceso Completo de Diffing:
┌─────────────────────────────────────────────────────────────────┐
│
### FLUJO DE TRABAJO GHIDRIFF
│
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│
### 1. OBTENER BINARIOS
│
│
└─WinbIndex / Extract-Patch.ps1 / Microsoft Update Catalog │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│
### 2. DESCARGAR SÍMBOLOS (PDB)
│
│
└─symchk.exe o Symbol Server directo
│
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│
### 3. EJECUTAR GHIDRIFF
│
│
└─ghidriff old.sys new.sys -o diff_output
│
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│
### 4. REVISAR REPORTE MARKDOWN
│
│
└─diff_output/*.ghidriff.md
│
│
└─Funciones modificadas, añadidas, eliminadas
│
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│
### 5. ANÁLISIS PROFUNDO
│
│
└─Funciones con ratio < 0.95 = cambios significativos
│
│
└─Buscar: bounds checks, NULL checks, validaciones
│
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
│
### 6. CORRELACIONAR CON CVE
│
│
└─MSRC Advisory / NVD / Vendor Release Notes
│
└─────────────────────────────────────────────────────────────────┘
Comandos Ghidriff Esenciales:
# Diff básico
ghidriff old.sys new.sys -o diff_report
# Con símbolos (RECOMENDADO - mejora significativamente los nombres)
ghidriff old.sys new.sys -o diff_report --symbols-path C:\Symbols
# Para binarios grandes (ntoskrnl.exe, tcpip.sys)
ghidriff old.sys new.sys \
--max-section-funcs 5000 \
--max-ram-percent 80 \
--output large_diff
# Solo analizar sección .text (más rápido, menos ruido)
ghidriff old.dll new.dll --section .text -o text_only_diff
# Modo no-threaded (más estable, más lento)
ghidriff old.sys new.sys --no-threaded -o stable_diff
# Salida JSON para procesamiento automatizado
ghidriff old.sys new.sys -o diff_report --json-only
Estructura de Salida de Ghidriff:
diff_report/
├──old.sys-new.sys.ghidriff.md
# Reporte Markdown legible
│
├──Resumen de cambios
│
├──Funciones añadidas
│
├──Funciones eliminadas
│
└──Funciones modificadas (con snippets de código)
├──json/
│
├──old.sys-new.sys.ghidriff.json
# Datos estructurados completos
│
│
├──functions.added[]
│
│
├──functions.deleted[]
│
│
├──functions.modified[]
│
│
│
├──name
│
│
│
├──ratio (similaridad)
│
│
│
├──old.address
│
│
│
└──new.address
│
│
└──stats{}
│
└──old.sys-new.sys.matches.json
# Correspondencias de funciones
└──ghidriffs/
# Directorio legacy (algunas versiones)

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
### 4.3.3.
### 3.3.3 Version Tracking de Ghidra ﴾Alternativa GUI﴿
Para análisis interactivo lado a lado:
Paso 0: Crear Proyectos Separados
1. Crear proyecto "vulnerable" →importar old.sys
2. Crear proyecto "patched" →importar new.sys
3. Analizar ambos binarios completamente (Auto Analysis)
Paso 1‐3: Crear Sesión de Version Tracking
1. Menú: Tools →Version Tracking →Version Tracking
2. Click "Create Session" (+)
3. Source Program: old.sys (vulnerable)
4. Destination Program: new.sys (parcheado)
5. Seleccionar correladores (usar defaults para empezar)
Paso 4‐5: Ejecutar y Filtrar Resultados
1. Click "Run" para ejecutar correladores seleccionados
2. Panel "Matches": Lista de funciones emparejadas
3. Ordenar por "Similarity" (menor = más cambios)
4. Doble-click para ver comparación lado a lado
5. Filtrar: similarity < 0.95 AND length > 100 bytes
Indicadores Clave en Version Tracking:
Indicador
Significado
Similarity 1.0
Funciones idénticas
Similarity 0.95‐0.99
Cambios menores ﴾nombres, comentarios﴿
Similarity < 0.95
Cambios significativos de lógica
Similarity < 0.80
Reescritura substancial
“Added”
Nueva función en versión parcheada
“Deleted”
Función eliminada en parche
### 4.4.
### 3.4 Caso de Estudio: CVE‐2022‐34718 ﴾EvilESP﴿
Información del CVE:
Atributo
Valor
### CVE
### CVE‐2022‐34718
Nombre
“EvilESP”
Componente
tcpip.sys ﴾Windows TCP/IP Driver﴿
Tipo
Remote Code Execution ﴾RCE﴿
### CVSS
### 9.8 ﴾Crítico﴿
Vector
Red, sin autenticación ﴾con IPsec habilitado﴿
Versiones
Windows Server 2012‐2022, Windows 10/11

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
Atributo
Valor
Parche
Septiembre 2022 ﴾KB5017308, KB5017305﴿
Prerrequisitos para Explotación:
┌─────────────────────────────────────────────────────────────────┐
│
### PRERREQUISITOS CVE-2022-34718
│
├─────────────────────────────────────────────────────────────────┤
│
✓IPv6 habilitado (default en Windows)
│
│
✓IPsec habilitado y SA establecida
│
│
✓Atacante conoce SPI + clave HMAC de la víctima
│
│
✓Atacante puede enviar paquetes IPv6 a la víctima
│
└─────────────────────────────────────────────────────────────────┘
### 4.4.1.
### 3.4.1 Adquisición de Binarios para EvilESP
# Crear directorio de trabajo
mkdir C:\EvilESP-Analysis
cd C:\EvilESP-Analysis
# Obtener tcpip.sys vulnerable (pre-Septiembre 2022)
# Opción 1: WinbIndex
# https://winbindex.m417z.com/ →buscar tcpip.sys →KB5016616 (Agosto 2022)
# Opción 2: De sistema Windows sin parche
# Copy desde máquina vulnerable:
# copy \\victimPC\c$\Windows\System32\drivers\tcpip.sys .\tcpip_vulnerable.sys
# Obtener tcpip.sys parcheado (Septiembre 2022+)
# WinbIndex →tcpip.sys →KB5017308 (Server 2022) o KB5017305 (Win 10/11)
# Renombrar para claridad
Rename-Item tcpip.sys tcpip_patched.sys
# Descargar símbolos
$symchk = "C:\Program Files (x86)\Windows Kits\10\Debuggers\x64\symchk.exe"
& $symchk tcpip_vulnerable.sys /s "SRV*.\Symbols*https://msdl.microsoft.com/download/symbols"
& $symchk tcpip_patched.sys /s "SRV*.\Symbols*https://msdl.microsoft.com/download/symbols"
### 4.4.2.
### 3.4.2 Ejecutar Diff y Análisis
# Ejecutar ghidriff
ghidriff tcpip_vulnerable.sys tcpip_patched.sys \
--symbols-path .\Symbols \
--max-section-funcs 5000 \
--max-ram-percent 80 \

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
--output tcpip_diff
# Revisar resultados
Get-Content .\tcpip_diff\*.ghidriff.md | Select-String "Modified Functions"
# Expected: Solo 2 funciones principales cambiadas
#
- IppReceiveEsp
#
- Ipv6pReassembleDatagram
### 4.4.3.
### 3.4.3 Análisis de Código Vulnerable vs Parcheado
Función 1: IppReceiveEsp
Código Vulnerable:
void IppReceiveEsp(longlong param_1) {
// ... setup code ...
iVar3 = IppReceiveEspNbl(...);
// BUG: Solo verifica 0 (éxito) o 0x105 (pendiente)
// Otros códigos de resultado pasan sin verificación
if ((iVar3 == 0) || (iVar3 == 0x105)) {
// Continuar procesamiento - pero iVar3 podría indicar error!
*(undefined4 *)((longlong)param_1 + 0x2c) = 0x3b;
return;
}
// ... error handling para solo estos dos casos ...
}
Código Parcheado:
void IppReceiveEsp(longlong param_1) {
// ... setup code ...
iVar3 = IppReceiveEspNbl(...);
// FIX 1: Verificación de rango completa
// Acepta solo 0 (éxito), 0x2c-0x3b (rango válido), o 0x105 (pendiente)
if ((iVar3 != 0) && (1 < (uint)(iVar3 - 0x2b))) {
// FIX 2: Descartar paquetes inválidos y registrar error
if ((iVar3 != 0x105) && (puVar3 != NULL)) {
IppDiscardReceivedPackets(
(longlong)puVar3, 6, param_1, 0, 0, 0, 0xe0004148);
*(undefined4 *)(piVar2 + 0x8c) = 0xc000021b;
return;
}
}
*(undefined4 *)((longlong)param_1 + 0x2c) = 0x3b;
return;
}

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
Función 2: Ipv6pReassembleDatagram
Código Vulnerable:
void Ipv6pReassembleDatagram(...) {
// Calcular tamaños
uVar11 = *(int *)(param_2 + 0x8c) + (uint)*(ushort *)(param_2 + 0x88);
// BUG 1: Sin verificación de overflow de 16 bits
// IPv6 payload length es campo de 16 bits, pero uVar14 puede exceder 0xFFFF
// BUG 2: Sin validación de nextheader_offset vs tamaño de buffer
if (uVar1 < uVar13) {
// Procesar reensamblaje SIN validación de tamaño
IppRemoveFromReassemblySet(lVar8 + 0x4f00, param_2, param_3);
// BUG 3: memcpy sin verificación de límites
memcpy(puVar5 + 5, *(void **)(param_2 + 0x80),
(ulonglong)*(ushort *)(param_2 + 0x88));
}
}
Código Parcheado:
void Ipv6pReassembleDatagram(...) {
uVar11 = *(int *)(param_2 + 0x8c) + (uint)*(ushort *)(param_2 + 0x88);
// FIX 1: Verificar overflow de 16 bits
if (uVar14 < 0x10001) {
// FIX 2: Validar nextheader_offset contra tamaño de buffer
if (*(ushort *)(param_2 + 0xbc) <= uVar13) {
// ... operaciones seguras ...
// FIX 3: Verificar tamaño final reensamblado
if (uVar14 + 0x28 < *(uint *)(lVar4 + 0x18)) {
// Discrepancia de tamaño - registrar fallo
if ((DAT_1c0222618 & 0x20) != 0) {
McTemplateK0qq_EtwWriteTransfer(
&MICROSOFT_TCPIP_PROVIDER_Context,
### &TCPIP_IP_REASSEMBLY_FAILURE_PKT_LEN, ...);
}
}
}
} else {
// FIX 4: Registrar overflow de longitud
if ((DAT_1c0222618 & 0x20) != 0) {
McTemplateK0qq_EtwWriteTransfer(...TCPIP_IP_REASSEMBLY_FAILURE_PKT_LEN...);
}

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
}
// Cleanup seguro de paquetes inválidos
IppDeleteFromReassemblySet(lVar8 + 0x4f00, param_2, param_3);
}
### 4.4.4.
### 3.4.4 Flujo de Ataque Visual
┌─────────────────────────────────────────────────────────────────┐
│
ATACANTE (Remoto)
│
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│
Crear paquetes IPv6 maliciosos con:
│
│
• Header ESP (requiere SPI + HMAC válidos de SA establecida)
│
│
• Fragmentos con offsets que causan overflow (>= 0x10001)
│
│
• nextheader_offset apuntando fuera del buffer
│
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│
Paquete 1:
│
│
[Ether][IPv6 nh=ESP][ESP hdr][Fragment(off=0,M=1)][Routing]... │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│
Paquete 2:
│
│
[Ether][IPv6 nh=ESP][ESP hdr][Fragment(off=24,M=0)][Routing].. │
│
└─Dispara reensamblaje ────────┘│
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│
KERNEL VÍCTIMA (tcpip.sys)
│
├─────────────────────────────────────────────────────────────────┤
│
1. Recibir fragmentos IPv6
│
│
2. IppReceiveEsp() - Sin validación de código de resultado
### ◄──┤BUG 1
│
└─Continúa con estado inválido
│
│
3. Ipv6pReassembleDatagram() - Reensamblar fragmentos
│
│
└─Sin check: uVar14 < 0x10001
### ◄──┤BUG 2
│
└─Sin check: nextheader_offset <= buffer_size
### ◄──┤BUG 3
│
4. memcpy / escritura de array va OOB
│

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
│
5. Corrupción de memoria kernel →RCE o BSOD
│
└─────────────────────────────────────────────────────────────────┘
### 4.4.5.
### 3.4.5 Estructura de Paquetes ESP e IPv6
ESP Packet Structure ﴾RFC 4303﴿:

0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|
Security Parameters Index (SPI)
|
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|
Sequence Number
|
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|
Payload Data (variable)
|
~
~
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|
Padding (0-255 bytes)
| Pad Length | NH
|
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
IPv6 Fragment Header:

0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|
Next Header
|
Reserved
|
Fragment Offset
|Res|M|
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|
Identification
|
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
### 4.4.6.
### 3.4.6 Primitiva de Explotación
Aspecto
Detalles
Tipo
Out‐of‐bounds write ﴾potencialmente lectura
también﴿
Tamaño
Variable ﴾controlado via tamaños de fragmento﴿
Control de Offset
Via nextheader_offset en header de fragmento
Trigger
Remoto, requiere IPsec SA establecida
Prerrequisito
IPv6 enabled ﴾default﴿, servicio IPsec corriendo
Enfoque de Explotación Teórico:
1. PRERREQUISITO: Establecer Security Association IPsec con target
└─Requiere SPI válido + clave HMAC (barrera crítica)
2. HEAP GROOMING: Enviar tráfico ESP legítimo para crear estado
predecible en NonPagedPoolNx

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
3. TRIGGER OOB: Enviar headers de fragmento anidados dentro de ESP
para corromper estructuras NET_BUFFER_LIST adyacentes
4. CORRUPCIÓN DE ESTRUCTURA: Sobrescribir punteros de función o
enlaces de lista en allocación de pool adyacente
5. EJECUCIÓN DE CÓDIGO: Redirigir ejecución cuando se procese
estructura corrupta
### 4.4.7.
### 3.4.7 Resumen del Parche
Función
Vulnerabilidad
Fix Añadido
IppReceiveEsp
Validación de resultado faltante
Verificación de rango: (iVar3
!= 0) && (1 < (uint)(iVar3 -
0x2b))
IppReceiveEsp
Ejecución continua en error
Llamada a
IppDiscardReceivedPackets
con error 0xe0004148
Ipv6pReassembleDatagramInteger overflow en tamaño ﴾16‐bit﴿
Check: if (uVar14 < 0x10001)
Ipv6pReassembleDatagramOOB via nextheader_offset
Check: if (*(ushort
*)(param_2 + 0xbc) <=
uVar13)
Ipv6pReassembleDatagramDiscrepancia de tamaño
Check: if (uVar14 + 0x28 <
*(uint *)(lVar4 + 0x18))
Ambas
Sin telemetría
Eventos ETW añadidos: TC-
### PIP_IP_REASSEMBLY_FAILURE_PKT_LEN
### 4.4.8.
### 3.4.8 Lecciones del Caso de Estudio
1. El binary diffing es altamente efectivo: Solo 2 funciones cambiaron en tcpip.sys ‐ enfoque
instantáneo de 10,000+ funciones a 2
2. El conocimiento de protocolos es esencial: Entender ESP ﴾RFC 4303﴿y fragmentación IPv6
﴾RFC 8200﴿fue crucial para comprender el ataque
3. Bugs simples en código complejo son de alto impacto: Una verificación de límites faltante
ganó CVSS 9.8
4. Vulnerabilidades multi‐función son comunes: El fallo de validación de IppReceiveEsp habi‐
litó el OOB write de Ipv6pReassembleDatagram
5. Los prerrequisitos afectan el riesgo real: El requisito de IPsec SA limita la explotación a pesar
del rating crítico
6. Los parches revelan condiciones de trigger: Ver los bounds checks muestra exactamente
qué inputs causan el bug

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
### 4.5.
### 3.5 Pipeline de Automatización de Patch Diffing
¿Por Qué Automatizar?
Microsoft libera parches mensualmente ﴾Patch Tuesday ‐ 2do martes de cada mes﴿
Analizar cada actualización manualmente consume mucho tiempo
Detección temprana de vulnerabilidades provee ventaja competitiva
La automatización permite monitoreo continuo
Etapas del Pipeline:
┌─────────────────────────────────────────────────────────────────┐
│
### PIPELINE DE PATCH DIFFING
│
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────┐
┌─────────────────┐
┌─────────────────┐
│
### 1. MONITOREAR
│───►│
### 2. DESCARGAR
│───►│
### 3. EXTRAER
│
│
### - MSRC API
│
│
- WinbIndex
│
│
- Expand MSU
│
│
- Patch Tuesday│
│
- Update Cat.
│
│
- Extract CAB
│
└─────────────────┘
└─────────────────┘
└─────────────────┘
│
│
└─────────────────────────────────────────────┘
│
▼
┌─────────────────┐
┌─────────────────┐
┌─────────────────┐
│
### 4. SÍMBOLOS
│───►│
### 5. DIFF
│───►│
### 6. REPORTE
│
│
- symchk.exe
│
│
- Ghidriff
│
│
### - HTML/PDF
│
│
- Symbol Server│
│
- BinDiff
│
│
- JSON para CI │
└─────────────────┘
└─────────────────┘
└─────────────────┘
│
▼
┌─────────────────────────────────┐
│
### 7. ALERTA
│
│
- Email a equipo
│
│
- Ticket en sistema
│
│
- Slack/Teams notification
│
└─────────────────────────────────┘
### 4.5.1.
### 3.5.1 Script de Automatización Python para Ghidriff
#!/usr/bin/env python3
"""
ghidriff_batch.py - Batch Diffing para Análisis de Parches de Windows
Ejecuta ghidriff en múltiples binarios y genera reporte HTML consolidado.
Diseñado para ghidriff 0.4.x+ output format.

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
"""
import subprocess
import json
import os
import glob
from pathlib import Path
from datetime import datetime
class PatchDiffer:
def __init__(self, work_dir, target_files):
self.work_dir = Path(work_dir)
self.target_files = target_files
self.results = []
def diff_binaries(self, old_dir, new_dir, output_dir):
"""Ejecutar ghidriff en todos los binarios objetivo"""
old_path = Path(old_dir)
new_path = Path(new_dir)
out_path = Path(output_dir)
out_path.mkdir(parents=True, exist_ok=True)
for target in self.target_files:
old_file = self.find_file(old_path, target)
new_file = self.find_file(new_path, target)
if not old_file or not new_file:
print(f"[-] Saltando {target}: archivos no encontrados")
continue
print(f"[+] Diffing {target}...")
diff_name = f"{target.replace('.', '_')}_diff"
diff_out = out_path / diff_name
cmd = [
"ghidriff",
str(old_file),
str(new_file),
"--output", str(diff_out),
"--symbols-path", "C:\\patch-analysis\\symbols\\",
"--max-section-funcs", "5000",
"--max-ram-percent", "80"
]
try:
result = subprocess.run(cmd, capture_output=True,

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
text=True, timeout=1800)
if result.returncode == 0:
print(f"[+] Éxito: {diff_name}")
self.parse_results(diff_out, target)
else:
print(f"[-] Error diffing {target}: {result.stderr}")
except subprocess.TimeoutExpired:
print(f"[-] Timeout diffing {target}")
except Exception as e:
print(f"[-] Excepción diffing {target}: {e}")
def find_file(self, directory, filename):
"""Buscar archivo recursivamente en directorio"""
for path in directory.rglob(filename):
return path
return None
def parse_results(self, diff_dir, binary_name):
"""Parsear salida JSON de ghidriff"""
json_patterns = [
diff_dir / "json" / "*.ghidriff.json",
diff_dir / "*.ghidriff.json",
diff_dir.parent / "ghidriffs" / "json" / "*.ghidriff.json",
]
json_file = None
for pattern in json_patterns:
matches = glob.glob(str(pattern))
if matches:
json_file = Path(matches[0])
break
if not json_file or not json_file.exists():
print(f"[-] No se encontró salida JSON para {binary_name}")
return
with open(json_file) as f:
data = json.load(f)
functions = data.get("functions", {})
added = functions.get("added", [])
deleted = functions.get("deleted", [])
modified = functions.get("modified", [])
summary = {
"binary": binary_name,

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
"total_funcs": data.get("stats", {}).get("total_functions",
len(added) + len(deleted) + len(modified)),
"matched": data.get("stats", {}).get("matched", 0),
"changed": len(modified),
"new": len(added),
"deleted": len(deleted),
"changed_details": []
}
# Extraer funciones cambiadas con baja similaridad
for func in modified:
ratio = func.get("ratio", 1.0)
if ratio < 0.95:
# Solo funciones con cambios significativos
old_info = func.get("old", {})
new_info = func.get("new", {})
summary["changed_details"].append({
"name": old_info.get("name") or new_info.get("name", "unknown"),
"similarity": ratio,
"address_old": old_info.get("address", ""),
"address_new": new_info.get("address", "")
})
self.results.append(summary)
def generate_report(self, output_file):
"""Generar reporte HTML"""
html = f"""
<!DOCTYPE html>
<html>
<head>
<title>Reporte Patch Diff - {datetime.now().strftime(' %Y- %m- %d')}</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; }}
table {{ border-collapse: collapse; width: 100 %; margin: 20px 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background-color: #4CAF50; color: white; }}
.changed {{ color: #FF5722; font-weight: bold; }}
.highlight {{ background-color: #FFEB3B; }}
.critical {{ background-color: #FFCDD2; }}
</style>
</head>
<body>
<h1>Análisis de Patch Diff de Windows</h1>
<p>Generado: {datetime.now().strftime(' %Y- %m- %d %H: %M: %S')}</p>
"""
for result in self.results:
html += f"""

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
<h2>{result['binary']}</h2>
<table>
<tr><th>Métrica</th><th>Cantidad</th></tr>
<tr><td>Funciones Totales</td><td>{result['total_funcs']}</td></tr>
<tr><td>Emparejadas</td><td>{result['matched']}</td></tr>
<tr class="changed"><td>Cambiadas</td><td>{result['changed']}</td></tr>
<tr><td>Nuevas</td><td>{result['new']}</td></tr>
<tr><td>Eliminadas</td><td>{result['deleted']}</td></tr>
</table>
"""
if result['changed_details']:
html += """
<h3>Funciones Cambiadas (Similaridad < 0.95)</h3>
<table>
<tr><th>Nombre de Función</th><th>Similaridad</th>
<th>Dirección Vieja</th><th>Dirección Nueva</th></tr>
"""
for func in sorted(result['changed_details'],
key=lambda x: x['similarity']):
row_class = 'critical' if func['similarity'] < 0.80 else 'highlight'
html += f"""
<tr class="{row_class}">
<td>{func['name']}</td>
<td>{func['similarity']:.2f}</td>
<td>{func['address_old']}</td>
<td>{func['address_new']}</td>
</tr>
"""
html += "
</table>\n"
html += """
</body>
</html>
"""
with open(output_file, 'w', encoding='utf-8') as f:
f.write(html)
print(f"[+] Reporte generado: {output_file}")
if __name__ == "__main__":
import sys
if len(sys.argv) < 4:
print("Uso: python ghidriff_batch.py <dir_viejo_kb> <dir_nuevo_kb> <dir_salida>")
print("")

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
print("Argumentos:")
print("
dir_viejo_kb
Directorio con binarios vulnerables")
print("
dir_nuevo_kb
Directorio con binarios parcheados")
print("
dir_salida
Directorio para salida de diff y reportes")
print("")
print("Ejemplo:")
print("
python ghidriff_batch.py ./binarios/KB5041565 ./binarios/KB5041571 ./diffs/agosto20
sys.exit(1)
old_dir = sys.argv[1]
new_dir = sys.argv[2]
out_dir = sys.argv[3]
# Objetivos de alto valor por defecto
targets = ["ntdll.dll", "win32k.sys", "tcpip.sys", "ntoskrnl.exe",
"afd.sys", "http.sys"]
differ = PatchDiffer(out_dir, targets)
differ.diff_binaries(old_dir, new_dir, out_dir)
differ.generate_report(os.path.join(out_dir, "report.html"))
### 4.5.2.
### 3.5.2 Automatización con Task Scheduler ﴾Windows﴿
# Crear tarea mensual para Patch Tuesday
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
-Argument "-File C:\patch-analysis\monthly_diff.ps1"
# Trigger: Segundo miércoles de cada mes (día después de Patch Tuesday)
$trigger = New-ScheduledTaskTrigger -Weekly -WeeksInterval 4 -DaysOfWeek Wednesday
# Settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries `
-DontStopIfGoingOnBatteries -StartWhenAvailable
# Registrar tarea
Register-ScheduledTask -TaskName "MonthlyPatchDiff" `
-Action $action -Trigger $trigger -Settings $settings `
-Description "Automated Windows patch diffing"
### 4.5.3.
### 3.5.3 Integración con LLMs para Resumen
Combinar salida de ghidriff con Large Language Models acelera el análisis:
Template de Prompt para LLM:
Eres un investigador de vulnerabilidades analizando un patch diff binario.
Contexto:
- Este diff compara un driver Windows vulnerable con su versión parcheada

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
- Enfócate en cambios relevantes para seguridad (bounds checks, validación, manejo de errores)
- Ignora cambios cosméticos (renombrado de variables, movimiento de código sin cambio de lógica)
Analiza este patch diff y proporciona:
1. CLASE DE VULNERABILIDAD: ¿Qué tipo de bug se está corrigiendo?
2. FUNCIONES AFECTADAS: Lista las funciones con cambios relevantes para seguridad
3. CAUSA RAÍZ: ¿Cuál fue el error de programación subyacente?
4. DESCRIPCIÓN DEL FIX: ¿Qué validación o checks se añadieron?
5. VECTOR DE ATAQUE: ¿Cómo podría un atacante haber disparado esta vulnerabilidad?
6. POTENCIAL DE BYPASS: ¿Hay formas obvias en que el fix podría ser incompleto?
Patch Diff:
[pegar salida markdown de ghidriff - enfocarse en funciones con similaridad <0.95]
Limitaciones de LLMs para Análisis de Parches:
LLMs Ayudan Con
LLMs Tienen Problemas Con
Resumir diffs grandes
Race conditions sutiles
Hipótesis iniciales de clase de vuln
Cálculos complejos de punteros
Explicar patrones de código
Internals del kernel Windows
Redactar secciones de reporte
Distinguir fixes de seguridad vs optimización
### 4.6.
### 3.6 Patch Diffing en Linux Kernel
### 4.6.1.
### 3.6.1 Diferencias con Windows
Aspecto
Windows
Linux
Código Fuente
Cerrado ﴾solo binarios﴿
Abierto ﴾git.kernel.org﴿
Formato Binario
### PE/COFF
### ELF
Símbolos Debug
PDB via Symbol Server
DWARF en paquetes
‐dbgsym
Distribución
Windows Update
apt/yum + distro‐specific
Modificaciones Vendor
Ninguna
Backports, parches
custom
### 4.6.2.
### 3.6.2 Flujo de Trabajo para Linux
Paso 1: Identificar Versiones de Kernel
# Obtener versión actual
CURRENT_KERNEL=$(uname -r)
echo "Kernel actual: $CURRENT_KERNEL"
# Ejemplo: 6.8.0-87-generic
# Extraer base y número de parche

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
KERNEL_BASE=$(echo $CURRENT_KERNEL | sed 's/-[0-9]*-generic//')
KERNEL_PATCH=$(echo $CURRENT_KERNEL | grep -oP '(?<=-)[0-9]+(?=-generic)')
### PREV_PATCH=$((KERNEL_PATCH - 1))
PREV_KERNEL="${KERNEL_BASE}-${PREV_PATCH}-generic"
echo "Versión vulnerable: $PREV_KERNEL"
echo "Versión parcheada: $CURRENT_KERNEL"
# Consultar Ubuntu Security Notices
curl -s 'https://ubuntu.com/security/notices.json?offset=50' | \
jq '.notices[] | select(.title | ascii_downcase | contains("kernel")) | {id, title}'
Paso 2: Descargar Imágenes de Kernel y Símbolos
mkdir ~/kernel-diff && cd ~/kernel-diff
mkdir old new symbols
# Descargar versiones
apt-get download linux-image-unsigned-${PREV_KERNEL}
apt-get download linux-image-unsigned-${CURRENT_KERNEL}
# Extraer
dpkg-deb -x linux-image-unsigned-${PREV_KERNEL}_*.deb old/
dpkg-deb -x linux-image-unsigned-${CURRENT_KERNEL}_*.deb new/
# Símbolos debug (añadir repo ddebs primero)
sudo apt-key adv --keyserver keyserver.ubuntu.com \
--recv-keys F2EDC64DC5AEE1F6B9C621F0C8CAB6595FDFF622
echo "deb http://ddebs.ubuntu.com $(lsb_release -cs)-updates main" | \
sudo tee /etc/apt/sources.list.d/ddebs.list
sudo apt update
apt-get download linux-image-unsigned-${PREV_KERNEL}-dbgsym
apt-get download linux-image-unsigned-${CURRENT_KERNEL}-dbgsym
dpkg-deb -x linux-image-unsigned-${PREV_KERNEL}-dbgsym_*.ddeb old/
dpkg-deb -x linux-image-unsigned-${CURRENT_KERNEL}-dbgsym_*.ddeb new/
Paso 3: Extraer vmlinux
# Desde paquete dbgsym (MEJOR - incluye símbolos)
cp old/usr/lib/debug/boot/vmlinux-${PREV_KERNEL} old/vmlinux
cp new/usr/lib/debug/boot/vmlinux-${CURRENT_KERNEL} new/vmlinux
# Verificar símbolos
file old/vmlinux
# Esperado: ELF 64-bit ... with debug_info, not stripped
nm old/vmlinux | head -5
# Debería mostrar nombres de funciones

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
Paso 4: Identificar Módulos Cambiados
# Comparar árboles de módulos
diff -qr old/usr/lib/debug/lib/modules/${PREV_KERNEL}/kernel/ \
new/usr/lib/debug/lib/modules/${CURRENT_KERNEL}/kernel/ | grep differ
# Enfocarse en subsistemas específicos
diff -qr old/.../kernel/net new/.../kernel/net
diff -qr old/.../kernel/fs/overlayfs/ new/.../kernel/fs/overlayfs/
Paso 5: Diff con Ghidriff
# Activar entorno virtual de ghidriff
source ~/ghidriff-env/bin/activate
# Descomprimir módulo específico (Ubuntu usa .ko.zst)
zstd -d old/usr/lib/debug/lib/modules/${PREV_KERNEL}/kernel/net/netfilter/nf_tables.ko.zst \
-o old/nf_tables.ko
zstd -d new/usr/lib/debug/lib/modules/${CURRENT_KERNEL}/kernel/net/netfilter/nf_tables.ko.zst \
-o new/nf_tables.ko
# Ejecutar diff
ghidriff old/nf_tables.ko new/nf_tables.ko \
--max-ram-percent 80 \
--max-section-funcs 3000 \
--output nf_tables_diff \
--no-threaded
### 4.6.3.
### 3.6.3 Diff a Nivel de Código Fuente
# Clonar fuente del kernel
git clone --branch v6.8 https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
cd linux
# Buscar commits de CVE
git log --all --grep="CVE" --oneline | head -20
# Ver diff de commit específico
git show f342de4e2f33e0e39165d8639387aa6c19dff660
# Buscar fixes en subsistema específico
git log --all --oneline --grep="netfilter" --grep="fix" | head -10
### 4.6.4.
### 3.6.4 Ejemplo: CVE‐2024‐1086 ﴾nf_tables UAF﴿
Información del CVE:

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
Atributo
Valor
### CVE
### CVE‐2024‐1086
Componente
nf_tables ﴾subsistema Netfilter﴿
Tipo
Use‐After‐Free →LPE
### CVSS
### 7.8 ﴾Alto﴿
Afecta
Linux 3.15 ‐ 6.8
Exploit Público
Sí ﴾~99 % success rate﴿
Commit del Fix:
git show f342de4e2f33e0e39165d8639387aa6c19dff660
# Diff simplificado:
# -
default:
# -
switch (data->verdict.code & NF_VERDICT_MASK) {
# -
case NF_ACCEPT:
# -
case NF_DROP:
# -
case NF_QUEUE:
# -
break;
# -
default:
# -
return -EINVAL;
# -
}
# -
fallthrough;
# +
case NF_ACCEPT:
# +
case NF_DROP:
# +
case NF_QUEUE:
# +
break;
#
case NFT_CONTINUE:
#
case NFT_BREAK:
# ...
# +
default:
# +
return -EINVAL;
Análisis:
Bug: Validación basada en máscara permitía valores como NF_DROP | extra_bits
Causa Raíz: & NF_VERDICT_MASK dejaba pasar verdicts “decorados”
Impacto: Type confusion en código posterior →UAF →LPE
Fix: Cambiar de validación por máscara a coincidencia exacta
### 4.6.5.
### 3.6.5 Recursos para Linux Kernel
Recurso
### URL
Utilidad
syzbot
syzkaller.appspot.comReproducers, bisección automática
Ubuntu Security
ubuntu.com/security/notices
Advisories específicos de distro
Debian Tracker
security‐
tracker.debian.org
CVE tracking cross‐distro

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
Recurso
### URL
Utilidad
kernel.org
git.kernel.org
Código fuente oficial
Linux CVE Announce
lore.kernel.org/linux‐
cve‐announce/
Anuncios oficiales de CVE
### 4.7.
### 3.7 Caso de Estudio: 7‐Zip Path Traversal
### 4.7.1.
### 3.7.1 Información del Caso
Atributo
Valor
Software
7‐Zip File Archiver
Versiones Afectadas
### 24.09 y anteriores
Versión Parcheada
### 25.00+
Tipo
Path Traversal via Symlink ﴾CWE‐22﴿
Impacto
Arbitrary File Write →RCE potencial
CVSS Estimado
### 7.8 ﴾Alto﴿
### 4.7.2.
### 3.7.2 Análisis del Parche
Archivo Afectado: CPP/7zip/UI/Common/ArchiveExtractCallback.cpp
Obtener Diff:
git clone https://github.com/ip7z/7zip.git
cd 7zip
# Comparar versiones
git diff 24.09..25.00 -- CPP/7zip/UI/Common/ArchiveExtractCallback.cpp
Cambio 1: IsSafePath con Parámetro WSL
// ANTES (vulnerable):
bool IsSafePath(const UString &path) {
CLinkLevelsInfo levelsInfo;
levelsInfo.Parse(path);
// Sin awareness de WSL
return !levelsInfo.IsAbsolute && levelsInfo.LowLevel >= 0;
}
// DESPUÉS (parcheado):
static bool IsSafePath(const UString &path, bool isWSL) {
CLinkLevelsInfo levelsInfo;
levelsInfo.Parse(path, isWSL);
// Ahora toma parámetro isWSL
return !levelsInfo.IsAbsolute && levelsInfo.LowLevel >= 0;
}
Cambio 2: Detección de Path Absoluto WSL‐Aware

---

### CAPÍTULO 4. PATCH DIFFING
Bitácora Red Team
### // ANTES:
void CLinkLevelsInfo::Parse(const UString &path) {
IsAbsolute = NName::IsAbsolutePath(path);
// Solo semántica Windows
// ...
}
### // DESPUÉS:
void CLinkLevelsInfo::Parse(const UString &path, bool isWSL) {
// WSL usa '/' como indicador de path absoluto
// Windows usa 'C:\', '\\', etc.
IsAbsolute = isWSL ? IS_PATH_SEPAR(path[0]) : NName::IsAbsolutePath(path);
// ...
}
Cambio 3: Verificación de Link Peligroso para Todos los Tipos
// ANTES: Solo directorios en Windows
#ifdef _WIN32
if (_item.IsDir)
// BUG: Solo verifica dirs!
#endif
if (linkInfo.isRelative) { ... }
// DESPUÉS: Todos los symlinks relativos
if (!_ntOptions.SymLinks_AllowDangerous.Val && link.isRelative) {
CLinkLevelsInfo levelsInfo;
levelsInfo.Parse(link.LinkPath, link.Is_WSL());
// WSL-aware
if (levelsInfo.FinalLevel < 1 || levelsInfo.IsAbsolute)
return SendMessageError2(...);
}
### 4.7.3.
### 3.7.3 Escenario de Ataque
┌─────────────────────────────────────────────────────────────────┐
│
ESTRUCTURA DEL ARCHIVO MALICIOSO (tar/rar5)
│
├─────────────────────────────────────────────────────────────────┤
│
safe_folder/
│
│
safe_folder/link -> C:\Users\Public\Desktop
(symlink WSL)
│
│
safe_folder/link/malware.exe
(archivo payload)│
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│
EXTRACCIÓN EN WINDOWS (7-Zip 24.09 vulnerable)
│
├─────────────────────────────────────────────────────────────────┤
│
1. ReadLink() lee target: "C:\Users\Public\Desktop"
│
│
2. IsSafePath() llamado SIN isWSL=true
│
│
3. NName::IsAbsolutePath() usa semántica Windows
│