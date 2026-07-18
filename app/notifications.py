"""Servicio de notificaciones por correo.

- Si el SMTP no está configurado (settings.smtp_configured == False), las
  notificaciones se registran en modo "simulado": quedan en la bitácora de
  notificaciones pero no se envían. La funcionalidad queda lista para activarse
  con solo definir las variables SMTP_* en el entorno.
- El motor calcula destinatarios para cada tipo de regla y evita duplicados
  mediante una "clave" de deduplicación por destinatario y periodo/evento.
"""
import smtplib
from datetime import date, datetime, timedelta
from email.message import EmailMessage

from sqlalchemy.orm import Session

from .config import settings
from .models import (
    User, Role, Course, Enrollment, EnrollmentStatus, LoadSlot, Load, JumpDay,
    NotificationRule, NotificationLog, NotificationType, NotificationStatus, Setting,
)

SMTP_KEYS = ["smtp_host", "smtp_port", "smtp_user", "smtp_password", "smtp_from", "smtp_tls"]


def get_smtp_config(db: Session) -> dict:
    """Config SMTP efectiva: los valores guardados por el admin (tabla settings)
    tienen prioridad sobre las variables de entorno."""
    cfg = {
        "smtp_host": settings.smtp_host,
        "smtp_port": settings.smtp_port,
        "smtp_user": settings.smtp_user,
        "smtp_password": settings.smtp_password,
        "smtp_from": settings.smtp_from,
        "smtp_tls": settings.smtp_tls,
    }
    for row in db.query(Setting).filter(Setting.clave.in_(SMTP_KEYS)).all():
        if row.valor is None or row.valor == "":
            continue
        if row.clave == "smtp_port":
            try:
                cfg[row.clave] = int(row.valor)
            except ValueError:
                pass
        elif row.clave == "smtp_tls":
            cfg[row.clave] = row.valor.lower() in ("1", "true", "on", "yes", "sí", "si")
        else:
            cfg[row.clave] = row.valor
    cfg["configured"] = bool(cfg["smtp_host"] and cfg["smtp_user"])
    return cfg


def save_smtp_config(db: Session, data: dict):
    for k in SMTP_KEYS:
        if k not in data:
            continue
        row = db.get(Setting, k)
        val = str(data[k]) if data[k] is not None else ""
        if row:
            row.valor = val
        else:
            db.add(Setting(clave=k, valor=val))
    db.commit()

MESES = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def _fmt_fecha(d) -> str:
    if not d:
        return ""
    return f"{d.day} de {MESES[d.month]} de {d.year}"


def _fmt_cop(v) -> str:
    try:
        return "$ " + f"{int(round(float(v or 0))):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "$ 0"


def render_template(text: str, ctx: dict) -> str:
    """Reemplaza {placeholder} por su valor. Placeholders desconocidos se dejan."""
    out = text or ""
    for k, v in ctx.items():
        out = out.replace("{" + k + "}", str(v))
    return out


# --------------------------------------------------------------------------- #
#  Envío SMTP
# --------------------------------------------------------------------------- #
def send_email(to: str, subject: str, body: str, cfg: dict) -> tuple[NotificationStatus, str | None]:
    """Envía un correo con la config SMTP dada. Devuelve (estado, error).

    Si no hay SMTP configurado, devuelve estado 'simulado' sin error.
    """
    if not cfg.get("configured"):
        return NotificationStatus.simulado, None

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = cfg["smtp_from"]
        msg["To"] = to
        msg.set_content(body)
        html = "<html><body style='font-family:Arial,sans-serif;color:#26211b'>" \
               + body.replace("\n", "<br>") + "</body></html>"
        msg.add_alternative(html, subtype="html")

        with smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"], timeout=20) as s:
            if cfg["smtp_tls"]:
                s.starttls()
            if cfg["smtp_user"]:
                s.login(cfg["smtp_user"], cfg["smtp_password"])
            s.send_message(msg)
        return NotificationStatus.enviado, None
    except Exception as e:  # noqa: BLE001
        return NotificationStatus.error, str(e)[:300]


# --------------------------------------------------------------------------- #
#  Cálculo de destinatarios por tipo de regla
# --------------------------------------------------------------------------- #
def _aff_course(db: Session):
    return (db.query(Course).filter(Course.modalidad.ilike("AFF")).first()
            or db.query(Course).filter(Course.activo == True).first())  # noqa: E712


def recipients_recordatorio(db: Session, rule: NotificationRule) -> list[dict]:
    """Estudiantes con un salto programado dentro de los próximos N días."""
    hoy = date.today()
    limite = hoy + timedelta(days=rule.dias_antelacion or 2)
    slots = (db.query(LoadSlot).join(Load).join(JumpDay)
             .filter(LoadSlot.person_id.isnot(None),
                     JumpDay.fecha >= hoy, JumpDay.fecha <= limite)
             .all())
    out = []
    for s in slots:
        u = s.person
        if not u or u.role != Role.estudiante or not u.email:
            continue
        jd = s.load.jump_day
        ctx = {
            "nombre": u.nombre.split(" ")[0],
            "nombre_completo": u.nombre,
            "fecha_salto": _fmt_fecha(jd.fecha),
            "hora_salto": s.load.hora_estimada or "por confirmar",
            "vuelo": str(s.load.numero),
            "tipo_salto": s.tipo_salto or "tu salto",
            "zona": jd.zona,
        }
        out.append({
            "user": u, "ctx": ctx,
            "clave": f"recordatorio:{u.id}:{jd.fecha.isoformat()}",
        })
    return out


def recipients_oferta(db: Session, rule: NotificationRule) -> list[dict]:
    """Estudiantes que saltaron una sola vez y podrían volver / hacer el curso.

    Criterio: usuarios rol estudiante con exactamente 1 asignación de salto,
    cuyo (único) salto fue hace >= intervalo_dias, y que NO tienen una
    inscripción activa en AFF.
    """
    intervalo = rule.intervalo_dias or 30
    hoy = date.today()
    aff = _aff_course(db)
    estudiantes = (db.query(User)
                   .filter(User.role == Role.estudiante, User.activo == True).all())  # noqa: E712
    out = []
    for u in estudiantes:
        if not u.email:
            continue
        slots = db.query(LoadSlot).filter(LoadSlot.person_id == u.id).all()
        if len(slots) != 1:
            continue
        jd = slots[0].load.jump_day
        dias_desde = (hoy - jd.fecha).days
        if dias_desde < intervalo:
            continue
        # Excluir si ya tiene inscripción activa en AFF
        if aff:
            tiene_aff = (db.query(Enrollment)
                         .filter(Enrollment.student_id == u.id,
                                 Enrollment.course_id == aff.id,
                                 Enrollment.estado == EnrollmentStatus.activo)
                         .first())
            if tiene_aff:
                continue
        ctx = {
            "nombre": u.nombre.split(" ")[0],
            "nombre_completo": u.nombre,
            "curso": aff.nombre if aff else "Curso AFF",
            "precio": _fmt_cop(aff.precio) if aff else "",
            "reserva": _fmt_cop(aff.reserva_minima) if aff else "",
            "dias_desde": str(dias_desde),
        }
        out.append({
            "user": u, "ctx": ctx,
            "clave": f"oferta:{u.id}:{hoy.year}-{hoy.month:02d}",
        })
    return out


def compute_recipients(db: Session, rule: NotificationRule) -> list[dict]:
    if rule.tipo == NotificationType.recordatorio_salto:
        return recipients_recordatorio(db, rule)
    return recipients_oferta(db, rule)


def preview_rule(db: Session, rule: NotificationRule) -> list[dict]:
    """Previsualiza destinatarios (sin enviar): renderiza y marca duplicados."""
    result = []
    for r in compute_recipients(db, rule):
        ya = db.query(NotificationLog).filter(NotificationLog.clave == r["clave"]).first()
        result.append({
            "email": r["user"].email,
            "nombre": r["user"].nombre,
            "asunto": render_template(rule.asunto, r["ctx"]),
            "cuerpo": render_template(rule.cuerpo, r["ctx"]),
            "clave": r["clave"],
            "ya_enviado": ya is not None,
        })
    return result


def run_rule(db: Session, rule: NotificationRule, actor_id: int | None = None,
             cfg: dict | None = None) -> dict:
    """Genera y (intenta) enviar las notificaciones de una regla.

    Omite destinatarios cuya clave ya existe (evita duplicados).
    """
    if cfg is None:
        cfg = get_smtp_config(db)
    resumen = {"generados": 0, "enviados": 0, "simulados": 0, "errores": 0, "omitidos": 0}
    for r in compute_recipients(db, rule):
        existe = db.query(NotificationLog).filter(NotificationLog.clave == r["clave"]).first()
        if existe:
            resumen["omitidos"] += 1
            continue
        asunto = render_template(rule.asunto, r["ctx"])
        cuerpo = render_template(rule.cuerpo, r["ctx"])
        estado, error = send_email(r["user"].email, asunto, cuerpo, cfg)
        log = NotificationLog(
            rule_id=rule.id, tipo=rule.tipo, destinatario_id=r["user"].id,
            email=r["user"].email, asunto=asunto, cuerpo=cuerpo,
            estado=estado, error=error, clave=r["clave"],
            fecha_envio=datetime.utcnow() if estado in (
                NotificationStatus.enviado, NotificationStatus.simulado) else None,
        )
        db.add(log)
        resumen["generados"] += 1
        if estado == NotificationStatus.enviado:
            resumen["enviados"] += 1
        elif estado == NotificationStatus.simulado:
            resumen["simulados"] += 1
        elif estado == NotificationStatus.error:
            resumen["errores"] += 1
    rule.ultima_ejecucion = datetime.utcnow()
    db.commit()
    return resumen


def run_all_active(db: Session) -> dict:
    total = {"generados": 0, "enviados": 0, "simulados": 0, "errores": 0, "omitidos": 0,
             "reglas": 0}
    cfg = get_smtp_config(db)
    for rule in db.query(NotificationRule).filter(NotificationRule.activo == True).all():  # noqa: E712
        res = run_rule(db, rule, cfg=cfg)
        total["reglas"] += 1
        for k in ("generados", "enviados", "simulados", "errores", "omitidos"):
            total[k] += res[k]
    return total
