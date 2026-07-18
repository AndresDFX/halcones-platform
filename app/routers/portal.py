"""Portal del estudiante: contenido de sus cursos, avance, pagos y saltos."""
from datetime import date

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_user
from ..models import (User, Role, Course, Enrollment, MediaType, LoadSlot, Load,
                      JumpDay)
from ..templating import render

router = APIRouter(prefix="/portal")


def _enrollment_or_403(db, user, course_id):
    enr = (db.query(Enrollment)
           .filter_by(student_id=user.id, course_id=course_id).first())
    if not enr:
        raise HTTPException(403, "No estás inscrito en este curso.")
    return enr


@router.get("/curso/{course_id}")
def course_content(course_id: int, request: Request, db: Session = Depends(get_db),
                   user: User = Depends(require_user)):
    curso = db.get(Course, course_id)
    if not curso:
        raise HTTPException(404, "Curso no encontrado")

    # Estudiante debe estar inscrito; staff puede ver siempre.
    enr = None
    if user.role == Role.estudiante:
        enr = _enrollment_or_403(db, user, course_id)

    videos = [m for m in curso.media if m.tipo == MediaType.video]
    manuales = [m for m in curso.media if m.tipo in (MediaType.manual, MediaType.documento)]
    return render(request, "portal/course_content.html", user=user, curso=curso,
                  videos=videos, manuales=manuales, enr=enr)


@router.get("/pagos")
def my_payments(request: Request, db: Session = Depends(get_db),
                user: User = Depends(require_user)):
    enrollments = db.query(Enrollment).filter_by(student_id=user.id).all()
    pagos = []
    for e in enrollments:
        pagos.extend(e.payments)
    pagos.sort(key=lambda p: (p.fecha or date.min), reverse=True)
    saldo_total = sum(e.saldo for e in enrollments if e.saldo > 0)
    return render(request, "portal/my_payments.html", user=user,
                  enrollments=enrollments, pagos=pagos, saldo_total=saldo_total)


@router.get("/saltos")
def my_jumps(request: Request, db: Session = Depends(get_db),
             user: User = Depends(require_user)):
    slots = (db.query(LoadSlot)
             .join(Load).join(JumpDay)
             .filter(LoadSlot.person_id == user.id)
             .order_by(JumpDay.fecha.desc()).all())
    return render(request, "portal/my_jumps.html", user=user, slots=slots,
                  hoy=date.today())


@router.get("/perfil")
def my_profile(request: Request, db: Session = Depends(get_db),
               user: User = Depends(require_user)):
    return render(request, "portal/profile.html", user=user)
