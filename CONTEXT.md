# 📓 CONTEXT.md — Plataforma Halcones Paracaidismo

Archivo de contexto del proyecto: qué es, cómo está construido y por qué. Pensado para que
cualquier persona (o asistente de IA) retome el desarrollo con el panorama completo.

---

## 1. Contexto de negocio

**Halcones Paracaidismo** (marca comercial: *Halcones Cali Paracaidismo*) es una escuela de
paracaidismo en **Santiago de Cali, Colombia**.

- **Zona de salto:** *Braaap Park*, vía Rozo–Cali, a ~15 min del aeropuerto Alfonso Bonilla Aragón.
- **Contacto:** +57 301 6265503 · halconesparacaidismo@gmail.com · IG @halconescali_paracaidismo
- **Producto estrella:** **Curso AFF (Caída Libre Acelerada)** — 7 niveles, salto desde 10.000 ft,
  ~30 s de caída libre por salto. Precio **$6.333.333 COP**; reserva desde **$2.000.000**.
  Incluye: manual, teoría + práctica en tierra, 7 saltos con instructor, alquiler de equipos
  (paracaídas, overol, altímetro, casco, gafas, radio), bitácora y **videos de los saltos**.
- **Operación real (del chat):** la teoría se da por partes los fines de semana en la zona;
  los pagos son por transferencia/consignación/efectivo/link; se piden documentos (cédula,
  certificado EPS, exámenes ocupacionales, contacto de emergencia); los videos se comparten
  por enlaces (YouTube / fromsmash); y **hay que confirmar quién va en cada vuelo** porque
  cada día hay varios vuelos con cupos limitados.

Estas realidades del negocio son las que la plataforma modela.

### Fuentes usadas
- `MANUALAFF123.pdf` — Manual de Instrucción AFF (76 páginas). De aquí salen el temario,
  los 7 niveles, el logo (escudo con "H" + halcón) y los **colores de marca**.
- `Chat de WhatsApp con Halcones Paracaidismo.txt` — caso real del estudiante **Julián Andrés
  Castaño Espinosa**, usado como dato de ejemplo (reserva, pagos, saltos, documentos).

---

## 2. Identidad de marca

Extraída del logo y el manual oficiales:

| Token | Color | Uso |
|---|---|---|
| `--maroon` | `#7E0704` | Barras del manual, sidebar, títulos, botones primarios |
| `--red` | `#A93037` | Rojo del logo, acentos, degradados |
| `--gold` | `#F2B705` | Detalles, resaltados, avatar |
| `--ink` | `#16130F` | Texto y trazos del logo |
| fondo | `#f5f1ea` | Papel / lienzo |

- **Logo:** escudo tipo rombo (estilo "Superman") con una **H** en rojo, una **cabeza de halcón**
  y un blanco de aterrizaje. Assets en `app/static/img/`:
  `logo-shield.png` (escudo, fondo transparente), `logo-mark.png` (recorte), `wordmark-dark/light.png`
  (texto "HALCONES Paracaidismo") y `favicon.png`.
- **Tipografía:** *Oswald* (títulos, condensada como el wordmark) + *Inter* (texto).

El sistema de diseño completo vive en `app/static/css/app.css`.

---

## 3. Arquitectura y stack

```
Navegador ──HTTP──> [web: FastAPI + Uvicorn]  ──SQL──>  [db: PostgreSQL 16]
                         │  Jinja2 (UI)
                         │  /api/* (REST + Swagger)
                         └─ /uploads (manuales y videos subidos, volumen persistente)
```

- **FastAPI** sirve tanto la **UI server-rendered** (Jinja2) como una **API REST JSON** (`/api`).
- **Autenticación por sesión:** al iniciar sesión se emite un **JWT** que viaja en una cookie
  `httponly` (`halcones_session`). En cada request `deps.get_current_user` lo decodifica.
- **Autorización por rol:** `deps.require_user`, `staff_required` (admin+instructor) y
  `admin_required`. Las páginas protegidas redirigen a `/login`; los accesos sin permiso
  muestran una página 403 de marca.
- **Persistencia:** SQLAlchemy 2. En Docker usa Postgres; sin `DATABASE_URL` cae a SQLite
  (útil para pruebas locales rápidas).
- **Arranque:** `main.on_startup` crea las tablas (`Base.metadata.create_all`) y ejecuta el
  **seed idempotente** (`seed.py`) si `SEED_ON_STARTUP=true`.

### ¿Por qué este stack?
Se priorizó una **versión inicial funcional, robusta y fácil de levantar/probar**: un solo
contenedor de aplicación (menos piezas que fallen que un SPA + build de Node + Nginx),
con Swagger incluido y una UI de marca cuidada. Es directo de extender a un SPA más adelante
porque ya existe la capa `/api`.

---

## 4. Modelo de datos (`app/models.py`)

- **User** — usuario único con `role` (`admin` | `instructor` | `estudiante`). Incluye campos
  de estudiante (peso, EPS, dirección, contacto de emergencia) y de instructor (licencia).
- **Course** → **CourseLevel** (niveles/saltos) y **MediaResource** (videos/manuales;
  `url` externa **o** `archivo` subido; detecta y embebe YouTube).
- **Enrollment** (inscripción estudiante↔curso) → **LevelProgress** (bitácora por nivel) y
  **Payment** (pagos de estudiantes). Propiedades calculadas: `total_pagado`, `saldo`, `porcentaje_avance`.
- **InstructorPayment** — pago HACIA un instructor (nómina/compensación). Separado de las
  finanzas del negocio: el instructor solo ve los suyos.
- **Aircraft** (aviones) · **JumpDay** (jornada) → **Load** (vuelo) → **LoadSlot**
  (persona asignada a un vuelo: alumno/instructor/tándem/cámara) = *quién va en cada vuelo*.
- **NotificationRule** (regla programable por el admin) → **NotificationLog** (bitácora de
  correos generados: enviado/simulado/error). **Setting** (clave-valor, p.ej. config SMTP).

Los cuatro pilares del encargo mapean así:
1. Cursos informativos → `Course` / `CourseLevel` / `MediaResource`
2. Seguimiento de estudiantes → `Enrollment` / `LevelProgress`
3. Finanzas → `Payment` (+ saldos calculados)
4. Programación de saltos → `Aircraft` / `JumpDay` / `Load` / `LoadSlot`

---

## 5. Rutas principales (`app/routers/`)

| Prefijo | Archivo | Contenido |
|---|---|---|
| `/login`, `/logout` | `auth.py` | Inicio/cierre de sesión (sin registro público) |
| `/` | `dashboard.py` | Panel según rol: admin (finanzas) · instructor (operativo) · estudiante |
| `/cursos` | `courses.py` | Catálogo, detalle, crear/editar (admin), niveles (admin), media (staff) |
| `/estudiantes` | `students.py` | Fichas y bitácora (staff); editar/inscribir (admin) |
| `/usuarios` | `users.py` | **CRUD de usuarios de todos los roles (solo admin)** |
| `/finanzas` | `finance.py` | **Finanzas del negocio y nómina de instructores (solo admin)** |
| `/instructor/pagos` | `instructor.py` | Vista propia del instructor: sus pagos (compensación) |
| `/notificaciones` | `notifications.py` | **Reglas de correo + config SMTP + cron (solo admin)** |
| `/manifiesto` | `manifest.py` | Jornadas, vuelos, asignaciones (staff); aviones (crear: admin) |
| `/portal` | `portal.py` | Vistas del estudiante (contenido, pagos, saltos, perfil) |
| `/api` | `api.py` | REST JSON + Swagger en `/api/docs` (endpoints financieros: solo admin) |
| `/sw.js`, `/manifest.webmanifest`, `/offline` | `main.py` | **PWA** (service worker, manifiesto, página offline) |

### Notificaciones (servicio `notifications.py`)
Correos **programables desde el admin**. Dos tipos: `recordatorio_salto` (a estudiantes con
salto próximo, N días antes) y `oferta_curso` (a quienes saltaron **una sola vez** hace ≥ X días
y no están en AFF). Plantillas con variables (`{nombre}`, `{fecha_salto}`, `{curso}`…), dedupe por
`clave`, y config SMTP editable en el panel (tabla `Setting`, con prioridad sobre variables de
entorno). Sin SMTP → modo **simulado** (se registra, no se envía). Cron en
`GET /notificaciones/cron?token=CRON_SECRET` (para Render Cron Job).

### PWA y despliegue
Instalable (manifest + service worker con offline básico, iconos de marca). Despliegue en
**Render**: `render.yaml` (web Docker + Postgres + cron), `Dockerfile` respeta `$PORT`,
`Dockerfile.cron` dispara notificaciones. Guía paso a paso en **DEPLOY_RENDER.md**. El
Postgres gratis de Render expira (~30 días) → usar Neon/Supabase para persistencia.

### Reglas de negocio de permisos
- **Sin registro público**: el admin crea todas las cuentas (`/usuarios`) y entrega credenciales.
- **Admin**: CRUD de todas las entidades, incluidos usuarios; ve todas las finanzas.
- **Instructor**: operativo/docente (estudiantes, bitácora, manifiesto, contenido). **No ve
  finanzas del negocio**; solo **sus propios pagos**. Guardas: `staff_required` (operativo,
  admin+instructor) vs `admin_required` (usuarios, finanzas, precios/inscripción, CRUD de cursos).
- **Estudiante**: solo su portal.

---

## 6. Datos de ejemplo (`app/seed.py`)

Idempotente (si existe `admin@halcones.co`, no re-siembra). Crea:
- **Usuarios:** 1 admin, 2 instructores (Camilo Restrepo, Laura Marín), 5 estudiantes.
- **Cursos:** AFF (7 niveles, con manual PDF real + 2 videos) y Tándem.
- **Julián** (caso real): inscrito en AFF, reserva $2M + abono $1M, Nivel 1 aprobado,
  Nivel 2 en curso; datos reales de cédula, peso, EPS y contacto de emergencia.
- Otros estudiantes en distintos estados (uno completó el curso, otro a mitad, una recién
  reservó, otro en tándem) para poblar finanzas y avance.
- **Aviones:** HK-4512 (Cessna 206) y HK-2890 (Cessna 182).
- **Nómina:** pagos de compensación a los instructores (por salto y salario) como ejemplo.
- **Jornadas:** una pasada (6/7/2026, cerrada) y una próxima (19/7/2026) con 3 vuelos y
  personas asignadas — incluye a Julián en el vuelo del mediodía (Nivel 2).

El manual `MANUALAFF123.pdf` se copia a `/app/uploads/curso-1/` y queda enlazado como recurso
del curso AFF (los estudiantes lo abren desde su portal).

---

## 7. Cómo ejecutar y credenciales

```bash
docker compose up -d --build      # http://localhost:8080
```

| Rol | Correo | Contraseña |
|---|---|---|
| Admin | admin@halcones.co | admin123 |
| Instructor | instructor@halcones.co | instructor123 |
| Estudiante | julian@example.com | estudiante123 |

Puerto host **8080** (configurable en `docker-compose.yml`). `docker compose down -v` borra
los volúmenes y reinicia el seed.

---

## 8. Estado y próximos pasos sugeridos

**Listo:** auth+roles, CRUD de cursos/estudiantes/pagos, bitácora, manifiesto completo,
subida de videos/manuales, portal del estudiante, API REST, seed realista, Docker.

**Posibles mejoras futuras:**
- Migraciones con Alembic (hoy se usa `create_all`).
- Notificaciones (WhatsApp/email) de programación de saltos y recordatorios de pago.
- Reportes financieros exportables (PDF/Excel) y facturación electrónica.
- Carga de documentos del estudiante (cédula, EPS, exámenes) con verificación.
- Portal público de inscripción/reserva en línea con pasarela de pago.
- Migrar la UI a un SPA (React) reutilizando la capa `/api` ya existente.

> ⚠️ Seguridad para producción: cambiar `SECRET_KEY`, credenciales de Postgres y las
> contraseñas demo; servir tras HTTPS; endurecer validaciones de subida de archivos.
