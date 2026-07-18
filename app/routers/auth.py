"""Autenticación: login y logout."""
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import User
from ..security import (create_access_token, verify_password, COOKIE_NAME)
from ..config import settings
from ..templating import render

router = APIRouter()


@router.get("/login")
def login_form(request: Request, db: Session = Depends(get_db), next: str = "/panel"):
    user = get_current_user(request, db)
    if user:
        return RedirectResponse("/panel", status_code=303)
    return render(request, "login.html", error=None, next=next)


@router.post("/login")
def login_submit(
    request: Request,
    db: Session = Depends(get_db),
    email: str = Form(...),
    password: str = Form(...),
    next: str = Form("/panel"),
):
    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if not user or not verify_password(password, user.password_hash):
        return render(request, "login.html",
                      error="Correo o contraseña incorrectos.", next=next)
    if not user.activo:
        return render(request, "login.html",
                      error="Tu cuenta está desactivada. Contacta al administrador.",
                      next=next)
    token = create_access_token(user.id, user.role.value)
    resp = RedirectResponse(next or "/panel", status_code=303)
    resp.set_cookie(
        COOKIE_NAME, token, httponly=True, samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
    )
    return resp


@router.get("/logout")
def logout():
    resp = RedirectResponse("/login", status_code=303)
    resp.delete_cookie(COOKIE_NAME)
    return resp
