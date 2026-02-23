---
title: "Capítulo 02: Clases de Vulnerabilidades"
chapter: 02
description: "Clases de Vulnerabilidades - Manual de Explotación del Kernel de Linux"
---

Capítulo 1
Introducción
### 1.1.
Información del Documento
Campo
Valor
Título
Bitácora Red Team
Versión
### 1.0
Clasificación
Material Técnico de Referencia
Idioma
Español
Propósito
Educativo e Investigación Defensiva
### 1.2.
Índice de Contenidos
### 1.2.1.
Capítulo 1: Clases de Vulnerabilidades
### 1.1 Fundamentos de Corrupción de Memoria
• 1.1.1 Desbordamiento de Búfer en Pila
• 1.1.2 Uso Después de Liberación ﴾UAF﴿
• 1.1.3 Desbordamiento de Búfer en Heap
• 1.1.4 Lectura Fuera de Límites
• 1.1.5 Uso de Memoria No Inicializada
• 1.1.6 Errores de Conteo de Referencias
• 1.1.7 Desreferencia de Puntero Nulo
### 1.2 Vulnerabilidades Lógicas y Condiciones de Carrera
• 1.2.1 Condiciones de Carrera
• 1.2.2 Vulnerabilidades TOCTOU
• 1.2.3 Vulnerabilidades Double‐Fetch
• 1.2.4 Fallas Lógicas en Autenticación
### 1.3 Confusión de Tipos y Enteros

---

### CAPÍTULO 1. INTRODUCCIÓN
Bitácora Red Team
• 1.3.1 Confusión de Tipos en JIT
• 1.3.2 Desbordamiento de Enteros
• 1.3.3 Vulnerabilidades de Parsers
### 1.4 Vulnerabilidades de Strings y Formato
### 1.5 Vulnerabilidades de Drivers y Sistemas de Archivos
### 1.6 Evaluación de Impacto y Clasificación
### 1.2.2.
Capítulo 2: Fuzzing
### 2.1 Fundamentos de Fuzzing
### 2.2 AFL++ y Fuzzing Guiado por Cobertura
### 2.3 FuzzTest y Fuzzing In‐Process
### 2.4 Honggfuzz y Fuzzing de Protocolos
### 2.5 Syzkaller y Fuzzing de Kernel
### 1.2.3.
Capítulo 3: Patch Diffing
### 3.1 Fundamentos de Patch Diffing
### 3.2 Extracción de Parches de Windows
### 3.3 Herramientas de Diffing Binario
### 3.4 Análisis de Casos de Estudio
### 1.2.4.
Capítulo 4: Análisis de Crashes
### 4.1 Fundamentos del Análisis de Crashes
### 4.2 Depuradores y Configuración
### 4.3 Sanitizadores de Memoria
### 4.4 Clasificación y Triage
### 4.5 Evaluación de Explotabilidad

---

Capítulo 2
Clases de Vulnerabilidades
Este capítulo documenta las principales clases de vulnerabilidades encontradas en sistemas opera‐
tivos y aplicaciones, con énfasis particular en el contexto de kernel y sistemas de bajo nivel. Cada
entrada incluye descripción técnica, casos de estudio reales, impacto y mitigaciones aplicables.
Objetivo: Comprender las clases primarias de vulnerabilidades de corrupción de memoria y su
impacto en el mundo real.
Recursos de Lectura Recomendados: ‐ “The Art of Software Security Assessment” por Mark Dowd,
John McDonald, Justin Schuh ‐ Capítulo 5: Memory Corruption ‐ Memory Corruption: Examples,
Impact, and 4 Ways to Prevent It ‐ Microsoft Security Research: Memory Safety ‐ Google Project
Zero Blog ‐ Hallazgos recientes de corrupción de memoria
### 2.1.
### 1.1 Fundamentos de Corrupción de Memoria
La corrupción de memoria continúa siendo una de las clases de vulnerabilidades más críticas y
prevalentes en software escrito en C/C++. A pesar de décadas de investigación en seguridad, estos
bugs persisten debido a la complejidad inherente de la gestión manual de memoria.
Conceptos Clave: ‐ ¿Qué es la corrupción de memoria y por qué importa? La corrupción de me‐
moria ocurre cuando un programa modifica memoria de maneras no intencionadas, permitiendo
a atacantes alterar el estado del programa y potencialmente obtener control de ejecución. ‐ Pi‐
la ﴾Stack﴿: Región de memoria para variables locales y direcciones de retorno. Su estructura LIFO
﴾Last‐In‐First‐Out﴿la hace vulnerable a desbordamientos que pueden sobrescribir direcciones de
retorno. ‐ Heap: Región de memoria dinámica gestionada por el allocator ﴾malloc/free﴿. Los me‐
tadatos del heap y objetos adyacentes pueden ser corrompidos por desbordamientos. ‐ Ciclo de
Vida de Memoria: Asignación →Uso →Liberación. Los errores en cualquier fase pueden llevar a
vulnerabilidades.
### 2.1.1.
### 1.1.1 Desbordamiento de Búfer en Pila ﴾Stack Buffer Overflow﴿
Descripción General

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
Un desbordamiento de búfer en pila ﴾stack buffer overflow﴿ocurre cuando un programa escribe
más datos en un búfer ubicado en la pila de los que este puede contener. Esto provoca la sobres‐
critura de memoria adyacente, incluyendo datos críticos como direcciones de retorno, permitiendo
potencialmente redirigir la ejecución del programa.
Mecánica del Ataque:
┌─────────────────────────────────────────────────────────────┐
│
### LAYOUT DE PILA
│
├─────────────────────────────────────────────────────────────┤
│
[Direcciones Altas]
│
│
┌─────────────────┐
│
│
│Dirección de
│←Sobrescrita por atacante
│
│
│Retorno
│
│
│
├─────────────────┤
│
│
│Frame Pointer
│←También corrompido
│
│
│Guardado
│
│
│
├─────────────────┤
│
│
│Variables
│
│
│
│Locales
│
│
│
├─────────────────┤
│
│
│Búfer[64]
│←Desbordamiento ocurre aquí
│
│
│
│
│
│
└─────────────────┘
│
│
[Direcciones Bajas]
│
└─────────────────────────────────────────────────────────────┘
Caso de Estudio: CVE‐2024‐27130 — QNAP QTS/QuTS Hero
Campo
Detalle
Producto Afectado
QNAP QTS y QuTS hero
Tipo
Stack Buffer Overflow
Vector
Interfaz de administración web
Severidad
Crítica
PoC Disponible
github.com/watchtowrlabs/CVE‐2024‐27130
El Bug
Los sistemas operativos QTS y QuTS hero de QNAP contenían múltiples vulnerabilidades de copia
de búfer donde funciones inseguras como strcpy() se utilizaban para copiar entrada suministrada
por el usuario a búferes de tamaño fijo en la pila sin validación de tamaño adecuada. Las vulnera‐
bilidades afectaban la interfaz de administración web y los componentes de manejo de archivos.
El Ataque ﴾Paso a Paso﴿
1. Reconocimiento: Atacante identifica endpoint vulnerable en interfaz de administración web

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
2. Preparación: Construcción de payload con entrada sobredimensionada
3. Explotación: Envío de solicitud especialmente diseñada con datos que exceden el tamaño
del búfer
4. Corrupción: Los datos no verificados desbordan el búfer en pila, sobrescribiendo:
Variables locales adyacentes
Frame pointer guardado
Dirección de retorno
5. Control de Ejecución: Cuando la función retorna, el flujo de ejecución se redirige a código
controlado por el atacante
Impacto
Ejecución remota de código con los privilegios del servicio QNAP ﴾típicamente root﴿
Control completo del dispositivo NAS, permitiendo:
• Acceso a todos los datos almacenados
• Pivoteo a otros recursos de red
• Instalación de backdoors persistentes
Riesgo crítico para infraestructura empresarial donde los NAS almacenan datos sensibles
Mitigación
QNAP lanzó QTS 5.1.7.2770 build 20240520 y QuTS hero h5.1.7.2770 build 20240520 en mayo de
2024: ‐ Reemplazo de funciones de copia de cadenas inseguras ﴾strcpy, sprintf﴿con alternativas
con verificación de límites ﴾strncpy, snprintf﴿‐ Implementación de validación de entrada adicional
‐ Habilitación de protecciones de compilador ﴾stack canaries﴿
Observaciones
Los desbordamientos de pila siguen siendo comunes en: ‐ Dispositivos embebidos con código
legacy C/C++ ‐ Sistemas NAS con interfaces de administración expuestas a Internet ‐ Aplicaciones
que no han adoptado APIs seguras modernas
Son particularmente peligrosos cuando: ‐ Proporcionan el punto de entrada inicial para cadenas
de ataque sofisticadas contra infraestructura empresarial ‐ No tienen protecciones de compilador
habilitadas ﴾ASLR, DEP, stack canaries﴿
### 2.1.2.
### 1.1.2 Uso Después de Liberación ﴾Use‐After‐Free / UAF﴿
Descripción General
Una vulnerabilidad de uso después de liberación ﴾Use‐After‐Free﴿ocurre cuando un programa con‐
tinúa usando un puntero después de que la memoria a la que apunta ha sido liberada. Esto crea
un “puntero colgante” ﴾dangling pointer﴿que puede ser explotado controlando cuidadosamente
las asignaciones del heap para colocar datos controlados por el atacante donde el objeto liberado
residía anteriormente.
Mecánica del Bug:
┌─────────────────────────────────────────────────────────────┐
│
### CICLO DE VIDA UAF
│
├─────────────────────────────────────────────────────────────┤

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
│
### 1. ASIGNACIÓN
│
│
obj = malloc(sizeof(Object));
│
│
obj->vtable = &legitimate_vtable;
│
│
│
│
### 2. USO LEGÍTIMO
│
│
obj->method();
// Llama función via vtable
│
│
│
│
### 3. LIBERACIÓN
│
│
free(obj);
// Memoria liberada, pero...
│
│
// ¡El puntero 'obj' aún existe!
│
│
│
│
4. REASIGNACIÓN (por atacante)
│
│
attacker_data = malloc(sizeof(Object));
│
│
// Mismo tamaño →puede obtener la misma ubicación
│
│
attacker_data->vtable = &malicious_vtable;
│
│
│
│
### 5. USO DESPUÉS DE LIBERACIÓN
│
│
obj->method();
// ¡Llama función del atacante!
│
└─────────────────────────────────────────────────────────────┘
Caso de Estudio: CVE‐2024‐2883 — Chrome ANGLE
Campo
Detalle
Producto Afectado
Google Chrome ﴾componente ANGLE﴿
Tipo
Use‐After‐Free
Vector
Página web maliciosa
Severidad
Crítica
Código ExplotableRemotamente
Sí, sin interacción del usuario
El Bug
El componente ANGLE ﴾Almost Native Graphics Layer Engine﴿de Google Chrome, que traduce lla‐
madas de API OpenGL ES a DirectX, Vulkan o OpenGL nativo, contenía una vulnerabilidad de uso
después de liberación. El bug ocurría cuando los contextos WebGL eran destruidos mientras aún
estaban referenciados por operaciones gráficas pendientes, dejando punteros colgantes a objetos
gráficos liberados.
El Ataque ﴾Paso a Paso﴿
1. Preparación del Entorno:
Atacante crea página HTML maliciosa con código JavaScript WebGL
El código manipula la creación y destrucción de contextos gráficos
2. Disparar el Bug:

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
// Concepto simplificado (no es el exploit real):
let ctx = canvas.getContext('webgl');
// Iniciar operación gráfica asíncrona
ctx.bindBuffer(ctx.ARRAY_BUFFER, buffer);
// Destruir contexto mientras operación está pendiente
ctx = null;
// Garbage collection libera el contexto
// pero operación pendiente aún tiene referencia
3. Heap Feng‐Shui:
Usar técnicas de heap spray para controlar asignaciones
Asignar objetos del mismo tamaño que el objeto liberado
Colocar datos controlados por atacante en ubicación liberada
4. Explotación:
Cuando código de ANGLE usa el puntero colgante, accede a datos del atacante
El atacante coloca un objeto falso con vtable maliciosa
La próxima llamada a método virtual ejecuta código del atacante
Impacto
Ejecución remota de código vía página web maliciosa con NO interacción del usuario más allá
de visitar la página
Al colocar un objeto falso en la memoria liberada, el atacante puede secuestrar el flujo de
control
Ejecutar código arbitrario en el proceso del renderer
Puede encadenarse con exploits de escape de sandbox para compromiso completo del siste‐
ma
Mitigación
Google Chrome 123.0.6312.86 ﴾lanzado marzo 2024﴿corrigió la vulnerabilidad: ‐ Implementación
de gestión adecuada del tiempo de vida para objetos gráficos ‐ Añadido conteo de referencias para
prevenir destrucción prematura de objetos aún en uso ‐ Validación adicional antes de usar punteros
a objetos gráficos
Observaciones
Las vulnerabilidades UAF son particularmente peligrosas en: ‐ Navegadores: Aplicaciones C++
complejas donde el tiempo de vida de objetos es difícil de rastrear ‐ Subsistemas Gráficos: ANGLE,
Skia y similares manejan contenido no confiable y tienen gestión de estado compleja ‐ Código con
Callbacks Asíncronos: Donde el orden de ejecución es difícil de predecir
Son un objetivo favorito de atacantes avanzados porque: ‐ Ofrecen control fino sobre la ejecución
del programa ‐ Son difíciles de detectar con análisis estático ‐ Las mitigaciones modernas ﴾ASLR﴿
pueden ser evadidas con técnicas de heap manipulation
### 2.1.3.
### 1.1.3 Desbordamiento de Búfer en Heap ﴾Heap Buffer Overflow﴿
Descripción General

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
Similar a los desbordamientos de pila, los desbordamientos de heap ocurren cuando un programa
escribe más allá de los límites de un búfer asignado dinámicamente en el heap. En lugar de corrom‐
per frames de pila, los desbordamientos de heap típicamente corrompen metadatos del heap o
objetos adyacentes, llevando a corrupción de memoria cuando el allocator posteriormente procesa
las estructuras corrompidas.
Mecánica del Desbordamiento de Heap:
┌─────────────────────────────────────────────────────────────┐
│
### LAYOUT DE HEAP
│
├─────────────────────────────────────────────────────────────┤
│
┌─────────────────────────────────────────┐
│
│
│Chunk Header (metadatos del allocator)
│
│
│
├─────────────────────────────────────────┤
│
│
│Búfer Vulnerable [100 bytes]
│
│
│
│
│
│
│
│════════════════════════════════════════│←Límite
│
│
### │OVERFLOW →→→→→→→→→→→→→→→→→→→→→→→→→→→→
│
│
│
└─────────────────────────────────────────┘
│
│
┌─────────────────────────────────────────┐
│
│
│Chunk Header (CORROMPIDO) ←←←←←←←←←←←
│←Corrupción
│
│
├─────────────────────────────────────────┤
│
│
│Objeto Adyacente
│
│
│
│- vtable *
│←O corrupción
│
│
│- function_ptr
│
de objeto
│
│
│- data fields
│
│
│
└─────────────────────────────────────────┘
│
└─────────────────────────────────────────────────────────────┘
Caso de Estudio: CVE‐2023‐4863 — libWebP
Campo
Detalle
Producto Afectado
libWebP ﴾Chrome, Firefox, Edge, múltiples apps﴿
Tipo
Heap Buffer Overflow
Vector
Imagen WebP maliciosa
Severidad
Crítica
PoC Disponible
github.com/mistymntncop/CVE‐2023‐4863
El Bug
La biblioteca libWebP, utilizada por Chrome, Firefox, Edge y muchas otras aplicaciones para proce‐
sar imágenes WebP, contenía un desbordamiento de heap en la función BuildHuffmanTable(). Al
parsear imágenes WebP especialmente diseñadas con datos de codificación Huffman malformados,
la función escribía más allá de los límites del búfer asignado.

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
El Ataque ﴾Paso a Paso﴿
1. Vector de Entrada:
Atacante embebe imagen WebP maliciosa en página web
O la envía vía aplicaciones de mensajería ﴾WhatsApp, Telegram, Signal﴿
O incluye en documento ﴾email, Word, PDF﴿
2. Trigger:
Navegador/aplicación de víctima intenta decodificar la imagen
Parser WebP procesa datos Huffman malformados
BuildHuffmanTable() calcula tamaño de tabla incorrectamente
3. Explotación:
El desbordamiento corrompe metadatos del heap
O corrompe objetos adyacentes con función pointers
Atacante controla datos del desbordamiento para conseguir primitivas
4. Resultado:
Ejecución de código arbitrario en contexto del proceso
En navegadores: código ejecuta en proceso renderer
Impacto
Ejecución remota de código sin interacción del usuario más allá de ver una página web o
abrir una imagen
Zero‐day explotado activamente antes de su divulgación pública ﴾septiembre 2023﴿
Billones de dispositivos afectados en múltiples plataformas:
• Windows, macOS, Linux ﴾desktop﴿
• Android, iOS ﴾mobile﴿
• Cualquier software usando libWebP ﴾Electron apps, etc.﴿
Por Qué Esta Vulnerabilidad es Emblemática:
1. Riesgo de Cadena de Suministro: Un bug en libWebP afectó docenas de aplicaciones ma‐
yores
2. Ubicuidad de Imágenes: Las imágenes son procesadas automáticamente y son ubicuas
3. Técnicas Modernas de Heap: Los atacantes combinaron heap overflow con técnicas de by‐
pass de ASLR
Mitigación
libWebP 1.3.2 ﴾septiembre 2023﴿: Corrigió verificación de límites en BuildHuffmanTable()
Chrome 116.0.5845.187: Parche de emergencia
Firefox 117.0.1: Parche de emergencia
Otros software afectado lanzó actualizaciones coordinadas
Observaciones
Los desbordamientos de heap en parsers de imágenes son particularmente peligrosos porque: ‐
Las imágenes son procesadas automáticamente sin confirmación del usuario ‐ Son compartidas
rutinariamente y consideradas “seguras” ‐ Parsers de imagen optimizan rendimiento, sacrificando
verificaciones de seguridad ‐ La complejidad de formatos de compresión ﴾Huffman, LZW, etc.﴿in‐
troduce bugs

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
### 2.1.4.
### 1.1.4 Lectura Fuera de Límites ﴾Out‐of‐Bounds Read / Info Leak﴿
Descripción General
Una lectura fuera de límites ﴾Out‐of‐Bounds Read﴿ocurre cuando un programa lee memoria pasando
los límites de un búfer sin modificarla. Aunque no permite escritura directa, frecuentemente se
utiliza para: ‐ Filtrar punteros para bypass de ASLR/KASLR ‐ Exponer metadatos de objetos para
construir primitivas más poderosas ‐ Revelar diseño de memoria del kernel para explotación
confiable
Rol en Cadenas de Explotación:
┌─────────────────────────────────────────────────────────────┐
│
### CADENA DE EXPLOTACIÓN TÍPICA
│
├─────────────────────────────────────────────────────────────┤
│
┌───────────────────┐
│
│
### │1. OOB READ
│←Filtrar direcciones de kernel
│
│
│
(Info Leak)
│
│
│
└─────────┬─────────┘
│
│
│
│
│
▼
│
│
┌───────────────────┐
│
│
### │2. KASLR BYPASS
│←Calcular direcciones reales
│
│
│
│
│
│
└─────────┬─────────┘
│
│
│
│
│
▼
│
│
┌───────────────────┐
│
│
│3. WRITE PRIMITIVE│←Otra vulnerabilidad (UAF, overflow)│
│
│
│
│
│
└─────────┬─────────┘
│
│
│
│
│
▼
│
│
┌───────────────────┐
│
│
│4. CODE EXECUTION │←Escribir a ubicación conocida
│
│
│
│
│
│
└───────────────────┘
│
└─────────────────────────────────────────────────────────────┘
Caso de Estudio: CVE‐2024‐53108 — Linux AMDGPU Display Driver
Campo
Detalle
Producto Afectado
Linux Kernel ﴾driver AMD Display﴿
Tipo
Out‐of‐Bounds Read ﴾slab‐out‐of‐bounds﴿
Vector
Datos EDID/display maliciosos

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
Campo
Detalle
Severidad
Media‐Alta
Diff del Parche
git.kernel.org
El Bug
En el driver de display AMD del kernel Linux, la ruta de parsing EDID/VSDB ﴾Video Specification
Database﴿tenía verificación insuficiente de límites al extraer identificadores de capacidades. Cuando
procesaba datos EDID con campos de longitud manipulados, el driver leía más allá de los límites
del búfer EDID asignado.
El bug fue detectado por KASAN ﴾Kernel AddressSanitizer﴿que reportó acceso slab‐out‐of‐bounds
durante la extracción de datos del display.
El Ataque
Un flujo de datos EDID/display maliciosamente construido podría: 1. Disparar lectura OOB en espa‐
cio de kernel 2. Exponer contenidos de memoria de kernel ﴾incluyendo punteros﴿3. Proporcionar
información para evadir KASLR 4. Ser encadenado con otra vulnerabilidad de escritura para explo‐
tación completa
Impacto
Divulgación de información: Exposición de contenido de memoria del kernel
Potencial inestabilidad del sistema: Lectura de memoria inválida puede causar oops
Habilitador de explotación: Utilizable para evadir KASLR en cadenas de explotación más
complejas
Por Qué las OOB Reads Importan:
En contextos de kernel: ‐ KASLR es una mitigación fundamental contra explotación ‐ Sin info
leak, escritura ciega falla ‐ el atacante necesita saber dónde escribir ‐ OOB reads son el primer
paso de la mayoría de exploits modernos de kernel
Mitigación
Las actualizaciones del kernel ajustaron la validación de longitud: ‐ Verificar que bLength sea >=
tamaño mínimo esperado ‐ Validar offsets antes de acceder a campos ‐ Asegurar que todas las
lecturas permanezcan dentro de los límites del búfer EDID
Observaciones
Las lecturas OOB puras son valiosas para construir cadenas de explotación confiables: ‐ Proporcio‐
nan información necesaria para bypass de ASLR/KASLR ‐ Son frecuentemente la primera etapa de
exploits multi‐paso ‐ En kernel, derrotar KASLR es pivotal para explotación confiable
### 2.1.5.
### 1.1.5 Uso de Memoria No Inicializada ﴾Uninitialized Memory Use﴿
Descripción General
Usar memoria de pila/heap/pool antes de que sea inicializada puede exponer contenidos residuales
de operaciones previas. Estos contenidos pueden incluir: ‐ Punteros previos ﴾direcciones del kernel

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
para bypass de KASLR﴿‐ Flags de capacidad ﴾para escalada de privilegios﴿‐ Campos de estructura
﴾para confusión de tipos﴿
Por Qué Es Peligroso:
// Código vulnerable - variable no inicializada
void vulnerable_function(struct netlink_msg *msg) {
struct nft_pipapo_match *m; // ←NO INICIALIZADO
// Si algún camino de código no asigna 'm'...
if (some_condition(msg)) {
m = find_match(msg);
}
// ... pero 'm' se usa incondicionalmente
copy_to_user(response, &m, sizeof(m)); // ←Filtra pila residual
}
Caso de Estudio: CVE‐2024‐26581 — Linux Kernel Netfilter
Campo
Detalle
Producto Afectado
Linux Kernel ﴾subsistema netfilter﴿
Tipo
Uso de Variable No Inicializada
Vector
Mensajes netlink locales
Severidad
Alta
PoC Disponible
sploitus.com/exploit?id=A4D521EE‐225F‐57D5‐8C31‐
### 9F1C86D066B6
El Bug
El subsistema netfilter del kernel Linux contenía una vulnerabilidad de variable no inicializada en el
componente nf_tables. Al procesar mensajes netlink para configurar reglas de firewall, la función
nft_pipapo_walk() fallaba en inicializar una variable local antes de su uso.
La variable no inicializada de pila podría contener datos residuales de llamadas a funciones previas,
incluyendo punteros del kernel y direcciones de memoria sensibles.
El Ataque ﴾Paso a Paso﴿
1. Obtener Capacidades:
Atacante está en espacio de nombres de usuario no privilegiado
User namespaces otorgan CAP_NET_ADMIN ﴾default en Ubuntu, Debian﴿
2. Disparar el Bug:
Enviar mensajes netlink específicos de configuración de nf_tables
Causar que se ejecute la ruta de código con variable no inicializada
La variable se lee y se copia de vuelta al espacio de usuario
3. Recolectar Información:
Repetir el trigger múltiples veces
Analizar datos retornados

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
Extraer direcciones de kernel ﴾heap, stack, código﴿
4. Explotar con Información:
Usar direcciones filtradas para evadir KASLR
Combinar con otra vulnerabilidad de escritura de netfilter
Lograr escalada de privilegios completa ﴾LPE chain﴿
Impacto
Divulgación de información →bypass de KASLR
Las direcciones del kernel filtradas permiten explotación confiable de otras vulnerabilidades
Particularmente peligrosa cuando se combina con otros bugs de netfilter para cadenas LPE
completas
Peligro del Combo: Netfilter + User Namespaces
Muchas distribuciones Linux permiten user namespaces no privilegiados por defecto: ‐ Ubuntu:
Habilitado por defecto ‐ Debian: Habilitado por defecto ‐ Fedora: Habilitado por defecto
Esto significa que CAP_NET_ADMIN está disponible para usuarios no privilegiados, haciendo que bugs
de netfilter sean explotables sin privilegios root.
Mitigación
Linux kernel 6.8‐rc1 ﴾febrero 2024﴿: ‐ Añadió inicialización apropiada: struct nft_pipapo_match *m
= NULL; ‐ Habilitó inicializadores designados para estructuras de pila ‐ Habilitó advertencias de
compilador más estrictas ﴾-Wuninitialized﴿para netfilter
Observaciones
Las lecturas de memoria no inicializada son frecuentemente la primera etapa en cadenas de ex‐
plotación: ‐ Proporcionan reducciones de entropía para evadir mitigaciones modernas ‐ Son parti‐
cularmente valiosas en explotación de kernel donde KASLR es esencial ‐ La combinación de user
namespaces no privilegiados y fugas de netfilter hace esta clase de vulnerabilidad accesible a ata‐
cantes locales sin requerir privilegios root
### 2.1.6.
### 1.1.6 Errores de Conteo de Referencias ﴾Reference Counting Bugs﴿
Descripción General
Los errores de conteo de referencias ocurren cuando hay incrementos/decrementos incorrectos o
desbordamientos en contadores que controlan el tiempo de vida de objetos ﴾sistemas de archivos,
networking, drivers﴿. Estos bugs pueden llevar a: ‐ Liberación prematura: Objeto liberado mientras
referencias aún existen →UAF ‐ Memory leak: Objeto nunca liberado →agotamiento de memoria
‐ Double‐free: Decremento excesivo →corrupción de heap
Mecánica de Reference Counting:
┌─────────────────────────────────────────────────────────────┐
│
### GESTIÓN DE CONTEO DE REFERENCIAS
│
├─────────────────────────────────────────────────────────────┤
│
│
│
## CORRECTO:
│

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
│
┌─────────┐
┌─────────┐
┌─────────┐
│
│
│ref = 1 │──►│ref = 2 │──►│ref = 1 │──►free()
│
│
│(alloc) │
│(add)
│
│(drop)
│
│
│
└─────────┘
└─────────┘
└─────────┘
│
│
│
│
### BUG - LIBERACIÓN PREMATURA:
│
│
┌─────────┐
┌─────────┐
┌─────────┐
│
│
│ref = 1 │──►│ref = 0 │──►│USE
### │←UAF!
│
│
│(alloc) │
│(drop)
│
│(bug)
│
│
│
└─────────┘
└─────────┘
└─────────┘
│
│
│
│
### BUG - DESBORDAMIENTO DE REFCOUNT:
│
│
┌─────────┐
┌─────────┐
┌─────────┐
│
│
│ref=MAX │──►│ref = 0 │──►│free()
│←¡Aún usado!│
│
│
│
│(overflow)│
│(wrong) │
│
│
└─────────┘
└─────────┘
└─────────┘
│
└─────────────────────────────────────────────────────────────┘
Caso de Estudio: CVE‐2022‐32250 — Linux Netfilter nf_tables
Campo
Detalle
Producto Afectado
Linux Kernel ﴾nf_tables﴿
Tipo
Error de Conteo de Referencias →UAF
Vector
User namespaces no privilegiados
Severidad
Crítica
Exploit Público
github.com/theori‐io/CVE‐2022‐32250‐exploit
El Bug
El subsistema netfilter del kernel Linux ﴾net/netfilter/nf_tables_api.c﴿tenía un error de conteo
de referencias en el componente nf_tables. Una verificación incorrecta de NFT_STATEFUL_EXPR fallaba
en rastrear adecuadamente los tiempos de vida de objetos de expresión durante actualizaciones
de reglas, llevando a destrucción prematura de objetos mientras referencias aún existían.
El Ataque ﴾Paso a Paso﴿
1. Configuración del Entorno:
Atacante crea user namespace no privilegiado
Esto otorga CAP_NET_ADMIN dentro del namespace
Permite manipular reglas de nf_tables
2. Disparar el Bug:
Crear expresiones stateful en reglas de nf_tables
Modificar reglas en secuencias específicas
Causar que el kernel decremente refcount incorrectamente
3. Condición UAF:

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
El kernel libera un objeto de expresión
Otra referencia al objeto aún existe
El código continúa usando el puntero colgante
4. Explotación:
Usar técnicas de heap spray para reclamar la memoria liberada
Colocar datos controlados por atacante en la ubicación
Usar el puntero colgante para lograr lectura/escritura arbitraria
5. Escalada de Privilegios:
Modificar credenciales del proceso ﴾task_struct->cred﴿
O sobrescribir punteros de función del kernel
Obtener root desde usuario no privilegiado
Impacto
Escalada de privilegios local de cualquier usuario a root en sistemas que permiten names‐
paces no privilegiados
La primitiva UAF puede explotarse para lectura/escritura arbitraria de memoria del kernel
Afectó kernels Linux desde 4.1 ﴾2015﴿hasta 5.18.1 ﴾2022﴿‐ más de 7 años de vulnerabilidad
Exploit público disponible hace esta vulnerabilidad especialmente peligrosa
Distribuciones Afectadas ﴾namespaces habilitados por defecto﴿: ‐ Ubuntu ‐ Debian
‐ Fedora ‐ Y muchas otras
Mitigación
Linux kernel 5.18.2+ corrigió la lógica de conteo de referencias: ‐ Añadió incrementos/decrementos
de refcount explícitos en los puntos apropiados del código ‐ Aseguró rastreo adecuado del tiempo
de vida durante operaciones de reglas ‐ Agregó validaciones adicionales en expresiones stateful
Observaciones
Los bugs de conteo de referencias: ‐ Son sutiles: Pueden llevar a condiciones de liberación prema‐
tura →use‐after‐free ‐ O desbordamiento de refcount →free mientras referencias permanecen
‐ Son particularmente peligrosos en código del kernel donde gestión del tiempo de vida de ob‐
jetos es crítica ‐ La accesibilidad vía user namespaces no privilegiados hizo esta vulnerabilidad
particularmente impactante para escalada de privilegios local
### 2.1.7.
### 1.1.7 Desreferencia de Puntero Nulo ﴾NULL Pointer Dereference﴿
Descripción General
Desreferenciar un puntero NULL en código privilegiado. Mientras los sistemas modernos típicamen‐
te previenen el mapeo de páginas NULL en espacio de usuario ﴾mitigando técnicas históricas de
escalada de privilegios﴿, las desreferencias de puntero NULL en kernel siguen siendo fuente signi‐
ficativa de vulnerabilidades de: ‐ Denegación de Servicio ﴾kernel panic inmediato﴿‐ Divulgación
de Información ﴾en algunos contextos﴿‐ Escalada de Privilegios ﴾en configuraciones específicas
legacy﴿
Evolución de la Mitigación:
┌─────────────────────────────────────────────────────────────┐

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
│
### EVOLUCIÓN DE PROTECCIONES CONTRA NULL DEREF
│
├─────────────────────────────────────────────────────────────┤
│
│
│
ANTES (Linux < 2.6.23):
│
│
┌─────────────────────────────────────────────────────┐
│
│
│Espacio de Usuario podía mapear página 0
│
│
│
│NULL deref →Ejecuta código de atacante →ROOT
│
│
│
└─────────────────────────────────────────────────────┘
│
│
│
│
DESPUÉS (Linux moderno con mmap_min_addr):
│
│
┌─────────────────────────────────────────────────────┐
│
│
│Página 0 no puede ser mapeada por usuario
│
│
│
│NULL deref →Kernel Panic →DoS (pero no RCE)
│
│
│
└─────────────────────────────────────────────────────┘
│
│
│
│
/proc/sys/vm/mmap_min_addr = 65536 (típico)
│
└─────────────────────────────────────────────────────────────┘
Caso de Estudio: CVE‐2023‐52434 — Linux SMB Client
Campo
Detalle
Producto Afectado
Linux Kernel ﴾cliente SMB/CIFS﴿
Tipo
Desreferencia de Puntero Nulo
Vector
Servidor SMB malicioso
Severidad
Alta ﴾CVSS 8.0﴿
Vector de Ataque
Red adyacente
El Bug
La implementación del cliente SMB del kernel Linux contenía una vulnerabilidad de desreferencia
de puntero nulo en la función smb2_parse_contexts(). Al parsear respuestas del servidor durante
el establecimiento de conexión SMB2/SMB3, el código fallaba en validar apropiadamente offsets y
longitudes de estructuras de contexto de creación antes de desreferenciar punteros.
Los contextos malformados con offsets inválidos podían causar que el kernel accediera a direcciones
de memoria no mapeadas, disparando una desreferencia de puntero nulo.
El Ataque ﴾Paso a Paso﴿
1. Vector de Entrada:
Servidor SMB malicioso o comprometido en la red
O ataque man‐in‐the‐middle modificando respuestas SMB
2. Trigger:

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
Servidor envía respuestas SMB2_CREATE con estructuras de contexto de creación inváli‐
das
Offsets apuntan fuera de los datos válidos
O longitudes calculan a direcciones NULL
3. Crash:
Cliente Linux intenta montar el share o acceder a archivos
Kernel parsea contextos malformados sin verificación de límites
Acceso a dirección inválida →kernel panic
4. Resultado:
BUG: unable to handle page fault for address: ffff8881178d8cc3
#PF: supervisor read access in kernel mode
...
Call Trace:
smb2_parse_contexts+0x...
Impacto
Denegación de servicio afectando kernels Linux desde 5.3 hasta 6.7‐rc5
La desreferencia de puntero nulo causaba kernel panic inmediato
Cualquier usuario con permiso para montar shares SMB podía disparar la vulnerabilidad
Explotable en entornos multi‐usuario donde montaje SMB está permitido
Contextos de Explotación: ‐ Red corporativa: Usuario malicioso levanta servidor SMB falso ‐ WiFi
público: Atacante hace MITM de conexiones SMB ‐ Red comprometida: Servidor SMB legítimo
comprometido envía respuestas maliciosas
Mitigación
Parches del kernel Linux ﴾versiones 5.4.277, 5.10.211, 5.15.150, 6.1.80 y 6.6.8+﴿: ‐ Añadieron vali‐
dación comprehensiva de offsets de contextos de creación ‐ Verifican que longitudes no excedan
límites del búfer ‐ Aseguran que toda aritmética de punteros permanezca dentro de límites asigna‐
dos
Observaciones
Las desreferencias de puntero nulo en parsers de protocolos de red son particularmente peligrosas
porque: ‐ Pueden ser disparadas remotamente por servidores maliciosos ‐ O mediante ataques
MITM modificando tráfico de red ‐ Mientras las protecciones modernas del kernel previenen el
mapeo de página NULL ﴾mitigando RCE histórico﴿‐ El impacto de DoS permanece crítico para
disponibilidad
### 2.1.8.
### 1.1.8 Conclusiones de Corrupción de Memoria
Hallazgos Clave:
1. La corrupción de memoria sigue siendo prevalente: A pesar de décadas de investigación en
seguridad, los bugs de corrupción de memoria continúan plagando software, especialmente
en bases de código C/C++.

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
2. La defensa en profundidad es esencial: Cada ejemplo del mundo real muestra atacantes
evadiendo múltiples mecanismos de protección ﴾DEP, ASLR, CET, XFG, safe‐linking﴿.
3. Las mitigaciones modernas elevan la barrera pero no eliminan el riesgo: Mientras tecno‐
logías como CET shadow stack y safe‐linking dificultan la explotación, atacantes determinados
continúan encontrando bypasses.
4. Las causas raíz son similares, pero los contextos difieren: Bugs de stack, heap y UAF com‐
parten causas raíz comunes ﴾verificación inadecuada de límites, gestión de tiempo de vida﴿
pero requieren diferentes técnicas de explotación.
5. Los componentes legacy permanecen vulnerables: Vulnerabilidades de años de antigüe‐
dad en parsers de office y manejadores de archivos continúan siendo explotadas debido a
ciclos de parcheo lentos.
Preguntas de Discusión:
1. ¿Qué puntos en común ves a través de las clases de vulnerabilidades de corrupción de me‐
moria cubiertas?
2. ¿Por qué persisten las vulnerabilidades de corrupción de memoria a pesar de décadas de
investigación en lenguajes memory‐safe?
3. ¿Cómo difieren las técnicas de explotación entre vulnerabilidades de stack, heap y UAF?
4. ¿Qué mecanismos de defensa fueron evadidos en cada ejemplo, y qué nos dice eso sobre el
estado actual de la mitigación de exploits?
### 2.2.
### 1.2 Vulnerabilidades Lógicas y Condiciones de Carrera
Las vulnerabilidades lógicas no involucran corrupción de memoria pero pueden ser igualmente
peligrosas. Esta sección cubre condiciones de carrera, bugs TOCTOU, double‐fetch, fallas de auten‐
ticación, primitivas de escritura arbitraria y mal uso de sincronización.
Recursos de Lectura: ‐ “Web Application Security, 2nd Edition” por Andrew Hoffman ‐ Capítulo 18:
“Business Logic Vulnerabilities” ‐ Portswigger Logic Flaws ‐ Time‐of‐check Time‐of‐use ﴾TOCTOU﴿
Vulnerabilities ‐ Microsoft: Avoiding Race Conditions
### 2.2.1.
### 1.2.1 Condiciones de Carrera ﴾Race Conditions﴿
Descripción General
Una condición de carrera ocurre cuando el comportamiento del software depende del timing relati‐
vo de eventos, como el orden en que los hilos ejecutan. Cuando múltiples hilos o procesos acceden
a recursos compartidos sin sincronización apropiada, un atacante puede manipular el timing para
causar comportamiento inesperado.
Patrones Comunes:
1. Condiciones de Carrera en Sistema de Archivos: Verificar permisos de un archivo, luego
abrirlo ﴾atacante intercambia el archivo entre verificación y apertura﴿

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
2. Double‐Fetch: Kernel lee memoria de modo usuario dos veces, atacante la modifica entre
lecturas
3. Primitivas de Sincronización: Uso faltante o incorrecto de locks, mutexes u operaciones
atómicas
Caso de Estudio: CVE‐2024‐26218 — Windows Kernel TOCTOU
Campo
Detalle
Producto Afectado
Windows Kernel
Tipo
Condición de Carrera TOCTOU
Vector
Local
Severidad
Alta ﴾CVSS 7.7﴿
El Bug
Una condición de carrera Time‐of‐Check Time‐of‐Use en el Windows Kernel permitía a un atacante
explotar una ventana de timing entre la validación y el uso de recursos del kernel. La vulnerabilidad
ocurría cuando el kernel verificaba permisos o estados de recursos pero no realizaba atómicamente
la operación subsecuente, permitiendo a un hilo en carrera modificar el estado del recurso entre
verificación y uso.
El Ataque ﴾Paso a Paso﴿
┌─────────────────────────────────────────────────────────────┐
│
### ATAQUE TOCTOU
│
├─────────────────────────────────────────────────────────────┤
│
│
│
### KERNEL
### ATACANTE
│
│
──────
────────
│
│
│
│
│
│
│1. Verificar permisos
│
│
│
│
del recurso
│
│
│
│
resultado: OK
│
│
│
│
║
│
│
│
│
║═══════════════════│
│
│
│
║
### VENTANA DE
│2. Modificar
│
│
│
║
### CARRERA
│
estado del
│
│
│
║
│
recurso
│
│
│
║═══════════════════│
│
│
│
▼
│
│
│
│3. Usar recurso (ahora
│
│
│
│
modificado por atacante)
│
│
│
│
│
│
│
│4. RESULTADO: Escalada de
│
│

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
│
│
privilegios
│
│
└─────────────────────────────────────────────────────────────┘
Impacto
Escalada de privilegios local de usuario de bajos privilegios a SYSTEM
Afectó Windows 10, Windows 11 y Windows Server 2019/2022
Parcheado en abril 2024 ﴾Microsoft Patch Tuesday﴿
Por Qué Es Difícil de Corregir:
Las condiciones de carrera requieren: ‐ Operaciones atómicas de check‐and‐use ‐ Mecanismos de
bloqueo apropiados a través de subsistemas complejos del kernel ‐ Copia defensiva para asegurar
que el estado verificado coincida con el estado usado ‐ Muchas operaciones del kernel asumen
ejecución secuencial sin considerar modificación concurrente
Mitigación
Microsoft implementó: ‐ Operaciones atómicas de verificación y uso ‐ Mecanismos de bloqueo
apropiados para recursos compartidos ‐ Copia defensiva para asegurar coincidencia de estado ve‐
rificado/usado
Observaciones
Las condiciones de carrera son difíciles de reproducir pero proporcionan explotación confiable cuan‐
do el timing es controlado. Requieren comprensión profunda del modelo de concurrencia del sis‐
tema objetivo.
### 2.2.2.
### 1.2.2 Vulnerabilidades TOCTOU ﴾Time‐of‐Check Time‐of‐Use﴿
Descripción General
TOCTOU es un tipo específico de condición de carrera donde hay una brecha entre verificar una
condición y usar el resultado. Durante esa brecha, la condición puede cambiar, invalidando la veri‐
ficación.
Ejemplo Clásico — Ataques con Symlinks:
// Programa vulnerable
1. if (access("/tmp/important_file", W_OK) == 0) {
### // VERIFICACIÓN
// [VENTANA DE CARRERA] Atacante: ln -s /etc/passwd /tmp/important_file
2.
fd = open("/tmp/important_file", O_WRONLY);
### // USO
write(fd, data, size);
// ¡Escribe a /etc/passwd!
}
Impacto del Mundo Real:
Escalada de Privilegios: Bugs TOCTOU en programas privilegiados permiten a usuarios no
privilegiados modificar archivos protegidos
Bypass de Verificaciones de Seguridad: Verificaciones de autenticación o autorización pue‐
den ser eludidas si el recurso cambia entre verificación y uso
Corrupción de Datos: Modificaciones inesperadas de archivos pueden corromper el estado
del sistema

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
Caso de Estudio: CVE‐2025‐11001/11002 — 7‐Zip Symlink Path Traversal
Campo
Detalle
Producto Afectado
7‐Zip
Tipo
TOCTOU / Path Traversal via Symlink
Vector
Archivo ZIP malicioso
Severidad
Alta
El Bug
La validación impropia de objetivos de symlinks en la extracción de ZIP permitía traversal de direc‐
torios vía symlinks maliciosos, habilitando escrituras fuera del directorio de extracción previsto.
El Ataque:
1. Preparación del Archivo Malicioso:
Atacante crea archivo ZIP/RAR especialmente diseñado
Incluye un symlink: link.txt -> ../../../etc/cron.d/malicious
Incluye archivo link.txt con contenido malicioso
2. Extracción:
Usuario extrae archivo en /home/user/downloads/
7‐Zip crea symlink que apunta fuera del directorio
Luego escribe contenido al symlink
3. Resultado:
Archivo escrito a /etc/cron.d/malicious
Ejecución de código como root cuando cron procesa el archivo
Impacto
Escritura arbitraria de archivos llevando a potencial RCE en contexto de usuario
Dependiendo del directorio objetivo ﴾ej. ~/.bashrc, /etc/cron.d/, ~/.ssh/authorized_keys﴿,
puede permitir escalada de privilegios
Afecta a todos los usuarios que extraen archivos de fuentes no confiables
Mitigación
Las actualizaciones abordaron: ‐ Validación de conversión y lógica de symlinks durante extracción
‐ Verificación de que rutas de destino permanezcan dentro del directorio de extracción ‐ Rechazo
de symlinks que apuntan fuera del contexto de extracción
Observaciones
Las vulnerabilidades TOCTOU en parsers de archivos son particularmente peligrosas porque los
usuarios frecuentemente extraen archivos de fuentes no confiables sin verificación adicional.
### 2.2.3.
### 1.2.3 Vulnerabilidades Double‐Fetch
Descripción General

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
Un double‐fetch ocurre cuando el código del kernel lee memoria de modo usuario dos veces, asu‐
miendo que no cambiará entre lecturas. Un atacante con múltiples hilos puede modificar la memoria
después de la primera lectura pero antes de la segunda, causando que el código del kernel opere
sobre datos inconsistentes.
Mecánica:
┌─────────────────────────────────────────────────────────────┐
│
### VULNERABILIDAD DOUBLE-FETCH
│
├─────────────────────────────────────────────────────────────┤
│
│
│
### KERNEL
ESPACIO USUARIO (Atacante)
│
│
──────
─────────────────────────
│
│
│
│
│
│
│1. Primera lectura
│
│
│
│
valor = *userptr
│
│
│
│
(validar: valor == 1)
│
│
│
│
║
│
│
│
│
║════════════════
│
│
│
│
║
### VENTANA
│2. *userptr = 999
│
│
│
║════════════════
│
│
│
│
▼
│
│
│
│3. Segunda lectura
│
│
│
│
usar *userptr
│
│
│
│
(¡ahora es 999!)
│
│
│
│
│
│
│
│4. Bug: código usa valor
│
│
│
│
no validado (999)
│
│
└─────────────────────────────────────────────────────────────┘
Caso de Estudio: CVE‐2023‐4155 — Linux KVM AMD SEV Double‐Fetch
Campo
Detalle
Producto Afectado
Linux Kernel ﴾KVM AMD SEV﴿
Tipo
Double‐Fetch →Stack Overflow
Vector
Invitado VM malicioso
Severidad
Alta
El Bug
Una condición de carrera double‐fetch en la implementación KVM AMD Secure Encrypted Virtua‐
lization del kernel Linux. Invitados KVM usando SEV‐ES o SEV‐SNP con múltiples vCPUs podían
disparar la vulnerabilidad manipulando memoria compartida de invitado que el hypervisor lee dos
veces sin sincronización apropiada.

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
El Patrón del Bug:
El manejador VMGEXIT en el hypervisor leía memoria controlada por el invitado para determinar qué
operación realizar. Un atacante podía modificar esta memoria entre la primera lectura ﴾validación﴿
y la segunda lectura ﴾uso﴿, causando comportamiento inconsistente.
El Ataque ﴾Paso a Paso﴿
1. Primera Lectura: Hypervisor lee memoria del invitado para validar el código de razón de
### VMGEXIT
2. Ventana de Carrera: El hilo vCPU del atacante modifica la memoria del invitado conteniendo
el código de razón
3. Segunda Lectura: Hypervisor lee el valor modificado y procesa una operación diferente a la
validada
4. Resultado: Invocación recursiva del manejador VMGEXIT, llevando a desbordamiento de pila
Impacto
Denegación de servicio ﴾DoS﴿vía desbordamiento de pila en hypervisor
En configuraciones del kernel sin páginas de guarda de pila ﴾CONFIG_VMAP_STACK﴿, potencial
escape de invitado a host
Afecta entornos de virtualización con AMD SEV habilitado
Por Qué Es Difícil de Corregir:
Los double‐fetch requieren: ‐ Identificar todas las ubicaciones donde código del hypervisor lee
memoria del invitado múltiples veces ‐ Copiar datos del invitado a memoria del hypervisor una vez
‐ Operar sobre la copia estable ‐ Consideraciones de rendimiento hacen la copia defensiva costosa
en rutas calientes de virtualización
Mitigación
Los parches del kernel Linux: ‐ Añadieron sincronización apropiada para asegurar que el código de
razón VMGEXIT se lea una vez ‐ Almacenaron el valor en variable local antes de validación y uso ‐
Añadieron verificaciones para prevenir invocación recursiva del manejador
Observaciones
Las vulnerabilidades double‐fetch son particularmente difíciles de corregir y particularmente peli‐
grosas en contextos de hypervisor donde el escape invitado→host tiene impacto crítico.
### 2.2.4.
### 1.2.4 Fallas Lógicas en Autenticación
Descripción General
Bugs en el flujo lógico de verificaciones de autenticación o autorización que permiten a atacantes
evadir límites de seguridad sin explotar corrupción de memoria.
Tipos de Fallas Lógicas de Autenticación:

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
Tipo
Descripción
Ejemplo
Bypass de
Autenticación
Acceder sin credenciales
Solicitudes malformadas
evaden verificación
Escalada Vertical
Usuario se convierte en admin
Manipulación de parámetros
de rol
Escalada
Horizontal
Usuario A accede a datos de B
IDOR ﴾Insecure Direct Object
Reference﴿
Confusión de
Estado
Estado de sesión inconsistente
Tokens de reseteo
reutilizables
Caso de Estudio: CVE‐2024‐0012 — Palo Alto PAN‐OS Authentication Bypass
Campo
Detalle
Producto Afectado
Palo Alto Networks PAN‐OS
Tipo
Bypass de Autenticación
Vector
Interfaz web de administración
Severidad
Crítica
PoC Disponible
github.com/0xjessie21/CVE‐2024‐0012
El Bug
El software PAN‐OS de Palo Alto Networks contenía una vulnerabilidad de bypass de autenticación
en su interfaz web de administración. La vulnerabilidad permitía a un atacante no autenticado eva‐
dir completamente las verificaciones de autenticación y obtener privilegios de administrador sin
proporcionar ninguna credencial.
El Ataque:
1. Atacante tiene acceso de red a la interfaz web de administración de PAN‐OS
2. Envía solicitudes especialmente diseñadas que evaden la lógica de autenticación
3. No se requieren credenciales ni interacción del usuario
4. Atacante obtiene acceso directo de administrador
Impacto
Bypass completo de autenticación permitiendo a atacantes remotos no autenticados obte‐
ner privilegios de administrador de PAN‐OS
Habilitaba realizar acciones administrativas:
• Manipular configuraciones de firewall
• Crear reglas para permitir tráfico malicioso
• Extraer configuraciones y credenciales
Podía encadenarse con otras vulnerabilidades como CVE‐2024‐9474 para explotación adi‐
cional
Mitigación

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
Palo Alto lanzó parches en versiones 10.2.12, 11.0.6, 11.1.5 y 11.2.4 ﴾noviembre 2024﴿: ‐ Corrigieron
la lógica de validación de autenticación ‐ Recomendaron restringir acceso a la interfaz de adminis‐
tración solo a IPs internas confiables como defensa en profundidad
Observaciones
Las fallas lógicas en autenticación y autorización pueden llevar a: ‐ Escalada de privilegios ﴾usuario
se convierte en admin﴿‐ Escalada horizontal ﴾usuario A accede a datos de usuario B﴿‐ Bypass de
autenticación ﴾acceso sin credenciales﴿
Todo sin corrupción de memoria. Verificaciones faltantes, confusión de estado, manipulación de
parámetros y fallas de gestión de sesión son patrones comunes.
### 2.2.5.
### 1.2.5 Escritura Arbitraria ﴾Write‐What‐Where﴿
Descripción General
Una primitiva de escritura arbitraria permite al atacante escribir un valor controlado a una dirección
controlada. Esta es una de las primitivas de explotación más poderosas, ya que permite modificar
cualquier ubicación de memoria.
Usos de Escritura Arbitraria:
┌─────────────────────────────────────────────────────────────┐
│
### PRIMITIVAS DE ESCRITURA ARBITRARIA
│
├─────────────────────────────────────────────────────────────┤
│
│
│
### 1. SOBRESCRIBIR CREDENCIALES
│
│
task_struct->cred->uid = 0
→Convertirse en root
│
│
│
│
### 2. CORROMPER PUNTEROS DE FUNCIÓN
│
│
callback_ptr = &shellcode
→Ejecución de código
│
│
│
│
### 3. DESHABILITAR PROTECCIONES
│
│
security_callback = NULL
→Bypass de seguridad
│
│
│
│
### 4. MODIFICAR POLÍTICAS
│
│
selinux_enforcing = 0
→Deshabilitar SELinux
│
└─────────────────────────────────────────────────────────────┘
Caso de Estudio: CVE‐2024‐21338 — Windows AppLocker Driver Arbitrary Function Call
Campo
Detalle
Producto Afectado
Windows AppLocker driver ﴾appid.sys﴿
Tipo
Llamada Arbitraria a Función →Escritura Arbitraria
Vector
Local ﴾servicio local o impersonación de admin﴿

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
Campo
Detalle
Severidad
Alta
PoC Disponible
github.com/hakaioffsec/CVE‐2024‐21338
El Bug
El driver de Windows AppLocker ﴾appid.sys﴿contenía una vulnerabilidad en su manejador IOCTL
﴾código de control 0x22A018﴿que permitía a un atacante con privilegios de servicio local llamar
punteros de función del kernel arbitrarios con argumentos controlados. El IOCTL estaba diseñado
para aceptar punteros de función del kernel para operaciones de archivos pero permanecía accesi‐
ble desde espacio de usuario sin validación apropiada.
El Ataque ﴾Paso a Paso﴿
1. Obtener Acceso:
Atacante impersona la cuenta de servicio local
O tiene acceso admin que puede impersonar
2. Enviar IOCTL Malicioso:
Enviar solicitud IOCTL especialmente diseñada a \Device\AppId
Incluir punteros de función maliciosos en el búfer de entrada
3. Explotar Gadget:
Escoger la función gadget correcta
Realizar copia de 64 bits a dirección arbitraria del kernel
Objetivo específico: Campo PreviousMode en estructura KTHREAD del hilo actual
4. Corrupción de PreviousMode:
Corromper PreviousMode a KernelMode ﴾0﴿
Esto bypasea verificaciones de modo kernel en syscalls como NtReadVirtualMemory y
NtWriteVirtualMemory
Otorga capacidades de lectura/escritura arbitraria del kernel desde modo usuario
5. Post‐Explotación:
Realizar manipulación directa de objetos del kernel ﴾DKOM﴿
Deshabilitar callbacks de seguridad
Cegar telemetría ETW
Suspender procesos de seguridad protegidos por PPL
Impacto
Esta vulnerabilidad fue usada por el sofisticado rootkit FudModule para: ‐ Escalada de privilegios
local de servicio local ﴾o admin vía impersonación﴿a lectura/escritura arbitraria nivel kernel ‐ Ata‐
que de kernel verdaderamente fileless ‐ sin necesidad de soltar o cargar drivers personalizados
‐ Manipulación directa de objetos del kernel ﴾DKOM﴿‐ Deshabilitación de callbacks de seguridad ‐
Cegar telemetría ETW ‐ Suspender procesos de seguridad protegidos por PPL
Por Qué Es Significativo:
Esto representa una evolución sofisticada más allá de técnicas BYOVD tradicionales. Al explotar
un zero‐day en un driver incorporado de Windows, los atacantes lograron un ataque de kernel
verdaderamente fileless sin necesidad de soltar o cargar drivers personalizados.
Mitigación

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
Microsoft lanzó parches en febrero 2024 ﴾Patch Tuesday﴿que: ‐ Añadieron verificación ExGetPre-
viousMode al manejador IOCTL ‐ Previenen que IOCTLs iniciados desde modo usuario disparen la
invocación de callback arbitrario
Observaciones
La primitiva de escritura arbitraria ﴾lograda vía corrupción de PreviousMode﴿es una técnica canónica
para: ‐ Voltear bits de privilegios ‐ Sobrescribir punteros de función ‐ Modificar datos de políticas
de seguridad
Este caso demuestra cómo manejadores IOCTL con validación de entrada insuficiente pueden pro‐
porcionar primitivas poderosas para explotación de kernel, especialmente cuando aceptan punteros
de función o permiten confusión de objetos.
### 2.2.6.
### 1.2.6 Mal Uso de Locking/RCU
Descripción General
Ordenamiento de locks incorrecto, locks faltantes o mal uso de RCU ﴾Read‐Copy‐Update﴿llevando
a carreras sobre objetos liberados. Estos bugs ocurren en código del kernel con alta concurrencia.
Patrones Comunes:
1. Lock Faltante: Acceso a datos compartidos sin sincronización
2. Ordenamiento de Locks Incorrecto: Deadlocks o carreras por orden inconsistente
3. Violaciones de RCU: Usar objeto RCU‐protegido fuera de sección crítica
4. Liberación Prematura: Soltar lock antes de que operación complete
Caso de Estudio: CVE‐2023‐32629 — Linux Netfilter nf_tables Race Condition
Campo
Detalle
Producto Afectado
Linux Kernel ﴾nf_tables﴿
Tipo
Condición de Carrera por Locking Impropio →UAF
Vector
User namespaces no privilegiados
Severidad
Alta
PoC Disponible
github.com/ThrynSec/CVE‐2023‐32629‐CVE‐2023‐
2640—POC‐Escalation
El Bug
El subsistema nf_tables de netfilter del kernel Linux contenía una vulnerabilidad de condición de
carrera debido a bloqueo impropio al manejar operaciones batch. La vulnerabilidad ocurría en el
código de manejo de transacciones donde el acceso concurrente a objetos de nf_tables no estaba
sincronizado apropiadamente, permitiendo condiciones use‐after‐free.
El Ataque:
Un atacante con capacidad CAP_NET_ADMIN ﴾obtenible a través de user namespaces no privilegiados
en muchas distribuciones﴿podía:

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
1. Enviar mensajes netlink concurrentes para manipular reglas de nf_tables
2. Cronometrar cuidadosamente estas operaciones a través de múltiples hilos
3. Disparar una ventana donde un hilo libera un objeto mientras otro hilo aún tiene una referen‐
cia
4. Explotar la condición use‐after‐free para escalada de privilegios
Impacto
Escalada de privilegios local de usuario no privilegiado a root en sistemas con user namespa‐
ces no privilegiados habilitados ﴾default en Ubuntu, Debian, Fedora y otros﴿
La primitiva use‐after‐free podía explotarse para obtener capacidades de lectura/escritura
arbitraria del kernel
Típicamente usada para modificar credenciales de proceso o sobrescribir punteros de función
del kernel
Afectó kernels Linux anteriores a versión 6.3.1 ﴾mayo 2023﴿
Mitigación
Linux kernel 6.3.1: ‐ Añadió mecanismos de bloqueo apropiados alrededor del procesamiento de
transacciones batch de nf_tables ‐ Implementó conteo de referencias para rastrear tiempos de vida
de objetos correctamente ‐ Aseguró operaciones atómicas para acceso concurrente a estructuras
de datos compartidas de netfilter
Observaciones
El mal uso de locking y RCU lleva a UAF reproducible y corrupción de memoria en rutas calientes
como sistemas de archivos, networking y timers. El ordenamiento de locks incorrecto, locks faltantes
y violaciones de RCU son particularmente peligrosos en código del kernel donde la concurrencia
es omnipresente.
El subsistema netfilter continúa siendo una fuente recurrente de tales vulnerabilidades debido a su
complejidad y uso extensivo de estructuras de datos concurrentes.
### 2.2.7.
### 1.2.7 Conclusiones de Vulnerabilidades Lógicas
Hallazgos Clave:
1. Las vulnerabilidades lógicas no requieren corrupción de memoria: Bypasses de autenti‐
cación, fallas TOCTOU y primitivas de escritura arbitraria pueden ser tan impactantes como
corrupción de memoria tradicional.
2. Los bugs de concurrencia habilitan exploits sofisticados: Double‐fetch, condiciones de ca‐
rrera y mal uso de locking son difíciles de reproducir pero proporcionan explotación confiable
cuando el timing es controlado.
3. La escritura arbitraria es la primitiva definitiva: Ya sea lograda a través de manejadores
IOCTL, corrupción de PreviousMode o mal uso de RCU, la escritura arbitraria del kernel habilita
escalada de privilegios, deshabilitación de callbacks de seguridad y despliegue de rootkits.
4. Los user namespaces expanden la superficie de ataque: Muchas vulnerabilidades del ker‐
nel ﴾netfilter, io_uring﴿se vuelven explotables desde contextos no privilegiados cuando user
namespaces otorgan capacidades como CAP_NET_ADMIN.

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
5. La defensa requiere operaciones atómicas: Las vulnerabilidades TOCTOU demuestran que
los patrones check‐then‐use son inherentemente propensos a carreras; operaciones atómicas
check‐and‐use, bloqueo apropiado y copia defensiva son esenciales.
Preguntas de Discusión:
1. ¿Cómo difieren las vulnerabilidades double‐fetch de las condiciones de carrera TOCTOU tra‐
dicionales y qué las hace particularmente peligrosas en contextos de hypervisor?
2. Compare la complejidad de explotación de fallas lógicas de autenticación versus condiciones
de carrera del kernel. ¿Cuál proporciona explotación más confiable y por qué?
3. ¿Cómo difiere la primitiva de escritura arbitraria lograda en CVE‐2024‐21338 ﴾vía corrupción
de PreviousMode﴿de la escritura arbitraria tradicional basada en buffer overflow, y qué ven‐
tajas proporciona a los atacantes?
### 2.3.
### 1.3 Confusión de Tipos y Enteros
Las vulnerabilidades de confusión de tipos ocurren cuando un programa procesa un objeto como
un tipo diferente al previsto. Los bugs de enteros incluyen desbordamiento, subdesbordamiento y
truncamiento.
### 2.3.1.
### 1.3.1 Confusión de Tipos en JIT
Descripción General
La confusión de tipos ocurre cuando un programa procesa un objeto como un tipo diferente al
previsto. Esto puede suceder en lenguajes de tipado dinámico, durante casts de tipo inseguros, o
en compiladores JIT que hacen suposiciones incorrectas sobre tipos de objetos.
Caso de Estudio: CVE‐2024‐7971 — V8 TurboFan Type Confusion
Campo
Detalle
Producto Afectado
Google Chrome ﴾V8 JavaScript Engine﴿
Tipo
Type Confusion en JIT
Vector
Página web maliciosa
Severidad
Crítica
El Bug
La optimización de eliminación CheckBounds de TurboFan asumió incorrectamente tipos de elemen‐
tos de array durante la compilación JIT. Al encontrar un inline cache polimórfico, TurboFan a veces
confundía punteros tagged ﴾objetos Heap﴿con SMI ﴾Small Integers﴿.
Impacto
Ejecución remota de código vía página web maliciosa

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
Permitía crear JSArray falso con puntero de backing store controlado
Capacidades de lectura/escritura fuera de límites
Escape del sandbox V8 para ejecución de shellcode
Contexto de Explotación
La confusión de tipos permitía construir primitivas de explotación: ‐ addrof: Filtrar direcciones de
objetos ﴾fuga de información para bypass de ASLR﴿‐ fakeobj: Crear objetos falsos con estructura
controlada ‐ lectura/escritura arbitraria: Acceso fuera de límites a cualquier ubicación de memoria
Mitigación
V8 parcheó la lógica de eliminación CheckBounds para rastrear correctamente información de tipos
durante pases de optimización.
Observaciones
La explotación de navegadores es un objetivo de alto valor. La confusión de tipos en compiladores
JIT es una clase de vulnerabilidad común, con nuevas variantes descubiertas regularmente.
### 2.3.2.
### 1.3.2 Desbordamiento de Enteros
Descripción General
Los bugs de enteros incluyen: ‐ Desbordamiento: Exceder valor máximo ﴾ej. INT_MAX + 1 envuelve a
INT_MIN﴿‐ Subdesbordamiento: Ir por debajo del valor mínimo ﴾ej. 0 - 1 se convierte en UINT_MAX
para unsigned﴿‐ Truncamiento: Perder datos al convertir de tipo mayor a menor
Los bugs de enteros frecuentemente llevan a corrupción de memoria porque los enteros se usan
para tamaños de búfer, contadores de bucle e índices de array.
Caso de Estudio: CVE‐2024‐38063 — Windows TCP/IP Integer Underflow RCE
Campo
Detalle
Producto Afectado
Windows TCP/IP Stack ﴾tcpip.sys﴿
Tipo
Integer Underflow →RCE
Vector
Paquetes IPv6 de red
Severidad
Crítica ﴾CVSS 9.8﴿
El Bug
La pila TCP/IP de Windows contenía una vulnerabilidad crítica de subdesbordamiento de enteros en
su código de procesamiento de paquetes IPv6. Al manejar paquetes IPv6 especialmente diseñados
con cabeceras de extensión malformadas, el driver tcpip.sys realizaba operaciones aritméticas que
podían resultar en un subdesbordamiento de enteros.
Impacto
Ejecución Remota de Código con privilegios SYSTEM en sistemas Windows afectados
CVSS Score: 9.8 ﴾Crítico﴿

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
Afectó Windows 10, Windows 11 y Windows Server versiones desde 2008 hasta 2022
Potencialmente wormeable ﴾podía propagarse automáticamente como SMBGhost﴿
Contexto de Explotación
1. Paquetes IPv6 con configuraciones específicas de cabeceras de extensión
2. Disparar el subdesbordamiento en cálculos de tamaño
3. El valor subdesbordado envuelve a un entero unsigned grande
4. El kernel asigna búfer pequeño basado en el valor envuelto
5. Operación de copia subsecuente usa tamaño grande original, causando desbordamiento de
heap
6. El desbordamiento de heap lleva a corrupción de memoria del kernel y RCE
Mitigación
Microsoft lanzó parches en agosto 2024 que añadieron verificación apropiada de límites al procesa‐
miento de paquetes IPv6 y corrigieron operaciones aritméticas de enteros para prevenir condiciones
de subdesbordamiento.
Observaciones
Esta vulnerabilidad demuestra cómo el subdesbordamiento de enteros en parsers de protocolos
de red puede llevar a vulnerabilidades de RCE críticas. El bug afectaba código de red fundamental
que procesa entrada de red no confiable, haciéndolo objetivo principal para exploits wormables
similares a SMBGhost y EternalBlue.
### 2.3.3.
### 1.3.3 Vulnerabilidades de Parsers
Descripción General
Los parsers convierten datos estructurados ﴾archivos, protocolos de red, etc.﴿en representaciones
internas del programa. Su complejidad los hace objetivos principales para fuzzing y explotación.
Caso de Estudio: CVE‐2024‐47606 — GStreamer Signed‐to‐Unsigned Integer Underflow
Campo
Detalle
Producto Afectado
GStreamer multimedia framework
Tipo
Conversión Signed‐to‐Unsigned →RCE
Vector
Archivo multimedia malicioso
Severidad
Alta
El Bug
GStreamer contenía una vulnerabilidad de conversión de entero signed a unsigned en la función
qtdemux_parse_theora_extension. Una variable de tamaño gint ﴾entero signed﴿subdesbordaba
a un valor negativo, que luego era implícitamente convertido a un entero unsigned de 64 bits,
convirtiéndose en un valor masivo.
Impacto

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
Ejecución remota de código al procesar archivos multimedia maliciosos
GStreamer es usado por innumerables aplicaciones ﴾GNOME, KDE, Firefox, Chrome, derivados
de VLC﴿
Los archivos multimedia son comúnmente compartidos y procesados automáticamente
Afecta tanto sistemas de escritorio como embebidos
Contexto de Explotación
1. Archivo multimedia malicioso contiene extensión Theora con campos de tamaño diseñados
2. La función calcula tamaño usando aritmética signed
3. El cálculo subdesborda ﴾ej. ‐6 o 0xFFFFFFFA en representación de 32 bits﴿
4. Valor negativo de 32 bits es convertido a unsigned de 64 bits →valor masivo
5. Solo se asignan bytes pequeños a pesar del tamaño enorme solicitado
6. memcpy subsecuente copia datos grandes en búfer pequeño
7. Desbordamiento de búfer corrompe estructura GstMapInfo
8. Secuestro de puntero de función logra RCE
Mitigación
GStreamer 1.24.10 ﴾diciembre 2024﴿corrigió la vulnerabilidad añadiendo verificaciones explícitas
para valores negativos antes de convertir signed a unsigned y usando aritmética de enteros segura.
Observaciones
Este es un ejemplo de libro de texto de vulnerabilidades de conversión signed‐to‐unsigned ﴾CWE‐
195﴿. En C/C++, las conversiones implícitas entre enteros signed y unsigned siguen reglas complejas
que los desarrolladores frecuentemente malinterpretan. Los enteros signed negativos se convierten
en valores unsigned positivos enormes cuando son convertidos.
Caso de Estudio: CVE‐2024‐27316 — nghttp2 HTTP/2 CONTINUATION Frame DoS
Campo
Detalle
Producto Afectado
nghttp2 HTTP/2 library
Tipo
Agotamiento de Recursos →DoS
Vector
Conexión HTTP/2 de red
Severidad
Alta ﴾CVSS 7.5﴿
El Bug
La biblioteca nghttp2 HTTP/2 ﴾usada por Apache httpd, nginx y muchos otros servidores﴿conte‐
nía una vulnerabilidad en su manejo de frames CONTINUATION. La biblioteca fallaba en limitar el
tamaño total acumulado de datos de cabecera a través de frames CONTINUATION.
Impacto
Denegación de Servicio vía agotamiento de memoria
Una única conexión TCP podía agotar gigabytes de memoria del servidor
Muy bajo ancho de banda requerido del atacante
Afectó nghttp2, Apache HTTP Server, nginx y otros

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
Contexto de Explotación
Un atacante podía establecer una conexión HTTP/2 y ejecutar: 1. Enviar frame HEADERS válido para
iniciar nuevo stream 2. Enviar frames CONTINUATION continuos sin establecer flag END_HEADERS
3. Cada frame CONTINUATION añade datos al búfer de cabecera acumulado 4. El servidor asigna
más memoria por cada frame recibido 5. El proceso se repite hasta que la memoria del servidor se
agota
Mitigación
nghttp2 v1.61.0 ﴾abril 2024﴿añadió límite NGHTTP2_DEFAULT_MAX_HEADER_LIST_SIZE ﴾64KB por de‐
fecto﴿para el tamaño total acumulado de cabeceras. Apache httpd 2.4.59 implementó directiva
H2MaxHeaderListSize.
Observaciones
Esta vulnerabilidad demuestra que los parsers deben rastrear el consumo de recursos a través de
operaciones relacionadas, no solo operaciones individuales. El ataque es particularmente efectivo
porque explota el mecanismo legítimo del protocolo.
### 2.4.
### 1.4 Vulnerabilidades de Strings y Formato
Las vulnerabilidades de format string ocurren cuando datos controlados por el usuario se pasan
como argumento de format string a funciones como printf, sprintf y similares.
Caso de Estudio: CVE‐2023‐35086 — ASUS Router Format String RCE
Campo
Detalle
Producto Afectado
ASUS RT‐AX56U V2 y RT‐AC86U routers
Tipo
Format String →RCE
Vector
Interfaz web de administración
Severidad
Crítica
El Bug
Los routers ASUS contenían una vulnerabilidad de format string en su interfaz de administración
web ﴾demonio httpd﴿. La función logmessage_normal del módulo do_detwan_cgi usaba directamen‐
te entrada controlada por el usuario como format string al llamar a syslog().
Impacto
Ejecución remota de código con privilegios root
Permitía fuga de información para bypass de ASLR
Habilitaba escritura arbitraria de memoria vía directiva %n
Compromiso completo del dispositivo de red
Contexto de Explotación

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
Etapa 1 ‐ Fuga de Información: ‐ Atacante envía solicitud HTTP con format string: %p. %p. %p. %p ‐
Router registra esto a syslog, filtrando direcciones de pila ‐ Las directivas %p revelan layout de pila
y derrotan ASLR
Etapa 2 ‐ Escritura Arbitraria: ‐ Atacante diseña format string con directiva %n ‐ Sobreescribe
puntero de función o dirección de retorno en pila ‐ Redirige ejecución a shellcode controlado por
atacante ‐ Resultado: Ejecución Remota de Código con privilegios root
Mitigación
Actualizaciones de firmware ASUS cambiaron:
// Vulnerable:
syslog(LOG_INFO, user_input);
// Corregido:
syslog(LOG_INFO, " %s", user_input);
Adicionalmente implementaron validación de entrada y habilitaron advertencias de compilador -
Wformat-security.
Observaciones
Las vulnerabilidades de format string en dispositivos embebidos y routers son particularmente pe‐
ligrosas porque los dispositivos frecuentemente ejecutan firmware desactualizado, muchos están
expuestos a Internet, y el compromiso proporciona acceso persistente a redes.
### 2.5.
### 1.5 Vulnerabilidades de Drivers y Sistemas de Archivos
Los drivers y sistemas de archivos representan una superficie de ataque masiva debido a sus inter‐
faces complejas con el kernel y el manejo de entrada no confiable.
### 2.5.1.
Vulnerabilidades de Manejadores IOCTL/Syscall
Caso de Estudio: CVE‐2023‐21768 — Windows AFD.sys Buffer Size Confusion
Campo
Detalle
Producto Afectado
Windows AFD.sys ﴾Ancillary Function Driver﴿
Tipo
Confusión de Tamaño de Búfer
Vector
Local
Severidad
Alta
El Bug
El Windows Ancillary Function Driver ﴾AFD.sys﴿, que maneja operaciones de socket, tenía una
vulnerabilidad de confusión de tamaño de búfer en su manejador IOCTL. Al procesar solicitudes

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
IOCTL_AFD_SELECT, el driver fallaba en validar apropiadamente la relación entre el tamaño de búfer
proporcionado por el usuario y el tamaño real de la estructura.
Impacto
Escalada de privilegios local de usuario estándar a SYSTEM
La primitiva de escritura OOB se usaba para corromper objetos del kernel adyacentes en el
pool
Explotado en el wild antes del parcheo
Contexto de Explotación
Un atacante podía llamar a DeviceIoControl() con un búfer de entrada especialmente diseñado
donde el tamaño declarado no coincidía con el tamaño real de datos. El driver asignaba un búfer
basado en un valor de tamaño pero copiaba datos basado en otro.
Mitigación
Microsoft KB5022845 añadió validación estricta asegurando que la longitud proporcionada por el
usuario coincidiera con el tamaño de estructura esperado, usó ProbeForRead() para validar punte‐
ros de usuario, e implementó verificación adicional de límites.
Observaciones
Los manejadores IOCTL/syscall son vectores de ataque comunes debido a confusión de tama‐
ño/límites, confianza en punteros de usuario sin probing, y problemas de double‐fetch.
### 2.5.2.
Vulnerabilidades de Sistemas de Archivos
Caso de Estudio: CVE‐2022‐0847 — Dirty Pipe
Campo
Detalle
Producto Afectado
Linux Kernel ﴾implementación de pipes﴿
Tipo
Falla Lógica →Escritura Arbitraria de Archivos
Vector
Local
Severidad
Crítica
El Bug
La implementación de pipes del kernel Linux fallaba en inicializar apropiadamente el flag PI-
PE_BUF_FLAG_CAN_MERGE al hacer splice de páginas de la caché de páginas hacia pipes. Esto permitía
sobreescribir datos en archivos de solo lectura haciendo splice de páginas modificadas de vuelta.
Impacto
Escalada de privilegios local de cualquier usuario a root sobreescribiendo /etc/passwd u otros
archivos privilegiados
Explotación extremadamente confiable requiriendo permisos mínimos
Afectó kernels Linux 5.8+ hasta 5.16.11

---

### CAPÍTULO 2. CLASES DE VULNERABILIDADES
Bitácora Red Team
Contexto de Explotación
Un atacante podía: 1. Abrir un archivo de solo lectura ﴾ej. /etc/passwd﴿2. Usar splice() para crear
un pipe conteniendo páginas de ese archivo 3. Modificar el búfer del pipe 4. Hacer splice de vuelta
para sobreescribir contenidos del archivo original
Mitigación
Linux kernel 5.16.11+ inicializa apropiadamente los flags de búfer de pipe y previene el splice de
vuelta a archivos de solo lectura.
Observaciones
Las operaciones de pipe y splice son mecanismos complejos del kernel con requisitos sutiles de
gestión de estado. Dirty Pipe demostró cómo bugs de inicialización pueden llevar a primitivas po‐
derosas de escritura arbitraria de archivos.
### 2.5.3.
Bring Your Own Vulnerable Driver ﴾BYOVD﴿
Caso de Estudio: Abuso de Drivers por Lazarus Group
Campo
Detalle
Técnica
BYOVD ﴾Bring Your Own Vulnerable Driver﴿
Tipo
Abuso de Driver Legítimo
Vector
Driver firmado vulnerable
Uso
Grupos de amenazas avanzados
La Técnica
Los atacantes dejan caer un driver legítimo pero vulnerable firmado ﴾ej. versiones antiguas de drivers
ASUS, Gigabyte o MSI﴿que Windows cargará debido a su firma válida.
Impacto
Una vez cargado, el driver vulnerable proporciona primitivas de lectura/escritura arbitraria del
kernel a través de su interfaz IOCTL
Los atacantes usan esto para deshabilitar características de seguridad ﴾PatchGuard, AV/EDR﴿
Permite cargar drivers no firmados o escalar privilegios
Contexto de Explotación
La técnica BYOVD fue ampliamente usada por grupos como Lazarus antes de que Microsoft expan‐
diera la Driver Blocklist. Grupos avanzados han cambiado de BYOVD a exploits directos de zero‐day
del kernel después de 2023 debido al aumento de detección.
Mitigación
Habilitar Vulnerable Driver Blocklist ﴾HVCI/Memory Integrity﴿
Monitorear cargas de drivers inusuales
Implementar políticas de control de aplicaciones