# 🚀 Despliegue en Render — Halcones Paracaidismo

Guía para publicar la plataforma en **Render** y obtener una **URL pública**
(`https://halcones-paracaidismo.onrender.com`).

El repositorio ya incluye todo lo necesario: [`render.yaml`](render.yaml) (blueprint),
[`Dockerfile`](Dockerfile) (respeta `$PORT`) y [`Dockerfile.cron`](Dockerfile.cron)
(disparo diario de notificaciones).

---

## 0. Requisitos
- Una cuenta gratuita en **Render** → https://render.com
- El código en un repositorio **GitHub/GitLab** (la carpeta `halcones-platform/` debe
  ser la **raíz** del repo, porque ahí están `render.yaml` y el `Dockerfile`).

## 1. Subir el código a GitHub
```bash
cd halcones-platform
git init && git add . && git commit -m "Halcones Paracaidismo — plataforma"
git branch -M main
git remote add origin https://github.com/<tu-usuario>/halcones-paracaidismo.git
git push -u origin main
```

## 2. Crear los servicios con el Blueprint
1. En Render: **New +** → **Blueprint**.
2. Conecta el repositorio. Render detecta `render.yaml` y propone crear:
   - **halcones-paracaidismo** (web, Docker, plan free)
   - **halcones-db** (PostgreSQL, plan free)
   - **halcones-notificaciones** (cron diario)
3. Pulsa **Apply**. Render construye la imagen y levanta la app.
   - Al primer arranque se crean las tablas y se cargan los **datos de ejemplo**
     (`SEED_ON_STARTUP=true`).

## 3. Variables de entorno (secretos)
El blueprint genera solo `SECRET_KEY` y `CRON_SECRET`. Define manualmente en el
dashboard del servicio **web**:
- `PUBLIC_BASE_URL` → la URL que te dio Render (p. ej. `https://halcones-paracaidismo.onrender.com`).
- (Opcional) `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` para activar el correo.
  > También puedes configurar el SMTP **desde el panel admin** en *Notificaciones → Configurar correo*.

En el servicio **cron** (`halcones-notificaciones`):
- `APP_URL` → la misma URL pública del servicio web.
- `CRON_SECRET` → **el mismo valor** que el del servicio web (cópialo desde allí).

## 4. Base de datos: nota importante ⚠️
El **PostgreSQL gratis de Render expira (~30 días)**. Dos opciones:

- **Rápida (demo):** usa la base `halcones-db` del blueprint. Suficiente para mostrar.
- **Persistente (recomendada):** crea una base gratis en **Neon** (https://neon.tech)
  o **Supabase**, copia su *connection string* y pégala en `DATABASE_URL` del servicio
  web (elimina el `fromDatabase` o sobreescribe el valor). La app normaliza la URL
  automáticamente (acepta `postgres://`, `postgresql://` → usa el driver `psycopg`).

## 5. Verificar
- Abre la URL pública → deberías ver el **login**.
- Entra con `admin@halcones.co` / `admin123` (cámbiala luego en *Usuarios*).
- `GET /healthz` responde `{"status":"ok"}`.
- La app es **PWA**: en Chrome/Edge aparece el botón **Instalar**; en móvil, *Añadir a
  pantalla de inicio*.

## 6. Notificaciones automáticas
El cron `halcones-notificaciones` llama cada día a
`GET /notificaciones/cron?token=$CRON_SECRET`, que ejecuta todas las reglas **activas**.
También puedes ejecutarlas manualmente desde *Notificaciones → Ejecutar activas*.
> Alternativa sin cron de Render: un servicio gratuito como **cron-job.org** apuntando a
> esa misma URL con el token.

## 7. Dominio propio (opcional)
En el servicio web → **Settings → Custom Domains** → añade `app.halcones.co` (o el que
sea) y crea el registro **CNAME** que indique Render en tu proveedor de dominio.
Render provee el **certificado HTTPS** automáticamente.

---

## Notas de producción
- Cambia las contraseñas demo y `SECRET_KEY`/`CRON_SECRET` (el blueprint ya los genera).
- El plan **free** de Render “duerme” tras inactividad; el primer acceso tarda ~30 s en
  despertar. Un plan **Starter (~US$7/mes)** lo mantiene siempre activo.
- Los archivos subidos (manuales/videos) se guardan en el disco del contenedor, que es
  **efímero** en el plan free. Para persistirlos usa un **Disk** de Render o almacenamiento
  externo (S3/R2). Ver la propuesta comercial para el detalle de costos.
