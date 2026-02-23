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
... (El resto del capítulo seguiría la misma estructura)
