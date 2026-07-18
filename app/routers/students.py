"""Gestión de estudiantes: perfiles, inscripciones y bitácora de avance."""
from datetime import datetime, date
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import staff_required, admin_required
from ..models import (User, Role, Course, CourseLevel, Enrollment, EnrollmentStatus,
                      LevelProgress, LevelStatus)
from ..templating import render

router = APIRouter(prefix="/estudiantes")


def _dec(value, default="0"):
    try:
        return Decimal(str(value).replace(".", "").replace(",", ".")) if value else Decimal(default)
    except (InvalidOperation, ValueError):
        return Decimal(default)


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


@router.get("")
def list_students(request: Request, db: Session = Depends(get_db),
                  user: User = Depends(staff_required), q: str = ""):
    query = db.query(User).filter(User.role == Role.estudiante)
    if q:
        like = f"%{q}%"
        query = query.filter((User.nombre.ilike(like)) | (User.cedula.ilike(like))
                             | (User.email.ilike(like)))
    estudiantes = query.order_by(User.nombre).all()
    return render(request, "students/list.html", user=user,
                  estudiantes=estudiantes, q=q)


@router.get("/{student_id}")
def student_detail(student_id: int, request: Request, db: Session = Depends(get_db),
                   user: User = Depends(staff_required)):
    est = db.get(User, student_id)
    if not est or est.role != Role.estudiante:
        raise HTTPException(404, "Estudiante no encontrado")
    cursos = db.query(Course).filter(Course.activo == True).all()  # noqa: E712
    instructores = db.query(User).filter(User.role == Role.instructor,
                                         User.activo == True).all()  # noqa: E712
    return render(request, "students/detail.html", user=user, est=est,
                  cursos=cursos, instructores=instructores)


@router.post("/{student_id}/editar")
def update_student(student_id: int, db: Session = Depends(get_db),
                   user: User = Depends(admin_required),
                   nombre: str = Form(...), telefono: str = Form(""),
                   cedula: str = Form(""), peso_kg: str = Form(""),
                   fecha_nacimiento: str = Form(""), eps: str = Form(""),
                   direccion: str = Form(""),
                   contacto_emergencia_nombre: str = Form(""),
                   contacto_emergencia_telefono: str = Form(""),
                   activo: bool = Form(False)):
    est = db.get(User, student_id)
    if not est:
        raise HTTPException(404, "Estudiante no encontrado")
    est.nombre = nombre.strip(); est.telefono = telefono; est.cedula = cedula
    est.peso_kg = float(peso_kg) if peso_kg else None
    est.fecha_nacimiento = _parse_date(fecha_nacimiento)
    est.eps = eps; est.direccion = direccion
    est.contacto_emergencia_nombre = contacto_emergencia_nombre
    est.contacto_emergencia_telefono = contacto_emergencia_telefono
    est.activo = activo
    db.commit()
    return RedirectResponse(f"/estudiantes/{student_id}", status_code=303)


# ---- Inscripciones ----
@router.post("/{student_id}/inscribir")
def enroll(student_id: int, db: Session = Depends(get_db),
           user: User = Depends(admin_required),
           course_id: int = Form(...), instructor_id: str = Form(""),
           precio_acordado: str = Form(""), fecha_inscripcion: str = Form("")):
    est = db.get(User, student_id)
    curso = db.get(Course, course_id)
    if not est or not curso:
        raise HTTPException(404, "Estudiante o curso no encontrado")
    if db.query(Enrollment).filter_by(student_id=student_id, course_id=course_id).first():
        raise HTTPException(400, "El estudiante ya está inscrito en este curso.")

    precio = _dec(precio_acordado) if precio_acordado else curso.precio
    enr = Enrollment(
        student_id=student_id, course_id=course_id,
        instructor_id=int(instructor_id) if instructor_id else None,
        precio_acordado=precio,
        fecha_inscripcion=_parse_date(fecha_inscripcion) or date.today(),
    )
    db.add(enr)
    db.flush()
    # Crear bitácora con un registro por cada nivel/salto del curso
    for lvl in curso.levels:
        db.add(LevelProgress(enrollment_id=enr.id, level_id=lvl.id,
                             estado=LevelStatus.pendiente))
    db.commit()
    return RedirectResponse(f"/estudiantes/{student_id}", status_code=303)


# ---- Bitácora: actualizar avance de un nivel ----
@router.post("/progreso/{progress_id}")
def update_progress(progress_id: int, db: Session = Depends(get_db),
                    user: User = Depends(staff_required),
                    estado: str = Form(...), fecha: str = Form(""),
                    nota: str = Form(""), video_url: str = Form(""),
                    altura_ft: str = Form("")):
    prog = db.get(LevelProgress, progress_id)
    if not prog:
        raise HTTPException(404, "Registro no encontrado")
    prog.estado = LevelStatus(estado)
    prog.fecha = _parse_date(fecha)
    prog.nota = nota
    prog.video_url = video_url.strip() or None
    prog.altura_ft = int(altura_ft) if altura_ft else None
    prog.instructor_id = user.id
    # Actualizar nivel actual de la inscripción
    enr = prog.enrollment
    enr.nivel_actual = enr.niveles_aprobados
    if enr.course and enr.niveles_aprobados >= enr.course.niveles_total:
        enr.estado = EnrollmentStatus.completado
    db.commit()
    return RedirectResponse(f"/estudiantes/{prog.enrollment.student_id}", status_code=303)
