"""Vistas propias del instructor. Solo información que le concierne:
sus pagos (compensación) y sus asignaciones. Nunca las finanzas del negocio.
"""
from datetime import date

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_roles
from ..models import User, Role, InstructorPayment, LoadSlot, Load, JumpDay
from ..templating import render

router = APIRouter(prefix="/instructor")

instructor_required = require_roles(Role.instructor, Role.admin)


@router.get("/pagos")
def my_payments(request: Request, db: Session = Depends(get_db),
                user: User = Depends(instructor_required)):
    pagos = (db.query(InstructorPayment)
             .filter(InstructorPayment.instructor_id == user.id)
             .order_by(InstructorPayment.fecha.desc(), InstructorPayment.id.desc())
             .all())
    total = sum(float(p.monto) for p in pagos)

    # Resumen por concepto
    por_concepto: dict[str, float] = {}
    for p in pagos:
        por_concepto[p.concepto.value] = por_concepto.get(p.concepto.value, 0) + float(p.monto)

    return render(request, "instructor/my_payments.html", user=user,
                  pagos=pagos, total=total, por_concepto=por_concepto)
