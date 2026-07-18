"""Configuración de SQLAlchemy (engine, sesión, Base)."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings


def _normalize_db_url(url: str) -> str:
    """Normaliza la URL a un driver soportado.

    Render/Neon/Supabase entregan cadenas 'postgres://' o 'postgresql://' (driver
    por defecto psycopg2). Este proyecto usa psycopg v3, así que forzamos el
    driver '+psycopg'.
    """
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


DATABASE_URL = _normalize_db_url(settings.database_url)

# SQLite necesita connect_args especial; Postgres no.
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_db():
    """Dependencia FastAPI que entrega una sesión de BD por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
