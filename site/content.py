"""Contenido del portafolio — fuente única ES/EN.

Los textos del CV salen del documento validado (CV-Arquitecto). Las previsualizaciones
del panel de margen viven acá para que el build las emita como JSON.
"""

NAME = "Marcelo Burgos Cayupil"
PORTRAIT = "/images/marcelo-portrait.jpg"

LINKS = {
    "email": "mburgos@hackfluency.com",
    "linkedin": "https://www.linkedin.com/in/maburg/",
    "github": "https://github.com/mburgc",
    "reddit": "https://www.reddit.com/user/hackcocaine/",
    "youtube": "https://www.youtube.com/@HackCocaine",
    "kofi": "https://ko-fi.com/s/f256b35318",
    "logbook": "/bitacora/",
    "experiments": "/experiments/",
    "lab": "/lab/",
    "zenodo": "https://zenodo.org/records/18228132",
    "redbrain": "https://redbrain.hackfluency.com",
    "engram": "https://engram.cloud",
    "cv_pdf": "/assets/cv/marcelo-burgos-cv.pdf",
}

# Video de la charla BSides 2019 (ID conocido). La Fase 4 lo reemplaza por data/video.json.
FEATURED_VIDEO = {"id": "YwhioxWlUWo", "label": "Advanced SQL Injection — BSides Chile 2019"}

CONTENT = {
    "en": {
        "lang": "en",
        "other": {"href": "/es/", "label": "ES"},
        "title": "Marcelo Burgos — Solutions Architect & Technical Lead",
        "description": "Solutions architect and technical lead: software architecture, Python, AWS, AI systems and offensive security.",
        "role": "Solutions Architect · Technical Lead",
        "kicker": "Offensive Security · AI Systems · Software Engineering",
        "labels": {
            "profile": "Profile",
            "experience": "Experience",
            "projects": "Projects & publications",
            "talks": "Talks",
            "skills": "Skills",
            "education": "Education & certifications",
            "certs": "Certifications",
            "now": "Now",
            "peek": "Preview",
            "close": "Close",
            "contact": "Contact",
            "colophon": "Built with HTML, a Python build and no tracking.",
            "idle_note": "Seven years of offensive security, now applied to architecture and AI systems.",
            "idle_hint": "Hover an entry to preview it.",
        },
        "profile": "Solutions architect and technical lead with 7+ years designing and leading systems in critical environments: banking, government and retail. I translate business needs into defensible architectures and carry them end to end — design, implementation, deployment and operations. I think like an adversary: my foundation is advanced exploitation, vulnerability research and zero-day work on Linux. I lead the architecture of VigIA, built TOXIC (a Wi-Fi/Bluetooth assessment drone), worked with Anthropic training models for offensive security, and I am an OWASP OASIS AppSec Expert.",
        "experience": [
            {
                "id": "agil",
                "company": "Agil Chile",
                "role": "Senior Offensive Security Architect",
                "period": "09/2026 – Present",
                "location": "Santiago, Chile",
                "subroles": ["Strategic Partner · 01/2025 – 09/2026", "Director of Architecture · VigIA"],
                "bullets": [
                    "I lead the architecture and development of <b>VigIA</b>, the firm's AI Security platform: governance, prioritisation and AI risk roadmap.",
                    "I design the architecture of offensive services: threat model, scope, methodology and technical acceptance criteria.",
                    "I translate business needs into technical proposals and support the sale through delivery.",
                ],
            },
            {
                "id": "hackfluency",
                "company": "Hackfluency",
                "role": "Red and Purple Team Chief Officer",
                "period": "09/2024 – Present",
                "location": "Santiago, Chile",
                "subroles": [],
                "bullets": [
                    "Architect of <b>RedBrain</b> (formerly CodeRed): an MCP server that gives AI agents 25 tools and 1,234 adversarial techniques, local by design; 10+ active clients.",
                    "I lead Red and Purple Team and the full product cycle: discovery, solution design, pre-sales, delivery and support.",
                ],
                "link": {"href": LINKS["redbrain"], "label": "redbrain.hackfluency.com"},
            },
            {
                "id": "sepal",
                "company": "Sepal AI",
                "role": "AI Cyber Specialist",
                "period": "08/2025 – 09/2025",
                "location": "Los Angeles, USA (remote)",
                "subroles": [],
                "bullets": [
                    "Automated and containerised red-teaming environments inside Anthropic's language-model training and evaluation pipelines.",
                    "Designed adversarial evaluation scenarios for LLMs at scale.",
                ],
            },
            {
                "id": "7a",
                "company": "7ASecurity",
                "role": "External Consultant",
                "period": "04/2026 – 05/2026",
                "location": "Dublin, Ireland (remote)",
                "subroles": [],
                "bullets": ["Intensive code audit and manual and dynamic testing on production software."],
            },
            {
                "id": "bvs",
                "company": "BVS Security",
                "role": "Red Team & CTI Leader",
                "period": "02/2022 – 09/2024",
                "location": "Santiago, Chile",
                "subroles": [],
                "bullets": [
                    "Led Red Team and Cyber Threat Intelligence: day-0 research, adversary emulation and team training.",
                    "Scaled service valuation by <b>275%</b> (USD 800 → USD 3,000+ per engagement) and opened international markets.",
                    "Standardised methodologies, reporting and portfolio; compliance auditing and continuous improvement for critical financial services.",
                    "Manual code review, DevSec and full-stack pentesting: web, mobile, network and databases.",
                ],
            },
            {
                "id": "early",
                "company": "CronUp · OZnet · Novared",
                "role": "Red Team Operator · Penetration Tester · Cybersecurity Consultant",
                "period": "07/2019 – 12/2021",
                "location": "Santiago, Chile",
                "subroles": [],
                "bullets": [
                    "50+ assessments across banking, government and retail: web, mobile, network and IoT, on microservices, APIs and cloud deployments (AWS, Azure, Kubernetes, Docker).",
                    "Malware and exploits with EDR/AV/IPS evasion; <b>Domain Admin</b> compromise in Active Directory (MITRE ATT&amp;CK); SQL Injection with <b>RCE</b> on government systems.",
                    "SAST/DAST (Fortify, Frida, mobSF, ImmuniWeb), manual code review (SCA) and documentation under OWASP, MSTG, WSTG, PTES, NIST and OSSTMM.",
                ],
            },
        ],
        "projects": [
            {
                "id": "gw",
                "title": "Template-Free Geometric Analysis of Gravitational-Wave Events",
                "meta": "2026 · DOI 10.5281/zenodo.18228132",
                "desc": "Python pipeline (NumPy, SciPy, GWpy) over 47 LIGO-Virgo events; a 51-variable dataset.",
                "link": {"href": LINKS["zenodo"], "label": "Read on Zenodo"},
            },
            {
                "id": "toxic",
                "title": "TOXIC",
                "meta": "Creator",
                "desc": "Drone for automated Wi-Fi and Bluetooth network assessment.",
            },
            {
                "id": "engram",
                "title": "ENGRAM",
                "meta": "engram.cloud",
                "desc": "Cognitive architecture: LLM + graph (KùzuDB) + vector search (LanceDB) + local inference (Ollama), with Hebbian plasticity.",
                "link": {"href": LINKS["engram"], "label": "engram.cloud"},
            },
            {
                "id": "logbook",
                "title": "Red Team LogBook",
                "meta": "Technical book, ES/EN",
                "desc": "Vulnerability research: fuzzing, patch diffing and crash analysis. In-house Python + CI pipeline.",
                "link": {"href": LINKS["logbook"], "label": "Open the logbook"},
            },
        ],
        "talks": [
            {
                "id": "bsides2023",
                "event": "BSides Chile 2023",
                "title": "Darknet Horrors #1",
                "meta": "Live · delivered in Spanish",
            },
            {
                "id": "bsides2019",
                "event": "BSides Chile 2019",
                "title": "Advanced SQL Injection",
                "meta": "Online · delivered in Spanish",
                "video": FEATURED_VIDEO["id"],
                "link": {"href": "https://www.youtube.com/live/YwhioxWlUWo", "label": "Watch"},
            },
            {
                "id": "bounty",
                "event": "Private Bug Bounty",
                "title": "Fraud detection attack chain",
                "meta": "USD 2,000 award",
            },
        ],
        "skills": [
            ["Architecture", "end-to-end solutions · discovery and technical pre-sales · data and API modelling · team leadership · C-level communication"],
            ["Languages", "Python · JavaScript/TypeScript · SQL · PowerShell · C# · Bash"],
            ["Data", "NumPy · SciPy · signal processing · ETL pipelines · reproducible datasets"],
            ["Cloud & infra", "AWS · Azure · Docker · Kubernetes · CI/CD (GitHub Actions) · Linux"],
            ["AI", "RAG · MCP · multi-agent systems · adversarial LLM evaluation · prompt injection"],
        ],
        "education": [
            ["Graduate Diploma in Philosophy of Science and Complex Systems", "IFICC · 2026"],
            ["Cyber Warfare and Terrorism", "Charles Sturt University · Distinction 78/100 · 2020"],
            ["Ethical Hacking &amp; Red Team", "Universidad Autónoma de Madrid · 2018"],
            ["RFID/NFC Penetration Testing", "8.8 Nine · 2019"],
        ],
        "certs": "CRTP · CEH · AWSE · CCNA R&amp;S · CVSS 4.0 · API Penetration Testing (12 h) · Introduction to CIP",
        "languages": "Spanish native · English C2 (IELTS 6.5) · Portuguese basic",
    },
    "es": {
        "lang": "es",
        "other": {"href": "/", "label": "EN"},
        "title": "Marcelo Burgos — Arquitecto de Soluciones y Líder Técnico",
        "description": "Arquitecto de soluciones y líder técnico: arquitectura de software, Python, AWS, sistemas de IA y seguridad ofensiva.",
        "role": "Arquitecto de Soluciones · Líder Técnico",
        "kicker": "Seguridad Ofensiva · Sistemas de IA · Ingeniería de Software",
        "labels": {
            "profile": "Perfil",
            "experience": "Experiencia",
            "projects": "Proyectos y publicaciones",
            "talks": "Charlas",
            "skills": "Habilidades",
            "education": "Educación y certificaciones",
            "certs": "Certificaciones",
            "now": "Ahora",
            "peek": "Vista previa",
            "close": "Cerrar",
            "contact": "Contacto",
            "colophon": "Hecho con HTML, un build en Python y sin rastreo.",
            "idle_note": "Siete años de seguridad ofensiva, hoy aplicados a arquitectura y sistemas de IA.",
            "idle_hint": "Pasá el cursor sobre una entrada para verla.",
        },
        "profile": "Arquitecto de soluciones y líder técnico con más de 7 años diseñando y dirigiendo sistemas en entornos críticos: banca, gobierno y retail. Traduzco necesidades de negocio en arquitecturas defendibles y las llevo de punta a punta —diseño, implementación, despliegue y operación—. Pienso como adversario: mi base es la explotación avanzada, la investigación de vulnerabilidades y el zero-day en Linux. Dirijo la arquitectura de VigIA, construí TOXIC (dron de evaluación Wi-Fi/Bluetooth), colaboré con Anthropic entrenando modelos para seguridad ofensiva y soy OWASP OASIS AppSec Expert.",
        "experience": [
            {
                "id": "agil",
                "company": "Agil Chile",
                "role": "Arquitecto Senior de Seguridad Ofensiva",
                "period": "09/2026 – Presente",
                "location": "Santiago, Chile",
                "subroles": ["Socio Estratégico · 01/2025 – 09/2026", "Director de Arquitectura · VigIA"],
                "bullets": [
                    "Dirijo la arquitectura y el desarrollo de <b>VigIA</b>, la plataforma de AI Security de la firma: gobierno, priorización y hoja de ruta del riesgo de IA.",
                    "Diseño la arquitectura de los servicios ofensivos: modelo de amenaza, alcance, metodología y criterios de aceptación técnica.",
                    "Traduzco necesidades de negocio en propuestas técnicas y acompaño la venta hasta la entrega.",
                ],
            },
            {
                "id": "hackfluency",
                "company": "Hackfluency",
                "role": "Director de Red y Purple Team",
                "period": "09/2024 – Presente",
                "location": "Santiago, Chile",
                "subroles": [],
                "bullets": [
                    "Arquitecto de <b>RedBrain</b> (ex CodeRed): servidor MCP que entrega a agentes de IA 25 herramientas y 1.234 técnicas adversariales, con ejecución local por diseño; 10+ clientes activos.",
                    "Dirijo Red y Purple Team y el ciclo completo de producto: discovery, diseño de solución, preventa, entrega y soporte.",
                ],
                "link": {"href": LINKS["redbrain"], "label": "redbrain.hackfluency.com"},
            },
            {
                "id": "sepal",
                "company": "Sepal AI",
                "role": "AI Cyber Specialist",
                "period": "08/2025 – 09/2025",
                "location": "Los Ángeles, EE.UU. (remoto)",
                "subroles": [],
                "bullets": [
                    "Automaticé y containericé entornos de red teaming dentro de los pipelines de entrenamiento y evaluación de modelos de lenguaje de Anthropic.",
                    "Diseñé escenarios de evaluación adversarial para LLM a escala.",
                ],
            },
            {
                "id": "7a",
                "company": "7ASecurity",
                "role": "Consultor Externo",
                "period": "04/2026 – 05/2026",
                "location": "Dublín, Irlanda (remoto)",
                "subroles": [],
                "bullets": ["Auditoría de código intensiva y pruebas manuales y dinámicas sobre software en producción."],
            },
            {
                "id": "bvs",
                "company": "BVS Security",
                "role": "Red Team & CTI Leader",
                "period": "02/2022 – 09/2024",
                "location": "Santiago, Chile",
                "subroles": [],
                "bullets": [
                    "Lideré Red Team y Cyber Threat Intelligence: investigación de día 0, emulación de adversarios y formación del equipo.",
                    "Escalé la valorización del servicio un <b>275%</b> (USD 800 → USD 3.000+ por engagement) y abrí mercados internacionales.",
                    "Estandaricé metodologías, informes y portafolio; auditoría de cumplimiento y mejora continua en servicios financieros críticos.",
                    "Revisiones manuales de código, DevSec y pentest integral: web, móvil, red y bases de datos.",
                ],
            },
            {
                "id": "early",
                "company": "CronUp · OZnet · Novared",
                "role": "Red Team Operator · Penetration Tester · Consultor de Ciberseguridad",
                "period": "07/2019 – 12/2021",
                "location": "Santiago, Chile",
                "subroles": [],
                "bullets": [
                    "50+ evaluaciones en banca, gobierno y retail: web, móvil, red e IoT, sobre microservicios, APIs y despliegues cloud (AWS, Azure, Kubernetes, Docker).",
                    "Malware y exploits con evasión de EDR/AV/IPS; compromiso de <b>Domain Admin</b> en Active Directory (MITRE ATT&amp;CK); SQL Injection con <b>RCE</b> en sistemas gubernamentales.",
                    "SAST/DAST (Fortify, Frida, mobSF, ImmuniWeb), revisión manual de código (SCA) y documentación bajo OWASP, MSTG, WSTG, PTES, NIST y OSSTMM.",
                ],
            },
        ],
        "projects": [
            {
                "id": "gw",
                "title": "Template-Free Geometric Analysis of Gravitational-Wave Events",
                "meta": "2026 · DOI 10.5281/zenodo.18228132",
                "desc": "Pipeline Python (NumPy, SciPy, GWpy) sobre 47 eventos LIGO-Virgo; dataset de 51 variables.",
                "link": {"href": LINKS["zenodo"], "label": "Leer en Zenodo"},
            },
            {
                "id": "toxic",
                "title": "TOXIC",
                "meta": "Creador",
                "desc": "Dron para la evaluación automatizada de redes Wi-Fi y Bluetooth.",
            },
            {
                "id": "engram",
                "title": "ENGRAM",
                "meta": "engram.cloud",
                "desc": "Arquitectura cognitiva: LLM + grafo (KùzuDB) + búsqueda vectorial (LanceDB) + inferencia local (Ollama), con plasticidad hebbiana.",
                "link": {"href": LINKS["engram"], "label": "engram.cloud"},
            },
            {
                "id": "logbook",
                "title": "Red Team LogBook",
                "meta": "Libro técnico ES/EN",
                "desc": "Investigación de vulnerabilidades: fuzzing, patch diffing y análisis de crashes. Pipeline propio en Python + CI.",
                "link": {"href": LINKS["logbook"], "label": "Abrir la bitácora"},
            },
        ],
        "talks": [
            {
                "id": "bsides2023",
                "event": "BSides Chile 2023",
                "title": "Darknet Horrors #1",
                "meta": "Presencial · dictada en español",
            },
            {
                "id": "bsides2019",
                "event": "BSides Chile 2019",
                "title": "Advanced SQL Injection",
                "meta": "Online · dictada en español",
                "video": FEATURED_VIDEO["id"],
                "link": {"href": "https://www.youtube.com/live/YwhioxWlUWo", "label": "Ver"},
            },
            {
                "id": "bounty",
                "event": "Bug Bounty privado",
                "title": "Cadena de ataque para detección de fraude",
                "meta": "Premio USD 2.000",
            },
        ],
        "skills": [
            ["Arquitectura", "soluciones end-to-end · discovery y preventa técnica · modelamiento de datos y APIs · dirección de equipos · comunicación C-Level"],
            ["Lenguajes", "Python · JavaScript/TypeScript · SQL · PowerShell · C# · Bash"],
            ["Datos", "NumPy · SciPy · procesamiento de señales · pipelines ETL · datasets reproducibles"],
            ["Cloud e infra", "AWS · Azure · Docker · Kubernetes · CI/CD (GitHub Actions) · Linux"],
            ["IA", "RAG · MCP · sistemas multi-agente · evaluación adversarial de LLM · prompt injection"],
        ],
        "education": [
            ["Diplomatura en Filosofía de las Ciencias y Sistemas Complejos", "IFICC · 2026"],
            ["Cyber Warfare and Terrorism", "Charles Sturt University · Distinction 78/100 · 2020"],
            ["Ethical Hacking &amp; Red Team", "Universidad Autónoma de Madrid · 2018"],
            ["RFID/NFC Penetration Testing", "8.8 Nine · 2019"],
        ],
        "certs": "CRTP · CEH · AWSE · CCNA R&amp;S · CVSS 4.0 · API Penetration Testing (12 h) · Introduction to CIP",
        "languages": "Español nativo · Inglés C2 (IELTS 6.5) · Portugués básico",
    },
}


def previews(lang: str) -> dict:
    """Contenido del panel de margen, por id."""
    c = CONTENT[lang]
    out = {}
    for job in c["experience"]:
        out[job["id"]] = {
            "kind": "experience",
            "title": job["company"],
            "meta": f'{job["role"]} · {job["period"]}',
            "bullets": job["bullets"],
            "link": job.get("link"),
        }
    for project in c["projects"]:
        out[project["id"]] = {
            "kind": "project",
            "title": project["title"],
            "meta": project["meta"],
            "text": project["desc"],
            "link": project.get("link"),
        }
    for talk in c["talks"]:
        out[talk["id"]] = {
            "kind": "talk",
            "title": talk["title"],
            "meta": f'{talk["event"]} · {talk["meta"]}',
            "video": talk.get("video"),
            "link": talk.get("link"),
        }
    return out


def canonical(lang: str) -> str:
    return "https://mburgc.github.io/" if lang == "en" else "https://mburgc.github.io/es/"

