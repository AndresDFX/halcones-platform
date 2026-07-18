# 🪂 Halcones Paracaidismo — Plataforma de Gestión

Plataforma web **integral** para la escuela **Halcones Paracaidismo** (Cali, Colombia).
Permite gestionar de forma unificada los **cursos**, el **seguimiento de estudiantes**,
la **parte financiera** y la **programación de saltos** (aviones, vuelos y quién salta en cada uno).

Construida con la identidad de marca real de Halcones (logo, colores del manual oficial:
vino `#7E0704`, rojo `#A93037`, dorado y negro).

---

## ✨ Funcionalidades

| Módulo | Qué hace |
|---|---|
| **Cursos** | Catálogo informativo (AFF de 7 niveles, Tándem…), temario, precios, requisitos, y **videos + manuales** (subir archivo o referenciar YouTube). |
| **Estudiantes** | Fichas completas (cédula, peso, EPS, contacto de emergencia), inscripciones y **bitácora de saltos** con avance por nivel. |
| **Finanzas** | Registro de pagos (reserva, abono, saldo) por transferencia/efectivo/link, cartera por cobrar, ingresos por método y por mes. |
| **Manifiesto** | Jornadas de salto, **vuelos (loads)** por avión y asignación de **quién va en cada vuelo** (alumnos, instructores, tándem, cámara). |
| **Usuarios** | Gestión de cuentas (admin): CRUD de estudiantes, instructores y admins, con restablecer contraseña y activar/desactivar. Sin registro público. |
| **Nómina** | Pagos **a instructores** (compensación por salto/salario/bono), separados de las finanzas de estudiantes. El instructor solo ve los suyos. |
| **Notificaciones** | Correos **programables desde el admin**: recordatorio del próximo salto y oferta de curso a quienes saltaron una sola vez. Plantillas, tiempos y SMTP configurables en el panel. |
| **Portal del estudiante** | Cada estudiante ve sus cursos, videos, manual, su avance, sus pagos y sus próximos saltos. |
| **API REST** | Endpoints JSON documentados en `/api/docs` (Swagger); los financieros requieren rol admin. |
| **PWA** | Instalable en móvil/escritorio, con service worker (funciona offline básico) e iconos de marca. |

## 👥 Roles y permisos

No hay **registro público**: el administrador crea todas las cuentas y entrega las
credenciales a estudiantes e instructores.

- **Administrador** — control total. **CRUD de todas las entidades**: usuarios
  (estudiantes, instructores y otros admins), cursos, inscripciones, **finanzas del
  negocio** (ingresos, cartera, pagos de estudiantes) y **nómina de instructores**,
  manifiesto y aviones.
- **Instructor** — parte **operativa y docente**: ve estudiantes y registra su
  **bitácora**, gestiona el **manifiesto**, ve cursos y añade contenido. **No ve las
  finanzas del negocio** (ni ingresos, ni cartera, ni pagos de estudiantes): solo
  consulta **sus propios pagos** (su compensación) en *Mis pagos*.
- **Estudiante** — su portal: contenido del curso, avance, **sus** pagos y saltos.

| Acción | Admin | Instructor | Estudiante |
|---|:--:|:--:|:--:|
| Crear/editar usuarios (cualquier rol) | ✅ | — | — |
| Cursos: crear/editar · añadir contenido | ✅ · ✅ | — · ✅ | ver · — |
| Estudiantes: ver/bitácora · crear/inscribir | ✅ · ✅ | ✅ · — | — |
| Finanzas del negocio (ingresos, cartera, pagos) | ✅ | ❌ | solo lo suyo |
| Nómina de instructores | ✅ (gestiona) | ve solo lo suyo | — |
| Manifiesto y aviones | ✅ | ✅ (aviones: ver) | ve sus saltos |

---

## 🚀 Puesta en marcha (Docker)

Requisitos: **Docker** y **Docker Compose**.

```bash
cd halcones-platform
docker compose up -d --build
```

Abre 👉 **http://localhost:8080**

La base de datos se crea y se **siembra automáticamente** con datos de ejemplo
(basados en el manual AFF y en el caso real del chat de WhatsApp de Halcones).

### 🔑 Cuentas de demostración

| Rol | Correo | Contraseña |
|---|---|---|
| Administrador | `admin@halcones.co` | `admin123` |
| Instructor | `instructor@halcones.co` | `instructor123` |
| Estudiante | `julian@example.com` | `estudiante123` |

> En la pantalla de login puedes hacer clic en cualquier cuenta demo para autocompletarla.

### Comandos útiles

```bash
docker compose logs -f web     # ver logs de la app
docker compose down            # detener
docker compose down -v         # detener y borrar datos (resetea el seed)
```

---

## 🧱 Stack técnico

- **Backend:** FastAPI (Python 3.12) · SQLAlchemy 2 · Jinja2
- **Auth:** JWT en cookie httponly · hashing bcrypt · control por rol
- **Base de datos:** PostgreSQL 16
- **Frontend:** HTML server-rendered + sistema de diseño CSS propio de marca
- **Orquestación:** Docker Compose (servicios `web` + `db`)

Ver **[CONTEXT.md](CONTEXT.md)** para la documentación de arquitectura, modelo de datos y decisiones de diseño.

---

## 📂 Estructura

```
halcones-platform/
├─ docker-compose.yml        # web (FastAPI) + db (Postgres)
├─ Dockerfile
├─ requirements.txt
├─ app/
│  ├─ main.py                # arranque, rutas, manejo de errores
│  ├─ config.py  database.py  models.py  security.py  deps.py
│  ├─ seed.py                # datos de ejemplo (manual AFF + chat real)
│  ├─ routers/               # auth, dashboard, courses, students, finance, manifest, portal, api
│  ├─ templates/             # UI (Jinja2)
│  ├─ static/                # CSS, JS, logo e imágenes de marca
│  └─ seed_assets/           # MANUALAFF123.pdf (se carga como manual del curso)
└─ CONTEXT.md
```
