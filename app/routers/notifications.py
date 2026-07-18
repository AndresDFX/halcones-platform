"""Notificaciones por correo, programables desde el panel del administrador."""
from fastapi import APIRouter, Depends, Form, Request, HTTPException, Query
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import admin_required
from ..config import settings
from ..models import (User, NotificationRule, NotificationLog, NotificationType,
                      NotificationStatus)
from ..templating import render
from .. import notifications as notif

router = APIRouter(prefix="/notificaciones")


DEFAULTS = {
    "recordatorio_salto": {
        "nombre": "Recordatorio de próximo salto",
        "asunto": "🪂 {nombre}, tu próximo salto es el {fecha_salto}",
        "cuerpo": ("Hola {nombre_completo},\n\n"
                   "Te recordamos que tienes programado tu salto ({tipo_salto}) "
                   "el {fecha_salto} a las {hora_salto}, en el vuelo {vuelo}.\n"
                   "Zona: {zona}.\n\n"
                   "Recuerda llegar con tiempo y con la teoría al día. ¡Nos vemos en el cielo!\n\n"
                   "Halcones Paracaidismo"),
        "dias_antelacion": 2, "intervalo_dias": 30,
    },
    "oferta_curso": {
        "nombre": "Oferta de curso a quienes saltaron una vez",
        "asunto": "🪂 {nombre}, ¿listo para volver a volar?",
        "cuerpo": ("Hola {nombre_completo},\n\n"
                   "¡Sabemos que probaste la caída libre con nosotros y sentimos que el "
                   "cielo te llama de nuevo! 🚀\n\n"
                   "Da el siguiente paso con nuestro {curso}: 7 niveles para lograr "
                   "autonomía de vuelo. Inversión: {precio} (reserva desde {reserva}).\n\n"
                   "Escríbenos y coordinamos tu inicio. ¡Te esperamos!\n\n"
                   "Halcones Paracaidismo"),
        "dias_antelacion": 2, "intervalo_dias": 30,
    },
}


@router.get("")
def list_rules(request: Request, db: Session = Depends(get_db),
               user: User = Depends(admin_required)):
    reglas = db.query(NotificationRule).order_by(NotificationRule.id).all()
    logs = (db.query(NotificationLog)
            .order_by(NotificationLog.id.desc()).limit(30).all())
    # Conteo por estado
    conteos = {}
    for est in NotificationStatus:
        conteos[est.value] = db.query(NotificationLog).filter(
            NotificationLog.estado == est).count()
    smtp_ok = notif.get_smtp_config(db)["configured"]
    return render(request, "notifications/list.html", user=user, reglas=reglas,
                  logs=logs, conteos=conteos, smtp_ok=smtp_ok)


@router.get("/config")
def smtp_config_form(request: Request, db: Session = Depends(get_db),
                     user: User = Depends(admin_required)):
    cfg = notif.get_smtp_config(db)
    return render(request, "notifications/config.html", user=user, cfg=cfg)


@router.post("/config")
def smtp_config_save(request: Request, db: Session = Depends(get_db),
                     user: User = Depends(admin_required),
                     smtp_host: str = Form(""), smtp_port: str = Form("587"),
                     smtp_user: str = Form(""), smtp_password: str = Form(""),
                     smtp_from: str = Form(""), smtp_tls: bool = Form(False)):
    data = {"smtp_host": smtp_host.strip(), "smtp_port": smtp_port or "587",
            "smtp_user": smtp_user.strip(), "smtp_from": smtp_from.strip(),
            "smtp_tls": "true" if smtp_tls else "false"}
    # No sobreescribir la contraseña si el campo se deja vacío
    if smtp_password:
        data["smtp_password"] = smtp_password
    notif.save_smtp_config(db, data)
    return RedirectResponse("/notificaciones/config", status_code=303)


@router.get("/nueva")
def new_rule_form(request: Request, db: Session = Depends(get_db),
                  user: User = Depends(admin_required), tipo: str = "recordatorio_salto"):
    if tipo not in DEFAULTS:
        tipo = "recordatorio_salto"
    return render(request, "notifications/form.html", user=user, regla=None,
                  tipo_sel=tipo, defaults=DEFAULTS)


@router.post("/nueva")
def create_rule(request: Request, db: Session = Depends(get_db),
                user: User = Depends(admin_required),
                nombre: str = Form(...), tipo: str = Form(...),
                asunto: str = Form(...), cuerpo: str = Form(...),
                dias_antelacion: int = Form(2), intervalo_dias: int = Form(30),
                frecuencia: str = Form("diaria"), activo: bool = Form(False)):
    regla = NotificationRule(
        nombre=nombre.strip(), tipo=NotificationType(tipo), asunto=asunto,
        cuerpo=cuerpo, dias_antelacion=dias_antelacion, intervalo_dias=intervalo_dias,
        frecuencia=frecuencia, activo=activo, creada_por_id=user.id,
    )
    db.add(regla)
    db.commit()
    return RedirectResponse("/notificaciones", status_code=303)


@router.get("/{rule_id}/editar")
def edit_rule_form(rule_id: int, request: Request, db: Session = Depends(get_db),
                   user: User = Depends(admin_required)):
    regla = db.get(NotificationRule, rule_id)
    if not regla:
        raise HTTPException(404, "Regla no encontrada")
    return render(request, "notifications/form.html", user=user, regla=regla,
                  tipo_sel=regla.tipo.value, defaults=DEFAULTS)


@router.post("/{rule_id}/editar")
def update_rule(rule_id: int, db: Session = Depends(get_db),
                user: User = Depends(admin_required),
                nombre: str = Form(...), tipo: str = Form(...),
                asunto: str = Form(...), cuerpo: str = Form(...),
                dias_antelacion: int = Form(2), intervalo_dias: int = Form(30),
                frecuencia: str = Form("diaria"), activo: bool = Form(False)):
    regla = db.get(NotificationRule, rule_id)
    if not regla:
        raise HTTPException(404, "Regla no encontrada")
    regla.nombre = nombre.strip(); regla.tipo = NotificationType(tipo)
    regla.asunto = asunto; regla.cuerpo = cuerpo
    regla.dias_antelacion = dias_antelacion; regla.intervalo_dias = intervalo_dias
    regla.frecuencia = frecuencia; regla.activo = activo
    db.commit()
    return RedirectResponse("/notificaciones", status_code=303)


@router.post("/{rule_id}/activar")
def toggle_rule(rule_id: int, db: Session = Depends(get_db),
                user: User = Depends(admin_required)):
    regla = db.get(NotificationRule, rule_id)
    if regla:
        regla.activo = not regla.activo
        db.commit()
    return RedirectResponse("/notificaciones", status_code=303)


@router.post("/{rule_id}/eliminar")
def delete_rule(rule_id: int, db: Session = Depends(get_db),
                user: User = Depends(admin_required)):
    regla = db.get(NotificationRule, rule_id)
    if regla:
        db.delete(regla)
        db.commit()
    return RedirectResponse("/notificaciones", status_code=303)


@router.get("/{rule_id}/previsualizar")
def preview(rule_id: int, request: Request, db: Session = Depends(get_db),
            user: User = Depends(admin_required)):
    regla = db.get(NotificationRule, rule_id)
    if not regla:
        raise HTTPException(404, "Regla no encontrada")
    destinatarios = notif.preview_rule(db, regla)
    smtp_ok = notif.get_smtp_config(db)["configured"]
    return render(request, "notifications/preview.html", user=user, regla=regla,
                  destinatarios=destinatarios, smtp_ok=smtp_ok)


@router.post("/{rule_id}/ejecutar")
def run_now(rule_id: int, db: Session = Depends(get_db),
            user: User = Depends(admin_required)):
    regla = db.get(NotificationRule, rule_id)
    if not regla:
        raise HTTPException(404, "Regla no encontrada")
    notif.run_rule(db, regla, actor_id=user.id)
    return RedirectResponse("/notificaciones", status_code=303)


@router.post("/ejecutar-todas")
def run_all(db: Session = Depends(get_db), user: User = Depends(admin_required)):
    notif.run_all_active(db)
    return RedirectResponse("/notificaciones", status_code=303)


@router.get("/cron", include_in_schema=False)
def cron_trigger(db: Session = Depends(get_db), token: str = Query("")):
    """Endpoint para disparar todas las reglas activas desde un Render Cron Job.

    Se protege con un token compartido (settings.cron_secret) en lugar de sesión.
    """
    if token != settings.cron_secret:
        raise HTTPException(status_code=403, detail="token inválido")
    resumen = notif.run_all_active(db)
    return JSONResponse(resumen)
