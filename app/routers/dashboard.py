"""Panel principal, adaptado según el rol del usuario."""
from datetime import date

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_user
from ..models import (User, Role, Course, Enrollment, EnrollmentStatus, Payment,
                      JumpDay, Load, LoadSlot, InstructorPayment)
from ..templating import render

router = APIRouter()


@router.get("/")
def dashboard(request: Request, db: Session = Depends(get_db),
              user: User = Depends(require_user)):
    if user.role == Role.estudiante:
        return _student_dashboard(request, db, user)
    if user.role == Role.instructor:
        return _instructor_dashboard(request, db, user)
    return _admin_dashboard(request, db, user)


# --------------------------------------------------------------------------- #
def _admin_dashboard(request, db, user):
    total_estudiantes = db.query(User).filter(User.role == Role.estudiante,
                                              User.activo == True).count()  # noqa: E712
    inscripciones_activas = db.query(Enrollment).filter(
        Enrollment.estado == EnrollmentStatus.activo).count()
    total_cursos = db.query(Course).filter(Course.activo == True).count()  # noqa: E712

    ingresos = db.query(func.coalesce(func.sum(Payment.monto), 0)).scalar() or 0

    activos = db.query(Enrollment).filter(
        Enrollment.estado.in_([EnrollmentStatus.activo, EnrollmentStatus.pausado])).all()
    cartera = sum(e.saldo for e in activos if e.saldo > 0)

    proximas_jornadas = (db.query(JumpDay)
                         .filter(JumpDay.fecha >= date.today())
                         .order_by(JumpDay.fecha).limit(5).all())

    ultimos_pagos = db.query(Payment).order_by(Payment.id.desc()).limit(6).all()

    por_cobrar = sorted([e for e in activos if e.saldo > 0],
                        key=lambda e: e.saldo, reverse=True)[:5]

    pagos = db.query(Payment).all()
    ingresos_mes: dict[str, float] = {}
    for p in pagos:
        if p.fecha:
            k = f"{p.fecha.year}-{p.fecha.month:02d}"
            ingresos_mes[k] = ingresos_mes.get(k, 0) + float(p.monto)
    serie = sorted(ingresos_mes.items())[-6:]

    return render(request, "dashboard_admin.html", user=user,
                  total_estudiantes=total_estudiantes,
                  inscripciones_activas=inscripciones_activas,
                  total_cursos=total_cursos,
                  ingresos=float(ingresos),
                  cartera=cartera,
                  proximas_jornadas=proximas_jornadas,
                  ultimos_pagos=ultimos_pagos,
                  por_cobrar=por_cobrar,
                  serie=serie)


# --------------------------------------------------------------------------- #
def _instructor_dashboard(request, db, user):
    """Panel operativo del instructor. Sin finanzas del negocio: solo lo suyo."""
    mis_estudiantes = (db.query(Enrollment)
                       .filter(Enrollment.instructor_id == user.id,
                               Enrollment.estado == EnrollmentStatus.activo).all())

    proximas_jornadas = (db.query(JumpDay)
                         .filter(JumpDay.fecha >= date.today())
                         .order_by(JumpDay.fecha).limit(5).all())

    # Mis asignaciones próximas (donde el instructor está en un vuelo)
    mis_slots = (db.query(LoadSlot)
                 .join(Load).join(JumpDay)
                 .filter(LoadSlot.person_id == user.id,
                         JumpDay.fecha >= date.today())
                 .order_by(JumpDay.fecha).all())

    # Mi compensación (solo mis pagos)
    mis_pagos = (db.query(InstructorPayment)
                 .filter(InstructorPayment.instructor_id == user.id)
                 .order_by(InstructorPayment.fecha.desc()).all())
    total_compensacion = sum(float(p.monto) for p in mis_pagos)

    return render(request, "dashboard_instructor.html", user=user,
                  mis_estudiantes=mis_estudiantes,
                  proximas_jornadas=proximas_jornadas,
                  mis_slots=mis_slots,
                  ultimos_pagos=mis_pagos[:5],
                  total_compensacion=total_compensacion)


# --------------------------------------------------------------------------- #
def _student_dashboard(request, db, user):
    enrollments = (db.query(Enrollment)
                   .filter(Enrollment.student_id == user.id).all())

    slots = (db.query(LoadSlot)
             .join(Load).join(JumpDay)
             .filter(LoadSlot.person_id == user.id,
                     JumpDay.fecha >= date.today())
             .order_by(JumpDay.fecha).all())

    saldo_total = sum(e.saldo for e in enrollments if e.saldo > 0)

    return render(request, "dashboard_student.html", user=user,
                  enrollments=enrollments,
                  proximos_saltos=slots,
                  saldo_total=saldo_total)
