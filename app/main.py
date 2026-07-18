"""Punto de entrada de la plataforma Halcones Paracaidismo."""
import os

import os as _os

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import Base, engine, SessionLocal
from .deps import AuthRedirect
from .templating import templates
from .routers import (auth, dashboard, courses, students, finance, manifest, portal,
                      api, users, instructor, notifications, public)
from . import seed as seed_module

app = FastAPI(
    title="Halcones Paracaidismo · Plataforma",
    description="Plataforma integral de gestión de cursos, estudiantes, finanzas y "
                "programación de saltos para Halcones Paracaidismo (Cali, Colombia).",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Archivos estáticos y subidos
app.mount("/static", StaticFiles(directory="app/static"), name="static")
os.makedirs(settings.upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    if settings.seed_on_startup:
        db = SessionLocal()
        try:
            seed_module.seed(db)
        finally:
            db.close()


# Redirección al login cuando una página exige sesión y no la hay
@app.exception_handler(AuthRedirect)
async def auth_redirect_handler(request: Request, exc: AuthRedirect):
    return RedirectResponse(exc.location, status_code=303)


# Página 403 amigable
from fastapi.exceptions import HTTPException as FastAPIHTTPException  # noqa: E402


@app.exception_handler(FastAPIHTTPException)
async def http_exception_handler(request: Request, exc: FastAPIHTTPException):
    if exc.status_code == 403 and "text/html" in request.headers.get("accept", ""):
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "user": None, "code": 403,
             "mensaje": exc.detail or "Acceso denegado"},
            status_code=403,
        )
    if exc.status_code == 404 and "text/html" in request.headers.get("accept", ""):
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "user": None, "code": 404,
             "mensaje": "La página que buscas no existe."},
            status_code=404,
        )
    return HTMLResponse(f"<h1>{exc.status_code}</h1><p>{exc.detail}</p>",
                        status_code=exc.status_code)


# Rutas
app.include_router(public.router)
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(courses.router)
app.include_router(students.router)
app.include_router(users.router)
app.include_router(finance.router)
app.include_router(instructor.router)
app.include_router(notifications.router)
app.include_router(manifest.router)
app.include_router(portal.router)
app.include_router(api.router)


@app.get("/healthz", include_in_schema=False)
def healthz():
    return {"status": "ok", "app": settings.app_name}


# ---- PWA: service worker en la raíz (alcance "/") y página offline ----
_STATIC = _os.path.join(_os.path.dirname(__file__), "static")


@app.get("/sw.js", include_in_schema=False)
def service_worker():
    return FileResponse(
        _os.path.join(_STATIC, "sw.js"),
        media_type="application/javascript",
        headers={"Service-Worker-Allowed": "/", "Cache-Control": "no-cache"},
    )


@app.get("/manifest.webmanifest", include_in_schema=False)
def manifest():
    return FileResponse(
        _os.path.join(_STATIC, "manifest.webmanifest"),
        media_type="application/manifest+json",
    )


@app.get("/offline", include_in_schema=False)
def offline(request: Request):
    return templates.TemplateResponse("offline.html", {"request": request, "user": None})
