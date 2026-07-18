"""Utilidades varias (manejo de archivos subidos)."""
import os
import re
import unicodedata

from fastapi import UploadFile

from .config import settings


def _slug(name: str) -> str:
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    name = re.sub(r"[^a-zA-Z0-9._-]+", "-", name).strip("-")
    return name or "archivo"


def save_upload(file: UploadFile, subdir: str = "") -> str:
    """Guarda el archivo en uploads/<subdir> y devuelve la ruta relativa."""
    dest_dir = os.path.join(settings.upload_dir, subdir)
    os.makedirs(dest_dir, exist_ok=True)
    filename = _slug(os.path.basename(file.filename or "archivo"))
    # Evitar colisiones
    path = os.path.join(dest_dir, filename)
    stem, ext = os.path.splitext(filename)
    i = 1
    while os.path.exists(path):
        filename = f"{stem}-{i}{ext}"
        path = os.path.join(dest_dir, filename)
        i += 1
    with open(path, "wb") as out:
        out.write(file.file.read())
    rel = os.path.relpath(path, settings.upload_dir).replace("\\", "/")
    return rel
