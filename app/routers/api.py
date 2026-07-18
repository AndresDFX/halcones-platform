"""API REST JSON (documentada en /api/docs) para integraciones y extensibilidad."""
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_user, admin_required
from ..models import (Course, User, Role, Enrollment, EnrollmentStatus, Payment,
                      JumpDay, Load, LoadSlot)

router = APIRouter(prefix="/api", tags=["API"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/cursos", summary="Listado de cursos activos (requiere sesión)")
def api_courses(db: Session = Depends(get_db), user: User = Depends(require_user)):
    cursos = db.query(Course).filter(Course.activo == True).all()  # noqa: E712
    return [
        {
            "id": c.id, "codigo": c.codigo, "nombre": c.nombre,
            "modalidad": c.modalidad, "resumen": c.resumen,
            "niveles_total": c.niveles_total, "altura_salto_ft": c.altura_salto_ft,
            "precio": float(c.precio or 0), "moneda": c.moneda,
            "incluye": c.incluye_lista,
        }
        for c in cursos
    ]


@router.get("/cursos/{course_id}", summary="Detalle de un curso con su temario")
def api_course(course_id: int, db: Session = Depends(get_db),
               user: User = Depends(require_user)):
    c = db.get(Course, course_id)
    if not c:
        return {"error": "no encontrado"}
    return {
        "id": c.id, "codigo": c.codigo, "nombre": c.nombre,
        "modalidad": c.modalidad, "descripcion": c.descripcion,
        "precio": float(c.precio or 0), "reserva_minima": float(c.reserva_minima or 0),
        "incluye": c.incluye_lista, "requisitos": c.requisitos_lista,
        "niveles": [
            {"numero": l.numero, "titulo": l.titulo, "es_teorico": l.es_teorico,
             "descripcion": l.descripcion}
            for l in c.levels
        ],
        "videos": [{"titulo": m.titulo, "url": m.url}
                   for m in c.media if m.tipo.value == "video"],
    }


@router.get("/estadisticas", summary="Métricas del negocio (solo administrador)")
def api_stats(db: Session = Depends(get_db), user: User = Depends(admin_required)):
    ingresos = db.query(func.coalesce(func.sum(Payment.monto), 0)).scalar() or 0
    activos = db.query(Enrollment).filter(
        Enrollment.estado == EnrollmentStatus.activo).all()
    return {
        "estudiantes": db.query(User).filter(User.role == Role.estudiante).count(),
        "instructores": db.query(User).filter(User.role == Role.instructor).count(),
        "cursos_activos": db.query(Course).filter(Course.activo == True).count(),  # noqa: E712
        "inscripciones_activas": len(activos),
        "ingresos_totales": float(ingresos),
        "cartera_pendiente": sum(e.saldo for e in activos if e.saldo > 0),
    }


@router.get("/manifiesto/proximo", summary="Próxima jornada de saltos programada")
def api_next_manifest(db: Session = Depends(get_db), user: User = Depends(require_user)):
    jd = (db.query(JumpDay).filter(JumpDay.fecha >= date.today())
          .order_by(JumpDay.fecha).first())
    if not jd:
        return {"jornada": None}
    return {
        "jornada": {
            "fecha": jd.fecha.isoformat(), "zona": jd.zona,
            "vuelos": [
                {
                    "numero": l.numero, "hora": l.hora_estimada,
                    "avion": l.aircraft.matricula if l.aircraft else None,
                    "altura_ft": l.altura_ft, "estado": l.estado.value,
                    "asignados": [
                        {"nombre": s.display_nombre, "rol": s.rol.value,
                         "tipo_salto": s.tipo_salto}
                        for s in l.slots
                    ],
                }
                for l in jd.loads
            ],
        }
    }
