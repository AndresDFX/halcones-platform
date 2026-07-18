"""Manifiesto: programación de jornadas, vuelos (loads) y asignación de personas."""
from datetime import datetime, date

from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import staff_required, admin_required
from ..models import (User, Role, Aircraft, JumpDay, Load, LoadStatus, LoadSlot,
                      SlotRole)
from ..templating import render

router = APIRouter(prefix="/manifiesto")


def _parse_date(value):
    if not value:
        return date.today()
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return date.today()


@router.get("")
def list_days(request: Request, db: Session = Depends(get_db),
              user: User = Depends(staff_required)):
    jornadas = db.query(JumpDay).order_by(JumpDay.fecha.desc()).all()
    return render(request, "manifest/list.html", user=user, jornadas=jornadas)


@router.post("/jornada/nueva")
def create_day(db: Session = Depends(get_db), user: User = Depends(staff_required),
               fecha: str = Form(...), zona: str = Form(""), notas: str = Form(""),
               clima: str = Form("")):
    jd = JumpDay(fecha=_parse_date(fecha),
                 zona=zona or "Braaap Park · Vía Rozo–Cali",
                 notas=notas, clima=clima)
    db.add(jd)
    db.commit()
    return RedirectResponse(f"/manifiesto/{jd.id}", status_code=303)


@router.get("/aviones")
def aircraft_list(request: Request, db: Session = Depends(get_db),
                  user: User = Depends(staff_required)):
    aviones = db.query(Aircraft).order_by(Aircraft.matricula).all()
    return render(request, "manifest/aircraft.html", user=user, aviones=aviones)


@router.post("/aviones/nuevo")
def create_aircraft(db: Session = Depends(get_db), user: User = Depends(admin_required),
                    matricula: str = Form(...), modelo: str = Form(...),
                    capacidad: int = Form(4), notas: str = Form("")):
    if db.query(Aircraft).filter_by(matricula=matricula.strip()).first():
        raise HTTPException(400, "Ya existe un avión con esa matrícula.")
    db.add(Aircraft(matricula=matricula.strip().upper(), modelo=modelo.strip(),
                    capacidad=capacidad, notas=notas))
    db.commit()
    return RedirectResponse("/manifiesto/aviones", status_code=303)


@router.get("/{day_id}")
def day_detail(day_id: int, request: Request, db: Session = Depends(get_db),
               user: User = Depends(staff_required)):
    jd = db.get(JumpDay, day_id)
    if not jd:
        raise HTTPException(404, "Jornada no encontrada")
    aviones = db.query(Aircraft).filter(Aircraft.activo == True).all()  # noqa: E712
    estudiantes = db.query(User).filter(User.role == Role.estudiante,
                                        User.activo == True).order_by(User.nombre).all()  # noqa: E712
    instructores = db.query(User).filter(User.role == Role.instructor,
                                         User.activo == True).order_by(User.nombre).all()  # noqa: E712
    return render(request, "manifest/day.html", user=user, jd=jd, aviones=aviones,
                  estudiantes=estudiantes, instructores=instructores,
                  personas=estudiantes + instructores)


@router.post("/{day_id}/load/nuevo")
def create_load(day_id: int, db: Session = Depends(get_db),
                user: User = Depends(staff_required),
                aircraft_id: str = Form(""), hora_estimada: str = Form(""),
                altura_ft: int = Form(10000)):
    jd = db.get(JumpDay, day_id)
    if not jd:
        raise HTTPException(404, "Jornada no encontrada")
    numero = len(jd.loads) + 1
    load = Load(jump_day_id=day_id,
                aircraft_id=int(aircraft_id) if aircraft_id else None,
                numero=numero, hora_estimada=hora_estimada, altura_ft=altura_ft)
    db.add(load)
    db.commit()
    return RedirectResponse(f"/manifiesto/{day_id}", status_code=303)


@router.post("/load/{load_id}/estado")
def update_load_status(load_id: int, db: Session = Depends(get_db),
                       user: User = Depends(staff_required),
                       estado: str = Form(...)):
    load = db.get(Load, load_id)
    if not load:
        raise HTTPException(404, "Vuelo no encontrado")
    load.estado = LoadStatus(estado)
    db.commit()
    return RedirectResponse(f"/manifiesto/{load.jump_day_id}", status_code=303)


@router.post("/load/{load_id}/eliminar")
def delete_load(load_id: int, db: Session = Depends(get_db),
                user: User = Depends(staff_required)):
    load = db.get(Load, load_id)
    if load:
        day_id = load.jump_day_id
        db.delete(load)
        db.commit()
        return RedirectResponse(f"/manifiesto/{day_id}", status_code=303)
    return RedirectResponse("/manifiesto", status_code=303)


@router.post("/load/{load_id}/asignar")
def assign_slot(load_id: int, db: Session = Depends(get_db),
                user: User = Depends(staff_required),
                person_id: str = Form(""), person_nombre: str = Form(""),
                rol: str = Form("alumno"), tipo_salto: str = Form(""),
                notas: str = Form("")):
    load = db.get(Load, load_id)
    if not load:
        raise HTTPException(404, "Vuelo no encontrado")
    if load.aircraft and load.ocupados >= load.capacidad:
        raise HTTPException(400, "El vuelo ya está completo.")
    slot = LoadSlot(
        load_id=load_id,
        person_id=int(person_id) if person_id else None,
        person_nombre=person_nombre or None,
        rol=SlotRole(rol), tipo_salto=tipo_salto, notas=notas,
    )
    db.add(slot)
    db.commit()
    return RedirectResponse(f"/manifiesto/{load.jump_day_id}", status_code=303)


@router.post("/slot/{slot_id}/eliminar")
def remove_slot(slot_id: int, db: Session = Depends(get_db),
                user: User = Depends(staff_required)):
    slot = db.get(LoadSlot, slot_id)
    if slot:
        day_id = slot.load.jump_day_id
        db.delete(slot)
        db.commit()
        return RedirectResponse(f"/manifiesto/{day_id}", status_code=303)
    return RedirectResponse("/manifiesto", status_code=303)
