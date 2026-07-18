"""Página inicial pública (comercial). Sin autenticación."""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Course
from ..templating import render

router = APIRouter()


@router.get("/", include_in_schema=False)
def landing(request: Request, db: Session = Depends(get_db)):
    cursos = (db.query(Course)
              .filter(Course.activo == True)  # noqa: E712
              .order_by(Course.destacado.desc(), Course.precio.desc()).all())
    user = get_current_user(request, db)   # para mostrar "Ir al panel" si ya inició sesión
    return render(request, "landing.html", user=user, cursos=cursos)
