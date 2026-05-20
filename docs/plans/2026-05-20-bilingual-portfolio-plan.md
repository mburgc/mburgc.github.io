# Plan: Sitio Bilingüe (ES/EN)

## Objetivo
Que todo el portfolio sea completamente navegable en español e inglés, con selector de idioma consistente en todas las páginas.

---

## Estado actual

| Ruta | ES | EN |
|------|----|----|
| `/` (homepage) | ❌ | ✅ |
| `/experimentos/` | ❌ | ✅ |
| `/bitacora/` | ✅ | ✅ |
| `/experimentos/julia/` | ✅ | ✅ |

---

## Enfoque

Misma convención ya establecida: **directorios separados por idioma**, con `index.html` como punto de entrada en cada idioma.

Estructura resultante:

```
/
├── index.html              # Homepage EN (existente, con lang switcher agregado)
├── es/
│   └── index.html          # 🆕 Homepage ES
├── experimentos/
│   ├── index.html          # EN (existente, con lang switcher)
│   └── es/
│       └── index.html      # 🆕 ES
├── bitacora/               # ✅ Ya bilingüe
└── experimentos/julia/     # ✅ Ya bilingüe
```

---

## Cambios necesarios

### 1. Homepage (`/index.html`)
- Agregar **language switcher** en el header (junto al botón de Experimentos)
  ```
  🇪🇸 ES  /  🇬🇧 EN
  ```
- El link ES apunta a `/es/`
- Traducir al español: todo el contenido visible (títulos, biografía, botones, placeholders JS)

### 2. Homepage ES (`/es/index.html`)
- Copia del `index.html` actual con:
  - Todo el texto visible traducido al español
  - Content-Type lang="es"
  - Language switcher: ES activo, EN apunta a `/`
  - Mismos estilos, mismas funcionalidades JS (starfield, GitHub repos, YouTube, etc.)

### 3. Experiments landing (`/experimentos/index.html`)
- Agregar language switcher
- El link ES apunta a `/experimentos/es/`

### 4. Experiments ES (`/experimentos/es/index.html`)
- Copia traducida del landing

### 5. Bitácora y JULIA diary
- Ya tienen switcher — solo verificar que los links del nuevo home apunten correctamente (ej: desde `/es/` las rutas deben ser `/bitacora/` o `../bitacora/` según corresponda)

---

## Detalles de traducción (homepage)

| Elemento actual (EN) | Traducción ES |
|---|---|
| `Solutions and Science` | `Soluciones y Ciencia` |
| `Bitácora Red Team` | `Bitácora Red Team` (se mantiene) |
| `Experimentos` | `Experimentos` |
| `About Me` | `Sobre Mí` |
| *Texto de la biografía* | Versión en español |
| `Connect` | `Conectar` |
| `Latest Video` | `Último Video` |
| `My Repositories` | `Mis Repositorios` |
| `Visitor Information` | `Información del Visitante` |
| Slogans rotativos | Versión en español |
| `Featured Post` (Reddit) | `Publicación Destacada` |
| Reddit fallback | Mismo post, misma URL |
| `Visitor Info` labels | Traducidos (IP, User Agent, Plataforma, etc.) |
| Texto de privacidad | Versión en español |

---

## Orden de implementación

| Fase | Qué |
|------|-----|
| 1 | Traducir y crear `/es/index.html` |
| 2 | Agregar language switcher al homepage EN |
| 3 | Traducir y crear `/experimentos/es/index.html` + switcher |
| 4 | Verificar que todos los links entre páginas funcionan en ambos idiomas |
| 5 | Push y deploy |
