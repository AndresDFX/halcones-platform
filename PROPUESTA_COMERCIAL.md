# 🪂 Propuesta Comercial — Plataforma de Gestión Halcones Paracaidismo

**Preparada para:** Halcones Paracaidismo (Cali, Colombia)
**Versión:** 1.0 · Julio 2026
**Objeto:** Plataforma web integral para la gestión de cursos, estudiantes, finanzas,
programación de saltos y notificaciones automáticas.

> Cifras en pesos colombianos (COP). Referencia de conversión: 1 USD ≈ 4.000 COP.
> Los precios de terceros (hosting, dominio, correo) son estimados de julio 2026 y los paga
> Halcones directamente al proveedor; se incluyen para total transparencia.

---

## 1. Resumen ejecutivo

Halcones Paracaidismo vende, entre otros, el **curso AFF a $6.333.333** por estudiante.
Hoy la gestión (cursos, pagos, documentos, programación de vuelos y seguimiento de alumnos)
se lleva por WhatsApp y de forma manual. Esta plataforma **centraliza toda la operación** en
un solo lugar, con acceso por roles y desde el celular.

**La propuesta de valor es simple:** la plataforma cuesta **menos que vender un solo curso
AFF**, y está diseñada precisamente para ayudar a **vender más cursos y no perder clientes**:

- **Recordatorios automáticos** del próximo salto → menos inasistencias y mejor experiencia.
- **Reactivación de clientes**: a quien saltó una sola vez (p. ej. un tándem) se le ofrece
  automáticamente el curso AFF cada cierto tiempo.
- **Seguimiento financiero** claro (ingresos, cartera por cobrar, nómina de instructores).

> **Con recuperar o convertir UN solo estudiante AFF adicional al año, la plataforma y toda su
> operación anual quedan pagadas.** El retorno llega con el primer curso extra.

---

## 2. Qué incluye la plataforma (ya construida y funcionando)

| Módulo | Descripción |
|---|---|
| **Gestión de cursos** | Catálogo informativo (AFF de 7 niveles, Tándem…), temario, precios, requisitos y **videos + manuales** (subir archivo o enlazar YouTube). |
| **Seguimiento de estudiantes** | Fichas completas (cédula, peso, EPS, contacto de emergencia), inscripciones y **bitácora de saltos** por nivel. |
| **Finanzas** | Pagos (reserva/abono/saldo), cartera por cobrar, ingresos por método y por mes, **nómina de instructores**. |
| **Programación de saltos (manifiesto)** | Jornadas, vuelos por avión y asignación de **quién va en cada vuelo** (alumno/instructor/tándem/cámara). |
| **Notificaciones por correo** | **Programables desde el panel del administrador**: recordatorio de próximo salto y oferta de curso a quienes saltaron una sola vez. |
| **Roles y seguridad** | Administrador, Instructor y Estudiante, cada uno con su propia vista y permisos. Sin registro público (el admin crea las cuentas). |
| **Portal del estudiante** | El alumno ve su curso, videos, manual, avance, pagos y próximos saltos. |
| **App instalable (PWA)** | Se instala en el celular/PC como una app, con ícono de marca y uso básico sin conexión. |
| **Identidad de marca** | Logo, colores (vino/rojo/negro) y estilo de Halcones en toda la interfaz. |

---

## 3. Valor de mercado vs. precio de esta propuesta

Según el mercado colombiano (2025-2026), un **sistema de gestión web a la medida** para una
PyME cuesta típicamente entre **$15.000.000 y $60.000.000 COP** (un MVP intermedio ronda los
$12–32 millones). Esta plataforma —por su alcance (6 módulos, 3 roles, notificaciones, PWA)—
se ubica cómodamente en ese rango de valor.

**Sin embargo, esta es una versión inicial y la ofrecemos con un precio de lanzamiento
deliberadamente por debajo de un curso AFF**, para que la decisión sea sencilla y el retorno,
inmediato.

---

## 4. Inversión y forma de pago

| Concepto | Valor |
|---|---|
| **Precio total (llave en mano)** | **$5.500.000 COP** — ~13 % menos que un curso AFF |

**Forma de pago (50 / 50):**

| Momento | Porcentaje | Valor |
|---|---|---|
| **Anticipo** — antes de empezar | 50 % | **$2.750.000 COP** |
| **Saldo** — al finalizar el desarrollo (entrega) | 50 % | **$2.750.000 COP** |

Incluye: instalación/despliegue en Render con URL pública, carga de la información inicial,
personalización de marca, capacitación de uso (1 sesión) y la **garantía de cambios** descrita
en la sección 8.

---

## 5. Costos recurrentes (los paga Halcones al proveedor)

Estos servicios no los cobra el desarrollador; se contratan a nombre de Halcones. Se listan
para que quede claro el costo real de operar la plataforma.

### 5.1 Hosting (Render.com)

| Escenario | Costo mensual | Costo anual | Notas |
|---|---|---|---|
| **Arranque / demostración** | **$0** | **$0** | Plan gratuito. Limitación: la app “se duerme” tras 15 min de inactividad y tarda ~30 s en despertar. Ideal para mostrar y arrancar. |
| **Producción (recomendado)** | **~$28.000–$52.000** | **~$336.000–$624.000** | Servicio web “Starter” siempre activo (US$7/mes ≈ $28.000) + base de datos persistente (Neon gratis, o Render Postgres ~$24.000/mes). SSL y HTTPS **gratis**. |
| Cron de notificaciones | ~$4.000 (o $0) | ~$48.000 (o $0) | Render Cron (mín. US$1/mes) **o** un servicio gratuito tipo cron-job.org. |

> ⚠️ El PostgreSQL **gratis** de Render **expira a los ~30 días**. Para producción se usa una
> base gratuita y persistente en **Neon** (neon.tech), sin costo, o el Postgres pago de Render.

### 5.2 Dominio propio (opcional pero recomendado)

| Tipo | Costo anual aprox. | Notas |
|---|---|---|
| `.com` | **$40.000 – $92.000 COP/año** | Más económico y estable (p. ej. Cloudflare al costo ~$40.000). |
| `.co` (Colombia) | **$150.000 – $230.000 COP/año** | Identidad local; la renovación es más costosa que el `.com`. |

El certificado de seguridad (HTTPS) es **gratuito** y automático en Render.

### 5.3 Correo para notificaciones

| Servicio | Costo | Notas |
|---|---|---|
| **Brevo / Resend (capa gratuita)** | **$0** | Brevo: 300 correos/día gratis; Resend: 3.000/mes gratis. **Suficiente** para los recordatorios y ofertas de Halcones. |
| Plan pago (si crece el volumen) | ~$36.000/mes | Brevo Starter (5.000 correos/mes) u opciones similares. |

### 5.4 Resumen de costos recurrentes

- **Modo arranque/demo:** prácticamente **$0/año** (hosting free + correo free; solo dominio si se desea).
- **Modo producción típico:** **~$700.000 – $1.000.000 COP/año** (hosting siempre activo + dominio `.co` + correo gratis).

---

## 6. Mantenimiento y soporte (opcional)

Recomendado para mantener la plataforma actualizada, segura y evolucionando.

| Plan | Precio | Incluye |
|---|---|---|
| **Soporte mensual** | **$350.000 COP/mes** | Monitoreo, copias de seguridad, actualizaciones de seguridad, hasta 3 h/mes de cambios menores y atención de incidencias. |
| **Bolsa de horas** | **$130.000 COP/hora** | Para nuevas funcionalidades o cambios puntuales, bajo demanda. |

> Referencia de industria: el mantenimiento anual de un sistema a medida suele ser el
> **15 %–20 % del valor del proyecto**. El plan mensual propuesto está dentro de ese estándar.

---

## 7. Retorno de inversión (ROI)

| Concepto | Valor |
|---|---|
| Precio de la plataforma (única vez) | $5.500.000 |
| Operación anual estimada (hosting + dominio + correo) | ~$700.000 – $1.000.000 |
| **Valor de UN curso AFF** | **$6.333.333** |

**Punto de equilibrio: menos de un curso AFF.** Si la plataforma —gracias a los recordatorios
y a la reactivación de quienes saltaron una vez— ayuda a **cerrar un solo estudiante AFF
adicional al año**, ya cubre su costo total. Todo estudiante adicional a partir de ahí es
ganancia neta, además del ahorro de tiempo administrativo y una imagen más profesional.

---

## 8. Proceso de trabajo y cronograma

**Duración del desarrollo: 2 semanas.** **Garantía de cambios: 2 semanas** posteriores a la
entrega (ajustes y correcciones sin costo sobre lo acordado).

| # | Fase | Descripción |
|---|---|---|
| 1 | **Reunión inicial** | Levantamiento a fondo de **requerimientos y riesgos** con Halcones. |
| 2 | **Primera versión funcional** | Desarrollo/ajuste de la plataforma y despliegue de una versión para revisión. |
| 3 | **Pruebas del cliente** | Halcones prueba la plataforma en su operación real. |
| 4 | **Ajustes** | Se incorporan los cambios surgidos de las pruebas. |
| 5 | **Entrega final** | Versión final desplegada, capacitación y puesta en marcha. |

```
Semana 1        Semana 2            +2 semanas
─────────────   ─────────────────   ───────────────────
Reunión +       Pruebas cliente +   Garantía de cambios
1ª versión      ajustes + entrega   (ajustes sin costo)
```

### Condiciones
- **Forma de pago:** 50 % anticipo (antes de empezar) + 50 % contra entrega final (sección 4).
- **Garantía de cambios:** 2 semanas tras la entrega.
- **Capacitación:** una sesión de uso para el administrador y los instructores.
- **Propiedad:** al completar el pago, el código y los datos quedan a disposición de Halcones.

### No incluye (se cotiza aparte si se requiere)
- Integración con pasarela de pagos en línea o facturación electrónica (DIAN).
- App nativa en tiendas (Play Store / App Store) — la PWA ya permite “instalar” sin tiendas.
- Migración masiva de datos históricos desde otros sistemas.
- Producción de fotos/videos o contenido de marketing.

---

## 9. Puesta en marcha (despliegue)

La plataforma se publica en **Render** con una **URL pública** (y HTTPS gratuito). El código ya
está en GitHub; el despliegue se realiza con el *blueprint* incluido (`render.yaml`). Pasos:

1. Conectar el repositorio en Render (**New → Blueprint**) → crea el servicio web + base de datos.
2. Definir variables (URL pública y, si se desea, el correo SMTP).
3. (Opcional) Conectar un **dominio propio** de Halcones.
4. (Opcional) Activar el envío real de correos y el cron diario de notificaciones.

Guía técnica completa en `DEPLOY_RENDER.md`.

### Próximos pasos
1. Aprobación de la propuesta y pago del anticipo (50 %).
2. Reunión inicial de requerimientos y riesgos.
3. Desarrollo, pruebas, ajustes y entrega final (2 semanas).
4. Registro de dominio y cuentas de hosting/correo a nombre de Halcones.
5. (Opcional) Activación del plan de soporte mensual.

---

*Esta propuesta es una estimación comercial; los precios de terceros pueden variar según el
proveedor y la tasa de cambio. Vigencia de la oferta: 30 días.*
