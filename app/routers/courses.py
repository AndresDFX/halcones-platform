"""Gestión de cursos, niveles y recursos multimedia."""
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, Form, Request, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_user, staff_required, admin_required
from ..models import User, Role, Course, CourseLevel, MediaResource, MediaType
from ..templating import render
from ..utils import save_upload

router = APIRouter(prefix="/cursos")


def _dec(value, default="0"):
    try:
        return Decimal(str(value).replace(".", "").replace(",", ".")) if value else Decimal(default)
    except (InvalidOperation, ValueError):
        return Decimal(default)


@router.get("")
def list_courses(request: Request, db: Session = Depends(get_db),
                 user: User = Depends(require_user)):
    cursos = db.query(Course).order_by(Course.destacado.desc(), Course.nombre).all()
    return render(request, "courses/list.html", user=user, cursos=cursos)


@router.get("/nuevo")
def new_course_form(request: Request, db: Session = Depends(get_db),
                    user: User = Depends(admin_required)):
    return render(request, "courses/form.html", user=user, curso=None)


@router.post("/nuevo")
def create_course(request: Request, db: Session = Depends(get_db),
                  user: User = Depends(admin_required),
                  codigo: str = Form(...), nombre: str = Form(...),
                  modalidad: str = Form(...), resumen: str = Form(""),
                  descripcion: str = Form(""), incluye: str = Form(""),
                  requisitos: str = Form(""), niveles_total: int = Form(7),
                  altura_salto_ft: int = Form(10000), duracion: str = Form(""),
                  precio: str = Form("0"), reserva_minima: str = Form("0"),
                  destacado: bool = Form(False)):
    curso = Course(
        codigo=codigo.strip(), nombre=nombre.strip(), modalidad=modalidad.strip(),
        resumen=resumen, descripcion=descripcion, incluye=incluye,
        requisitos=requisitos, niveles_total=niveles_total,
        altura_salto_ft=altura_salto_ft, duracion=duracion,
        precio=_dec(precio), reserva_minima=_dec(reserva_minima),
        destacado=destacado,
    )
    db.add(curso)
    db.commit()
    return RedirectResponse(f"/cursos/{curso.id}", status_code=303)


@router.get("/{course_id}")
def course_detail(course_id: int, request: Request, db: Session = Depends(get_db),
                  user: User = Depends(require_user)):
    curso = db.get(Course, course_id)
    if not curso:
        raise HTTPException(404, "Curso no encontrado")
    videos = [m for m in curso.media if m.tipo == MediaType.video]
    manuales = [m for m in curso.media if m.tipo in (MediaType.manual, MediaType.documento)]
    return render(request, "courses/detail.html", user=user, curso=curso,
                  videos=videos, manuales=manuales)


@router.get("/{course_id}/editar")
def edit_course_form(course_id: int, request: Request, db: Session = Depends(get_db),
                     user: User = Depends(admin_required)):
    curso = db.get(Course, course_id)
    if not curso:
        raise HTTPException(404, "Curso no encontrado")
    return render(request, "courses/form.html", user=user, curso=curso)


@router.post("/{course_id}/editar")
def update_course(course_id: int, request: Request, db: Session = Depends(get_db),
                  user: User = Depends(admin_required),
                  codigo: str = Form(...), nombre: str = Form(...),
                  modalidad: str = Form(...), resumen: str = Form(""),
                  descripcion: str = Form(""), incluye: str = Form(""),
                  requisitos: str = Form(""), niveles_total: int = Form(7),
                  altura_salto_ft: int = Form(10000), duracion: str = Form(""),
                  precio: str = Form("0"), reserva_minima: str = Form("0"),
                  activo: bool = Form(False), destacado: bool = Form(False)):
    curso = db.get(Course, course_id)
    if not curso:
        raise HTTPException(404, "Curso no encontrado")
    curso.codigo = codigo.strip(); curso.nombre = nombre.strip()
    curso.modalidad = modalidad.strip(); curso.resumen = resumen
    curso.descripcion = descripcion; curso.incluye = incluye
    curso.requisitos = requisitos; curso.niveles_total = niveles_total
    curso.altura_salto_ft = altura_salto_ft; curso.duracion = duracion
    curso.precio = _dec(precio); curso.reserva_minima = _dec(reserva_minima)
    curso.activo = activo; curso.destacado = destacado
    db.commit()
    return RedirectResponse(f"/cursos/{curso.id}", status_code=303)


# ---- Niveles ----
@router.post("/{course_id}/niveles")
def add_level(course_id: int, db: Session = Depends(get_db),
              user: User = Depends(admin_required),
              numero: int = Form(...), titulo: str = Form(...),
              descripcion: str = Form(""), es_teorico: bool = Form(False)):
    curso = db.get(Course, course_id)
    if not curso:
        raise HTTPException(404, "Curso no encontrado")
    db.add(CourseLevel(course_id=course_id, numero=numero, titulo=titulo.strip(),
                       descripcion=descripcion, es_teorico=es_teorico))
    db.commit()
    return RedirectResponse(f"/cursos/{course_id}", status_code=303)


# ---- Recursos multimedia (videos, manuales) ----
@router.get("/{course_id}/media/nuevo")
def new_media_form(course_id: int, request: Request, db: Session = Depends(get_db),
                   user: User = Depends(staff_required)):
    curso = db.get(Course, course_id)
    if not curso:
        raise HTTPException(404, "Curso no encontrado")
    return render(request, "courses/media_form.html", user=user, curso=curso)


@router.post("/{course_id}/media/nuevo")
async def create_media(course_id: int, request: Request, db: Session = Depends(get_db),
                       user: User = Depends(staff_required),
                       tipo: str = Form("video"), titulo: str = Form(...),
                       descripcion: str = Form(""), url: str = Form(""),
                       level_id: str = Form(""),
                       archivo: UploadFile | None = File(None)):
    curso = db.get(Course, course_id)
    if not curso:
        raise HTTPException(404, "Curso no encontrado")

    rel_path = None
    if archivo and archivo.filename:
        rel_path = save_upload(archivo, subdir=f"curso-{course_id}")

    media = MediaResource(
        course_id=course_id,
        tipo=MediaType(tipo),
        titulo=titulo.strip(),
        descripcion=descripcion,
        url=url.strip() or None,
        archivo=rel_path,
        level_id=int(level_id) if level_id else None,
        orden=len(curso.media),
    )
    db.add(media)
    db.commit()
    return RedirectResponse(f"/cursos/{course_id}", status_code=303)


@router.post("/{course_id}/media/{media_id}/eliminar")
def delete_media(course_id: int, media_id: int, db: Session = Depends(get_db),
                 user: User = Depends(staff_required)):
    media = db.get(MediaResource, media_id)
    if media:
        db.delete(media)
        db.commit()
    return RedirectResponse(f"/cursos/{course_id}", status_code=303)
