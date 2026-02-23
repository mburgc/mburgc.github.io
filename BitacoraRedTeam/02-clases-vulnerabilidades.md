# Capítulo 2: Clases de Vulnerabilidades

Este capítulo documenta las principales clases de vulnerabilidades encontradas en sistemas operativos y aplicaciones, con énfasis particular en el contexto de kernel y sistemas de bajo nivel. Cada entrada incluye descripción técnica, casos de estudio reales, impacto y mitigaciones aplicables.

**Objetivo:** Comprender las clases primarias de vulnerabilidades de corrupción de memoria y su impacto en el mundo real.

**Recursos de Lectura Recomendados:**
- “The Art of Software Security Assessment” por Mark Dowd, John McDonald, Justin Schuh - Capítulo 5: Memory Corruption
- Memory Corruption: Examples, Impact, and 4 Ways to Prevent It
- Microsoft Security Research: Memory Safety
- Google Project Zero Blog - Hallazgos recientes de corrupción de memoria

## 2.1. 1.1 Fundamentos de Corrupción de Memoria

La corrupción de memoria continúa siendo una de las clases de vulnerabilidades más críticas y prevalentes en software escrito en C/C++. A pesar de décadas de investigación en seguridad, estos bugs persisten debido a la complejidad inherente de la gestión manual de memoria.

**Conceptos Clave:**
- **¿Qué es la corrupción de memoria y por qué importa?** La corrupción de memoria ocurre cuando un programa modifica memoria de maneras no intencionadas, permitiendo a atacantes alterar el estado del programa y potencialmente obtener control de ejecución.
- **Pila (Stack):** Región de memoria para variables locales y direcciones de retorno. Su estructura LIFO (Last-In-First-Out) la hace vulnerable a desbordamientos que pueden sobrescribir direcciones de retorno.
- **Heap:** Región de memoria dinámica gestionada por el allocator (malloc/free). Los metadatos del heap y objetos adyacentes pueden ser corrompidos por desbordamientos.
- **Ciclo de Vida de Memoria:** Asignación → Uso → Liberación. Los errores en cualquier fase pueden llevar a vulnerabilidades.

### 2.1.1. 1.1.1 Desbordamiento de Búfer en Pila (Stack Buffer Overflow)

**Descripción General**

Un desbordamiento de búfer en pila (stack buffer overflow) ocurre cuando un programa escribe más datos en un búfer ubicado en la pila de los que este puede contener. Esto provoca la sobrescritura de memoria adyacente, incluyendo datos críticos como direcciones de retorno, permitiendo potencialmente redirijir la ejecución del programa.

**Mecánica del Ataque:**

```
      LAYOUT DE PILA
+-------------------------+
|   [Direcciones Altas]   |
|   +-----------------+   |
|   | Dirección de    | <--- Sobrescrita por atacante
|   | Retorno         |   |
|   +-----------------+   |
|   | Frame Pointer   | <--- También corrompido
|   | Guardado        |   |
|   +-----------------+   |
|   | Variables       |   |
|   | Locales         |   |
|   +-----------------+   |
|   | Búfer[64]       | <--- Desbordamiento ocurre aquí
|   |                 |   |
|   +-----------------+   |
|   [Direcciones Bajas]   |
+-------------------------+
```

**Caso de Estudio: CVE-2024-27130 — QNAP QTS/QuTS Hero**

| Campo             | Detalle                                       |
| ----------------- | --------------------------------------------- |
| Producto Afectado | QNAP QTS y QuTS hero                          |
| Tipo              | Stack Buffer Overflow                         |
| Vector            | Interfaz de administración web                |
| Severidad         | Crítica                                       |
| PoC Disponible    | github.com/watchtowrlabs/CVE-2024-27130       |

**El Bug**

Los sistemas operativos QTS y QuTS hero de QNAP contenían múltiples vulnerabilidades de copia de búfer donde funciones inseguras como `strcpy()` se utilizaban para copiar entrada suministrada por el usuario a búferes de tamaño fijo en la pila sin validación de tamaño adecuada. Las vulnerabilidades afectaban la interfaz de administración web y los componentes de manejo de archivos.

**El Ataque (Paso a Paso)**

1.  **Reconocimiento:** Atacante identifica endpoint vulnerable en interfaz de administración web
2.  **Preparación:** Construcción de payload con entrada sobredimensionada
3.  **Explotación:** Envío de solicitud especialmente diseñada con datos que exceden el tamaño del búfer
4.  **Corrupción:** Los datos no verificados desbordan el búfer en pila, sobrescribiendo:
    -   Variables locales adyacentes
    -   Frame pointer guardado
    -   Dirección de retorno
5.  **Control de Ejecución:** Cuando la función retorna, el flujo de ejecución se redirige a código controlado por el atacante

**Impacto**

-   Ejecución remota de código con los privilegios del servicio QNAP (típicamente root)
-   Control completo del dispositivo NAS, permitiendo:
    -   Acceso a todos los datos almacenados
    -   Pivoteo a otros recursos de red
    -   Instalación de backdoors persistentes
-   Riesgo crítico para infraestructura empresarial donde los NAS almacenan datos sensibles

**Mitigación**

QNAP lanzó QTS 5.1.7.2770 build 20240520 y QuTS hero h5.1.7.2770 build 20240520 en mayo de 2024:
-   Reemplazo de funciones de copia de cadenas inseguras (`strcpy`, `sprintf`) con alternativas con verificación de límites (`strncpy`, `snprintf`)
-   Implementación de validación de entrada adicional
-   Habilitación de protecciones de compilador (stack canaries)

**Observaciones**

Los desbordamientos de pila siguen siendo comunes en:
-   Dispositivos embebidos con código legacy C/C++
-   Sistemas NAS con interfaces de administración expuestas a Internet
-   Aplicaciones que no han adoptado APIs seguras modernas

Son particularmente peligrosos cuando:
-   Proporcionan el punto de entrada inicial para cadenas de ataque sofisticadas contra infraestructura empresarial
-   No tienen protecciones de compilador habilitadas (ASLR, DEP, stack canaries)

### 2.1.2. 1.1.2 Uso Después de Liberación (Use-After-Free / UAF)

**Descripción General**

Una vulnerabilidad de uso después de liberación (Use-After-Free) ocurre cuando un programa continúa usando un puntero después de que la memoria a la que apunta ha sido liberada. Esto crea un “puntero colgante” (dangling pointer) que puede ser explotado controlando cuidadosamente las asignaciones del heap para colocar datos controlados por el atacante donde el objeto liberado residía anteriormente.

**Mecánica del Bug:**

```
      CICLO DE VIDA UAF
+--------------------------------+
|   1. ASIGNACIÓN                |
|      obj = malloc(sizeof(Object)); |
|      obj->vtable = &legitimate_vtable; |
|                                |
|   2. USO LEGÍTIMO              |
|      obj->method();   // Llama función via vtable |
|                                |
|   3. LIBERACIÓN                |
|      free(obj);       // Memoria liberada, pero... |
|      // ¡El puntero 'obj' aún existe! |
|                                |
|   4. REASIGNACIÓN (por atacante) |
|      attacker_data = malloc(sizeof(Object)); |
|      // Mismo tamaño → puede obtener la misma ubicación |
|      attacker_data->vtable = &malicious_vtable; |
|                                |
|   5. USO DESPUÉS DE LIBERACIÓN |
|      obj->method();   // ¡Llama función del atacante! |
+--------------------------------+
```

**Caso de Estudio: CVE-2024-2883 — Chrome ANGLE**

| Campo                | Detalle                                    |
| -------------------- | ------------------------------------------ |
| Producto Afectado    | Google Chrome (componente ANGLE)           |
| Tipo                 | Use-After-Free                             |
| Vector               | Página web maliciosa                       |
| Severidad            | Crítica                                    |
| Código Explotable    | Sí, sin interacción del usuario            |

**El Bug**

El componente ANGLE (Almost Native Graphics Layer Engine) de Google Chrome, que traduce llamadas de API OpenGL ES a DirectX, Vulkan o OpenGL nativo, contenía una vulnerabilidad de uso después de liberación. El bug ocurría cuando los contextos WebGL eran destruidos mientras aún estaban referenciados por operaciones gráficas pendientes, dejando punteros colgantes a objetos gráficos liberados.

**El Ataque (Paso a Paso)**

1.  **Preparación del Entorno:**
    -   Atacante crea página HTML maliciosa con código JavaScript WebGL
    -   El código manipula la creación y destrucción de contextos gráficos
2.  **Disparar el Bug:**
    ```javascript
    // Concepto simplificado (no es el exploit real):
    let ctx = canvas.getContext('webgl');
    // Iniciar operación gráfica asíncrona
    ctx.bindBuffer(ctx.ARRAY_BUFFER, buffer);
    // Destruir contexto mientras operación está pendiente
    ctx = null;
    // Garbage collection libera el contexto
    // pero operación pendiente aún tiene referencia
    ```
3.  **Heap Feng-Shui:**
    -   Usar técnicas de heap spray para controlar asignaciones
    -   Asignar objetos del mismo tamaño que el objeto liberado
    -   Colocar datos controlados por atacante en ubicación liberada
4.  **Explotación:**
    -   Cuando código de ANGLE usa el puntero colgante, accede a datos del atacante
    -   El atacante coloca un objeto falso con vtable maliciosa
    -   La próxima llamada a método virtual ejecuta código del atacante

**Impacto**

-   Ejecución remota de código vía página web maliciosa con NO interacción del usuario más allá de visitar la página
-   Al colocar un objeto falso en la memoria liberada, el atacante puede secuestrar el flujo de control
-   Ejecutar código arbitrario en el proceso del renderer
-   Puede encadenarse con exploits de escape de sandbox para compromiso completo del sistema

**Mitigación**

Google Chrome 123.0.6312.86 (lanzado marzo 2024) corrigió la vulnerabilidad:
-   Implementación de gestión adecuada del tiempo de vida para objetos gráficos
-   Añadido conteo de referencias para prevenir destrucción prematura de objetos aún en uso
-   Validación adicional antes de usar punteros a objetos gráficos

**Observaciones**

Las vulnerabilidades UAF son particularmente peligrosas en:
-   Navegadores: Aplicaciones C++ complejas donde el tiempo de vida de objetos es difícil de rastrear
-   Subsistemas Gráficos: ANGLE, Skia y similares manejan contenido no confiable y tienen gestión de estado compleja
-   Código con Callbacks Asíncronos: Donde el orden de ejecución es difícil de predecir

Son un objetivo favorito de atacantes avanzados porque:
-   Ofrecen control fino sobre la ejecución del programa
-   Son difíciles de detectar con análisis estático
-   Las mitigaciones modernas (ASLR) pueden ser evadidas con técnicas de heap manipulation

### 2.1.3. 1.1.3 Desbordamiento de Búfer en Heap (Heap Buffer Overflow)

**Descripción General**

Similar a los desbordamientos de pila, los desbordamientos de heap ocurren cuando un programa escribe más allá de los límites de un búfer asignado dinámicamente en el heap. En lugar de corromper frames de pila, los desbordamientos de heap típicamente corrompen metadatos del heap o objetos adyacentes, llevando a corrupción de memoria cuando el allocator posteriormente procesa las estructuras corrompidas.

**Mecánica del Desbordamiento de Heap:**

```
      LAYOUT DE HEAP
+----------------------------------+
|   +----------------------------+   |
|   | Chunk Header (metadatos)   |   |
|   +----------------------------+   |
|   | Búfer Vulnerable [100]     |   |
|   |                            |   |
|   | ══════════════════════════ | <--- Límite
|   | OVERFLOW →→→→→→→→→→→→→→→→→→ |
|   +----------------------------+   |
|   +----------------------------+   |
|   | Chunk Header (CORROMPIDO)  | <--- Corrupción
|   +----------------------------+   |
|   | Objeto Adyacente           |   |
|   | - vtable *                 | <--- O corrupción
|   | - function_ptr             |      de objeto
|   | - data fields              |   |
|   +----------------------------+   |
+----------------------------------+
```

**Caso de Estudio: CVE-2023-4863 — libWebP**

| Campo             | Detalle                                       |
| ----------------- | --------------------------------------------- |
| Producto Afectado | libWebP (Chrome, Firefox, Edge, múltiples apps) |
| Tipo              | Heap Buffer Overflow                          |
| Vector            | Imagen WebP maliciosa                         |
| Severidad         | Crítica                                       |
| PoC Disponible    | github.com/mistymntncop/CVE-2023-4863         |

**El Bug**

La biblioteca libWebP, utilizada por Chrome, Firefox, Edge y muchas otras aplicaciones para procesar imágenes WebP, contenía un desbordamiento de heap en la función `BuildHuffmanTable()`. Al parsear imágenes WebP especialmente diseñadas con datos de codificación Huffman malformados, la función escribía más allá de los límites del búfer asignado.

**El Ataque (Paso a Paso)**

1.  **Vector de Entrada:**
    -   Atacante embebe imagen WebP maliciosa en página web
    -   O la envía vía aplicaciones de mensajería (WhatsApp, Telegram, Signal)
    -   O incluye en documento (email, Word, PDF)
2.  **Trigger:**
    -   Navegador/aplicación de víctima intenta decodificar la imagen
    -   Parser WebP procesa datos Huffman malformados
    -   `BuildHuffmanTable()` calcula tamaño de tabla incorrectamente
3.  **Explotación:**
    -   El desbordamiento corrompe metadatos del heap
    -   O corrompe objetos adyacentes con función pointers
    -   Atacante controla datos del desbordamiento para conseguir primitivas
4.  **Resultado:**
    -   Ejecución de código arbitrario en contexto del proceso
    -   En navegadores: código ejecuta en proceso renderer

**Impacto**

-   Ejecución remota de código sin interacción del usuario más allá de ver una página web o abrir una imagen
-   Zero-day explotado activamente antes de su divulgación pública (septiembre 2023)
-   Billones de dispositivos afectados en múltiples plataformas:
    -   Windows, macOS, Linux (desktop)
    -   Android, iOS (mobile)
    -   Cualquier software usando libWebP (Electron apps, etc.)

**Por Qué Esta Vulnerabilidad es Emblemática:**

1.  **Riesgo de Cadena de Suministro:** Un bug en libWebP afectó docenas de aplicaciones mayores
2.  **Ubicuidad de Imágenes:** Las imágenes son procesadas automáticamente y son ubicuas
3.  **Técnicas Modernas de Heap:** Los atacantes combinaron heap overflow con técnicas de bypass de ASLR

**Mitigación**

-   libWebP 1.3.2 (septiembre 2023): Corrigió verificación de límites en `BuildHuffmanTable()`
-   Chrome 116.0.5845.187: Parche de emergencia
-   Firefox 117.0.1: Parche de emergencia
-   Otros software afectado lanzó actualizaciones coordinadas

**Observaciones**

Los desbordamientos de heap en parsers de imágenes son particularmente peligrosos porque:
-   Las imágenes son procesadas automáticamente sin confirmación del usuario
-   Son compartidas rutinariamente y consideradas “seguras”
-   Parsers de imagen optimizan rendimiento, sacrificando verificaciones de seguridad
-   La complejidad de formatos de compresión (Huffman, LZW, etc.) introduce bugs

### 2.1.4. 1.1.4 Lectura Fuera de Límites (Out-of-Bounds Read / Info Leak)

**Descripción General**

Una lectura fuera de límites (Out-of-Bounds Read) ocurre cuando un programa lee memoria pasando los límites de un búfer sin modificarla. Aunque no permite escritura directa, frecuentemente se utiliza para:
-   Filtrar punteros para bypass de ASLR/KASLR
-   Exponer metadatos de objetos para construir primitivas más poderosas
-   Revelar diseño de memoria del kernel para explotación confiable

**Rol en Cadenas de Explotación:**

```
      CADENA DE EXPLOTACIÓN TÍPICA
+--------------------------------+
|   1. OOB READ (Info Leak)      | <--- Filtrar direcciones de kernel
|   └─────────┬─────────┘        |
|             │                  |
|             ▼                  |
|   2. KASLR BYPASS              | <--- Calcular direcciones reales
|   └─────────┬─────────┘        |
|             │                  |
|             ▼                  |
|   3. WRITE PRIMITIVE           | <--- Otra vulnerabilidad (UAF, overflow)
|   └─────────┬─────────┘        |
|             │                  |
|             ▼                  |
|   4. CODE EXECUTION            | <--- Escribir a ubicación conocida
+--------------------------------+
```

**Caso de Estudio: CVE-2024-53108 — Linux AMDGPU Display Driver**

| Campo             | Detalle                               |
| ----------------- | ------------------------------------- |
| Producto Afectado | Linux Kernel (driver AMD Display)     |
| Tipo              | Out-of-Bounds Read (slab-out-of-bounds)|
| Vector            | Datos EDID/display maliciosos         |
| Severidad         | Media-Alta                            |
| Diff del Parche   | git.kernel.org                        |

**El Bug**

En el driver de display AMD del kernel Linux, la ruta de parsing EDID/VSDB (Video Specification Database) tenía verificación insuficiente de límites al extraer identificadores de capacidades. Cuando procesaba datos EDID con campos de longitud manipulados, el driver leía más allá de los límites del búfer EDID asignado.

El bug fue detectado por KASAN (Kernel AddressSanitizer) que reportó acceso slab-out-of-bounds durante la extracción de datos del display.

**El Ataque**

Un flujo de datos EDID/display maliciosamente construido podría:
1.  Disparar lectura OOB en espacio de kernel
2.  Exponer contenidos de memoria de kernel (incluyendo punteros)
3.  Proporcionar información para evadir KASLR
4.  Ser encadenado con otra vulnerabilidad de escritura para explotación completa

**Impacto**

-   Divulgación de información: Exposición de contenido de memoria del kernel
-   Potencial inestabilidad del sistema: Lectura de memoria inválida puede causar oops
-   Habilitador de explotación: Utilizable para evadir KASLR en cadenas de explotación más complejas

**Por Qué las OOB Reads Importan:**

En contextos de kernel:
-   KASLR es una mitigación fundamental contra explotación
-   Sin info leak, escritura ciega falla - el atacante necesita saber dónde escribir
-   OOB reads son el primer paso de la mayoría de exploits modernos de kernel

**Mitigación**

Las actualizaciones del kernel ajustaron la validación de longitud:
-   Verificar que bLength sea >= tamaño mínimo esperado
-   Validar offsets antes de acceder a campos
-   Asegurar que todas las lecturas permanezcan dentro de los límites del búfer EDID

**Observaciones**

Las lecturas OOB puras son valiosas para construir cadenas de explotación confiables:
-   Proporcionan información necesaria para bypass de ASLR/KASLR
-   Son frecuentemente la primera etapa de exploits multi-paso
-   En kernel, derrotar KASLR es pivotal para explotación confiable

### 2.1.5. 1.1.5 Uso de Memoria No Inicializada (Uninitialized Memory Use)

**Descripción General**

Usar memoria de pila/heap/pool antes de que sea inicializada puede exponer contenidos residuales de operaciones previas. Estos contenidos pueden incluir:
-   Punteros previos (direcciones del kernel para bypass de KASLR)
-   Flags de capacidad (para escalada de privilegios)
-   Campos de estructura (para confusión de tipos)

**Por Qué Es Peligroso:**

```c
// Código vulnerable - variable no inicializada
void vulnerable_function(struct netlink_msg *msg) {
    struct nft_pipapo_match *m; // <--- NO INICIALIZADO

     // Si algún camino de código no asigna 'm'...
     if (some_condition(msg)) {
         m = find_match(msg);
     }
     // ... pero 'm' se usa incondicionalmente

     copy_to_user(response, &m, sizeof(m)); // <--- Filtra pila residual
}
```

**Caso de Estudio: CVE-2024-26581 — Linux Kernel Netfilter**

| Campo             | Detalle                               |
| ----------------- | ------------------------------------- |
| Producto Afectado | Linux Kernel (subsistema netfilter)   |
| Tipo              | Uso de Variable No Inicializada       |
| Vector            | Mensajes netlink locales              |
| Severidad         | Alta                                  |
| PoC Disponible    | sploitus.com/exploit?id=A4D521EE-225F-57D5-8C31-9F1C86D066B6 |

**El Bug**

El subsistema netfilter del kernel Linux contenía una vulnerabilidad de variable no inicializada en el componente nf_tables. Al procesar mensajes netlink para configurar reglas de firewall, la función `nft_pipapo_walk()` fallaba en inicializar una variable local antes de su uso.

La variable no inicializada de pila podría contener datos residuales de llamadas a funciones previas, incluyendo punteros del kernel y direcciones de memoria sensibles.

**El Ataque (Paso a Paso)**

1.  **Obtener Capacidades:**
    -   Atacante está en espacio de nombres de usuario no privilegiado
    -   User namespaces otorgan CAP_NET_ADMIN (default en Ubuntu, Debian)
2.  **Disparar el Bug:**
    -   Enviar mensajes netlink específicos de configuración de nf_tables
    -   Causar que se ejecute la ruta de código con variable no inicializada
    -   La variable se lee y se copia de vuelta al espacio de usuario
3.  **Recolectar Información:**
    -   Repetir el trigger múltiples veces
    -   Analizar datos retornados
    -   Extraer direcciones de kernel (heap, stack, código)
4.  **Explotar con Información:**
    -   Usar direcciones filtradas para evadir KASLR
    -   Combinar con otra vulnerabilidad de escritura de netfilter
    -   Lograr escalada de privilegios completa (LPE chain)

**Impacto**

-   Divulgación de información → bypass de KASLR
-   Las direcciones del kernel filtradas permiten explotación confiable de otras vulnerabilidades
-   Particularmente peligrosa cuando se combina con otros bugs de netfilter para cadenas LPE completas

**Peligro del Combo: Netfilter + User Namespaces**

Muchas distribuciones Linux permiten user namespaces no privilegiados por defecto:
-   Ubuntu: Habilitado por defecto
-   Debian: Habilitado por defecto
-   Fedora: Habilitado por defecto

Esto significa que CAP_NET_ADMIN está disponible para usuarios no privilegiados, haciendo que bugs de netfilter sean explotables sin privilegios root.

**Mitigación**

Linux kernel 6.8-rc1 (febrero 2024):
-   Añadió inicialización apropiada: `struct nft_pipapo_match *m = NULL;`
-   Habilitó inicializadores designados para estructuras de pila
-   Habilitó advertencias de compilador más estrictas (`-Wuninitialized`) para netfilter

**Observaciones**

Las lecturas de memoria no inicializada son frecuentemente la primera etapa en cadenas de explotación:
-   Proporcionan reducciones de entropía para evadir mitigaciones modernas
-   Son particularmente valiosas en explotación de kernel donde KASLR es esencial
-   La combinación de user namespaces no privilegiados y fugas de netfilter hace esta clase de vulnerabilidad accesible a atacantes locales sin requerir privilegios root
... (El resto del capítulo seguiría la misma estructura)
