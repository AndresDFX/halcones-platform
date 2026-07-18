"""Dependencias de autenticación y autorización para las rutas."""
from fastapi import Depends, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .database import get_db
from .models import User, Role
from .security import decode_access_token, COOKIE_NAME


class AuthRedirect(Exception):
    """Señal interna para redirigir al login cuando no hay sesión en una página."""
    def __init__(self, location: str = "/login"):
        self.location = location


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    """Devuelve el usuario autenticado o None (no lanza error)."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    user = db.get(User, int(payload.get("sub", 0)))
    if not user or not user.activo:
        return None
    return user


def require_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Exige sesión iniciada; si no, redirige al login (para páginas HTML)."""
    user = get_current_user(request, db)
    if not user:
        raise AuthRedirect(f"/login?next={request.url.path}")
    return user


def require_roles(*roles: Role):
    """Genera una dependencia que exige uno de los roles indicados."""
    def _dep(request: Request, db: Session = Depends(get_db)) -> User:
        user = get_current_user(request, db)
        if not user:
            raise AuthRedirect(f"/login?next={request.url.path}")
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="No tienes permisos para acceder a esta sección.")
        return user
    return _dep


# Guards reutilizables
staff_required = require_roles(Role.admin, Role.instructor)
admin_required = require_roles(Role.admin)
