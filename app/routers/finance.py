"""Módulo financiero del NEGOCIO: pagos de estudiantes, cartera, ingresos y
nómina de instructores. Acceso exclusivo del administrador.

Regla de negocio: el instructor NO ve las finanzas de la escuela; solo consulta
sus propios pagos en /instructor/pagos.
"""
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import admin_required
from ..models import (User, Role, Enrollment, EnrollmentStatus, Payment, PaymentMethod,
                      PaymentConcept, InstructorPayment, InstructorPayConcept)
from ..templating import render

router = APIRouter(prefix="/finanzas")


def _dec(value, default="0"):
    try:
        return Decimal(str(value).replace(".", "").replace(",", ".")) if value else Decimal(default)
    except (InvalidOperation, ValueError):
        return Decimal(default)


def _parse_date(value):
    if not value:
        return date.today()
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return date.today()


@router.get("")
def finance_dashboard(request: Request, db: Session = Depends(get_db),
                      user: User = Depends(admin_required)):
    ingresos = db.query(func.coalesce(func.sum(Payment.monto), 0)).scalar() or 0

    enrollments = db.query(Enrollment).all()
    valor_cursos = sum(float(e.precio_acordado or 0) for e in enrollments)
    cartera = sum(e.saldo for e in enrollments
                  if e.estado in (EnrollmentStatus.activo, EnrollmentStatus.pausado)
                  and e.saldo > 0)

    pagos = db.query(Payment).order_by(Payment.fecha.desc(), Payment.id.desc()).all()

    # Egresos: nómina de instructores
    nomina = db.query(func.coalesce(func.sum(InstructorPayment.monto), 0)).scalar() or 0

    por_metodo: dict[str, float] = {}
    for p in pagos:
        por_metodo[p.metodo.value] = por_metodo.get(p.metodo.value, 0) + float(p.monto)

    deudores = sorted(
        [e for e in enrollments if e.saldo > 0 and e.estado != EnrollmentStatus.cancelado],
        key=lambda e: e.saldo, reverse=True)

    return render(request, "finance/dashboard.html", user=user,
                  ingresos=float(ingresos), valor_cursos=valor_cursos,
                  cartera=cartera, pagos=pagos[:40], por_metodo=por_metodo,
                  deudores=deudores, nomina=float(nomina))


# --------------------------- Pagos de estudiantes --------------------------- #
@router.get("/pago/nuevo")
def new_payment_form(request: Request, db: Session = Depends(get_db),
                     user: User = Depends(admin_required),
                     enrollment_id: str = ""):
    enrollments = (db.query(Enrollment)
                   .filter(Enrollment.estado != EnrollmentStatus.cancelado).all())
    seleccionada = None
    if enrollment_id:
        seleccionada = db.get(Enrollment, int(enrollment_id))
    return render(request, "finance/payment_form.html", user=user,
                  enrollments=enrollments, seleccionada=seleccionada)


@router.post("/pago/nuevo")
def create_payment(request: Request, db: Session = Depends(get_db),
                   user: User = Depends(admin_required),
                   enrollment_id: int = Form(...), monto: str = Form(...),
                   metodo: str = Form("transferencia"), concepto: str = Form("abono"),
                   fecha: str = Form(""), referencia: str = Form(""),
                   nota: str = Form("")):
    enr = db.get(Enrollment, enrollment_id)
    if not enr:
        raise HTTPException(404, "Inscripción no encontrada")
    pago = Payment(
        enrollment_id=enrollment_id, monto=_dec(monto),
        metodo=PaymentMethod(metodo), concepto=PaymentConcept(concepto),
        fecha=_parse_date(fecha), referencia=referencia, nota=nota,
        registrado_por_id=user.id,
    )
    db.add(pago)
    db.commit()
    return RedirectResponse("/finanzas", status_code=303)


# ----------------------- Nómina / pagos a instructores ---------------------- #
@router.get("/instructores")
def instructor_payroll(request: Request, db: Session = Depends(get_db),
                       user: User = Depends(admin_required),
                       instructor_id: str = ""):
    instructores = (db.query(User).filter(User.role == Role.instructor)
                    .order_by(User.nombre).all())
    pagos = db.query(InstructorPayment).order_by(
        InstructorPayment.fecha.desc(), InstructorPayment.id.desc()).all()

    # Total pagado por instructor
    totales: dict[int, float] = {}
    for p in pagos:
        totales[p.instructor_id] = totales.get(p.instructor_id, 0) + float(p.monto)

    seleccionado = int(instructor_id) if instructor_id else None
    total_nomina = sum(float(p.monto) for p in pagos)

    return render(request, "finance/instructors.html", user=user,
                  instructores=instructores, pagos=pagos[:60], totales=totales,
                  seleccionado=seleccionado, total_nomina=total_nomina)


@router.post("/instructores/pago")
def create_instructor_payment(request: Request, db: Session = Depends(get_db),
                              user: User = Depends(admin_required),
                              instructor_id: int = Form(...), monto: str = Form(...),
                              concepto: str = Form("por_salto"),
                              metodo: str = Form("transferencia"),
                              fecha: str = Form(""), saltos: str = Form(""),
                              referencia: str = Form(""), nota: str = Form("")):
    instr = db.get(User, instructor_id)
    if not instr or instr.role != Role.instructor:
        raise HTTPException(404, "Instructor no encontrado")
    pago = InstructorPayment(
        instructor_id=instructor_id, monto=_dec(monto),
        concepto=InstructorPayConcept(concepto), metodo=PaymentMethod(metodo),
        fecha=_parse_date(fecha), saltos=int(saltos) if saltos else None,
        referencia=referencia, nota=nota, registrado_por_id=user.id,
    )
    db.add(pago)
    db.commit()
    return RedirectResponse("/finanzas/instructores", status_code=303)
