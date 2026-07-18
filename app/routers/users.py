"""Gestión de usuarios (solo administrador).

No hay registro público: el administrador crea las cuentas de estudiantes,
instructores y administradores, y entrega las credenciales. CRUD completo.
"""
from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import admin_required
from ..models import User, Role, Enrollment
from ..security import hash_password
from ..templating import render

router = APIRouter(prefix="/usuarios")

ROLES = ["estudiante", "instructor", "admin"]


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


@router.get("")
def list_users(request: Request, db: Session = Depends(get_db),
               user: User = Depends(admin_required), rol: str = "", q: str = ""):
    query = db.query(User)
    if rol in ROLES:
        query = query.filter(User.role == Role(rol))
    if q:
        like = f"%{q}%"
        query = query.filter((User.nombre.ilike(like)) | (User.email.ilike(like))
                             | (User.cedula.ilike(like)))
    usuarios = query.order_by(User.role, User.nombre).all()
    conteos = {r: db.query(User).filter(User.role == Role(r)).count() for r in ROLES}
    return render(request, "users/list.html", user=user, usuarios=usuarios,
                  rol=rol, q=q, conteos=conteos)


@router.get("/nuevo")
def new_user_form(request: Request, db: Session = Depends(get_db),
                  user: User = Depends(admin_required), rol: str = "estudiante"):
    if rol not in ROLES:
        rol = "estudiante"
    return render(request, "users/form.html", user=user, u=None, rol_sel=rol)


@router.post("/nuevo")
def create_user(request: Request, db: Session = Depends(get_db),
                user: User = Depends(admin_required),
                nombre: str = Form(...), email: str = Form(...),
                role: str = Form("estudiante"), password: str = Form("halcones123"),
                telefono: str = Form(""), cedula: str = Form(""),
                # estudiante
                peso_kg: str = Form(""), fecha_nacimiento: str = Form(""),
                eps: str = Form(""), direccion: str = Form(""),
                contacto_emergencia_nombre: str = Form(""),
                contacto_emergencia_telefono: str = Form(""),
                # instructor
                licencia: str = Form(""), especialidad: str = Form("")):
    email = email.strip().lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(400, "Ya existe un usuario con ese correo.")
    if role not in ROLES:
        raise HTTPException(400, "Rol inválido.")

    u = User(
        nombre=nombre.strip(), email=email, role=Role(role),
        password_hash=hash_password(password or "halcones123"),
        telefono=telefono, cedula=cedula, activo=True,
    )
    if role == "estudiante":
        u.peso_kg = float(peso_kg) if peso_kg else None
        u.fecha_nacimiento = _parse_date(fecha_nacimiento)
        u.eps = eps; u.direccion = direccion
        u.contacto_emergencia_nombre = contacto_emergencia_nombre
        u.contacto_emergencia_telefono = contacto_emergencia_telefono
    if role == "instructor":
        u.licencia = licencia; u.especialidad = especialidad
    db.add(u)
    db.commit()

    if u.role == Role.estudiante:
        return RedirectResponse(f"/estudiantes/{u.id}", status_code=303)
    return RedirectResponse("/usuarios", status_code=303)


@router.get("/{user_id}/editar")
def edit_user_form(user_id: int, request: Request, db: Session = Depends(get_db),
                   user: User = Depends(admin_required)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(404, "Usuario no encontrado")
    return render(request, "users/form.html", user=user, u=u, rol_sel=u.role.value)


@router.post("/{user_id}/editar")
def update_user(user_id: int, db: Session = Depends(get_db),
                user: User = Depends(admin_required),
                nombre: str = Form(...), email: str = Form(...),
                role: str = Form("estudiante"), telefono: str = Form(""),
                cedula: str = Form(""), activo: bool = Form(False),
                peso_kg: str = Form(""), fecha_nacimiento: str = Form(""),
                eps: str = Form(""), direccion: str = Form(""),
                contacto_emergencia_nombre: str = Form(""),
                contacto_emergencia_telefono: str = Form(""),
                licencia: str = Form(""), especialidad: str = Form("")):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(404, "Usuario no encontrado")
    email = email.strip().lower()
    otro = db.query(User).filter(User.email == email, User.id != user_id).first()
    if otro:
        raise HTTPException(400, "Ese correo ya está en uso por otro usuario.")
    # Evitar que el admin se quite a sí mismo el rol/estado y quede sin acceso
    if u.id == user.id and (role != "admin" or not activo):
        raise HTTPException(400, "No puedes cambiar tu propio rol o desactivarte.")

    u.nombre = nombre.strip(); u.email = email; u.role = Role(role)
    u.telefono = telefono; u.cedula = cedula; u.activo = activo
    u.peso_kg = float(peso_kg) if peso_kg else None
    u.fecha_nacimiento = _parse_date(fecha_nacimiento)
    u.eps = eps; u.direccion = direccion
    u.contacto_emergencia_nombre = contacto_emergencia_nombre
    u.contacto_emergencia_telefono = contacto_emergencia_telefono
    u.licencia = licencia; u.especialidad = especialidad
    db.commit()
    return RedirectResponse("/usuarios", status_code=303)


@router.post("/{user_id}/password")
def reset_password(user_id: int, db: Session = Depends(get_db),
                   user: User = Depends(admin_required),
                   password: str = Form(...)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(404, "Usuario no encontrado")
    u.password_hash = hash_password(password or "halcones123")
    db.commit()
    return RedirectResponse("/usuarios", status_code=303)


@router.post("/{user_id}/estado")
def toggle_active(user_id: int, db: Session = Depends(get_db),
                  user: User = Depends(admin_required)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(404, "Usuario no encontrado")
    if u.id == user.id:
        raise HTTPException(400, "No puedes desactivar tu propia cuenta.")
    u.activo = not u.activo
    db.commit()
    return RedirectResponse("/usuarios", status_code=303)


@router.post("/{user_id}/eliminar")
def delete_user(user_id: int, db: Session = Depends(get_db),
                user: User = Depends(admin_required)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(404, "Usuario no encontrado")
    if u.id == user.id:
        raise HTTPException(400, "No puedes eliminar tu propia cuenta.")
    # Si tiene inscripciones asociadas, mejor desactivar que borrar (integridad)
    tiene_datos = db.query(Enrollment).filter(
        (Enrollment.student_id == user_id) | (Enrollment.instructor_id == user_id)
    ).first()
    if tiene_datos:
        u.activo = False
        db.commit()
        raise HTTPException(400, "El usuario tiene registros asociados; se desactivó "
                                 "en lugar de eliminarse para conservar el historial.")
    db.delete(u)
    db.commit()
    return RedirectResponse("/usuarios", status_code=303)
