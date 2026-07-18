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

> **El precio es menor que el valor de un curso AFF: una sola venta adicional cubre la
> plataforma.** El retorno llega con el primer estudiante extra que ayude a captar o retener.

---

## 2. Funcionalidades de la plataforma (ya construidas y funcionando)

### 🌐 Página web comercial (pública)
- Página de inicio atractiva que presenta la escuela a nuevos clientes.
- Muestra los cursos disponibles con precios e información, tomados de la plataforma.
- Botones directos de **WhatsApp** para reservar/consultar y de **Iniciar sesión**.
- Sección de experiencia, zona de salto y datos de contacto.

### 🪂 Gestión de cursos
- Catálogo de cursos (AFF de 7 niveles, Tándem y los que se agreguen).
- Temario por niveles, precio, reserva mínima, requisitos y "qué incluye".
- **Contenido multimedia por curso**: cargar el **manual en PDF**, subir videos o
  enlazar videos de **YouTube** (se ven dentro de la plataforma).
- Crear y editar cursos y su contenido desde el panel.

### 🎓 Seguimiento de estudiantes
- Ficha completa: datos personales, cédula, peso, EPS, dirección y **contacto de emergencia**.
- Inscripción de estudiantes a uno o varios cursos, con instructor asignado.
- **Bitácora de saltos**: estado y avance nivel por nivel (aprobado / en progreso / pendiente),
  con fecha, altura, nota del instructor y enlace al video de cada salto.
- Barra de avance del curso por estudiante.

### 💳 Finanzas
- Registro de **pagos de estudiantes** (reserva, abono, saldo) por transferencia, consignación,
  efectivo o link de pago.
- **Cartera por cobrar**: saldos pendientes por estudiante y foco de cobranza.
- Panel con **ingresos** totales, por método de pago y por mes.
- **Nómina de instructores**: pagos a instructores por salto, salario o bono (separado de las
  finanzas de estudiantes).

### 📋 Programación de saltos (manifiesto)
- Jornadas de salto por día, con zona y estado.
- **Vuelos por avión** (loads), con hora, altura y estado.
- Asignación de **quién va en cada vuelo** (alumno, instructor, tándem, cámara) y control de cupos.
- Gestión de la **flota de aviones** (matrícula, modelo, capacidad).

### ✉️ Notificaciones por correo (programables por el administrador)
- **Recordatorio del próximo salto** a los estudiantes (N días antes).
- **Oferta de curso** a quienes saltaron una sola vez, para reactivarlos.
- Plantillas de correo editables con variables (nombre, fecha, curso…), previsualización de
  destinatarios y bitácora de envíos. Configuración de correo (SMTP) desde el mismo panel.

### 👥 Roles, seguridad y portal
- Tres roles: **Administrador**, **Instructor** y **Estudiante**, cada uno con su vista.
- El instructor ve su operación (estudiantes, bitácora, manifiesto) y **sus propios pagos**,
  sin ver las finanzas del negocio.
- **Sin registro público**: el administrador crea las cuentas y entrega las credenciales.
- **Portal del estudiante**: ve su curso, videos, manual, avance, pagos y próximos saltos.

### 📱 App instalable (PWA) e identidad de marca
- Se instala en el celular o el computador como una app, con ícono de Halcones.
- Diseño con el **logo y los colores oficiales** (vino, rojo, negro) en toda la interfaz.
- Publicada en internet con **URL propia y HTTPS** (candado de seguridad).

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
| **Precio total (llave en mano)** | **$6.000.000 COP** — menos que un curso AFF |

**Forma de pago (50 / 50):**

| Momento | Porcentaje | Valor |
|---|---|---|
| **Anticipo** — antes de empezar | 50 % | **$3.000.000 COP** |
| **Saldo** — al finalizar el desarrollo (entrega) | 50 % | **$3.000.000 COP** |

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
| Precio de la plataforma (única vez) | $6.000.000 |
| Operación anual estimada (hosting + dominio + correo) | ~$700.000 – $1.000.000 |
| **Valor de UN curso AFF** | **$6.333.333** |

**El precio ($6.000.000) es menor que el valor de un curso AFF ($6.333.333):** una sola venta
adicional cubre el desarrollo de la plataforma, y su operación anual (~$1.000.000) equivale a
una fracción de otro curso. Si —gracias a los recordatorios y a la reactivación de quienes
saltaron una vez— ayuda a **cerrar uno o dos estudiantes AFF adicionales al año**, la inversión
y su operación quedan cubiertas con holgura. Todo estudiante adicional a partir de ahí es
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

## 10. Contacto

**Julián Castaño**
📱 WhatsApp: **+57 318 846 8892**

Con gusto resuelvo cualquier duda y coordinamos la reunión inicial.

---

*Esta propuesta es una estimación comercial; los precios de terceros pueden variar según el
proveedor y la tasa de cambio. Vigencia de la oferta: 30 días.*
