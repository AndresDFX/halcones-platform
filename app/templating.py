"""Configuración de Jinja2 con filtros y contexto de marca."""
from datetime import date, datetime

from fastapi.templating import Jinja2Templates

from .config import settings

templates = Jinja2Templates(directory="app/templates")


def format_cop(value) -> str:
    """Formatea un número como pesos colombianos: $ 6.333.333"""
    try:
        n = float(value or 0)
    except (TypeError, ValueError):
        return "$ 0"
    entero = int(round(n))
    s = f"{entero:,}".replace(",", ".")
    return f"$ {s}"


def format_num(value) -> str:
    try:
        return f"{int(round(float(value or 0))):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "0"


MESES = ["", "ene", "feb", "mar", "abr", "may", "jun",
         "jul", "ago", "sep", "oct", "nov", "dic"]


def format_fecha(value) -> str:
    if not value:
        return "—"
    if isinstance(value, (date, datetime)):
        return f"{value.day} {MESES[value.month]} {value.year}"
    return str(value)


def format_fecha_larga(value) -> str:
    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    meses_l = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
               "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    if isinstance(value, (date, datetime)):
        return f"{dias[value.weekday()]} {value.day} de {meses_l[value.month]} de {value.year}"
    return str(value or "—")


templates.env.filters["cop"] = format_cop
templates.env.filters["num"] = format_num
templates.env.filters["fecha"] = format_fecha
templates.env.filters["fecha_larga"] = format_fecha_larga
templates.env.globals["APP_NAME"] = settings.app_name
templates.env.globals["APP_TAGLINE"] = settings.app_tagline
templates.env.globals["now"] = datetime.utcnow


def render(request, name: str, user=None, **ctx):
    """Atajo para renderizar una plantilla inyectando request y usuario."""
    base = {"request": request, "user": user}
    base.update(ctx)
    return templates.TemplateResponse(name, base)
