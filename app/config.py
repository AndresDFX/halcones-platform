"""Configuración central de la plataforma Halcones Paracaidismo."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Marca
    app_name: str = "Halcones Paracaidismo"
    app_tagline: str = "Escuela de Paracaidismo · Cali, Colombia"

    # Base de datos. En Docker se sobreescribe por variable de entorno.
    database_url: str = "sqlite:///./halcones.db"

    # Seguridad
    secret_key: str = "cambia-esta-clave-en-produccion-halcones-2026"
    access_token_expire_minutes: int = 60 * 12  # 12 horas
    jwt_algorithm: str = "HS256"

    # Archivos subidos (manuales, documentos, videos)
    upload_dir: str = "/app/uploads"
    max_upload_mb: int = 512

    # Semilla
    seed_on_startup: bool = True

    # Moneda por defecto
    currency: str = "COP"

    # ---- Correo (SMTP) para notificaciones ----
    # Si smtp_host queda vacío, las notificaciones se registran en modo "simulado"
    # (no se envían realmente) — la funcionalidad queda lista para activarse.
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "Halcones Paracaidismo <no-reply@halcones.co>"
    smtp_tls: bool = True

    # Token para disparar el cron de notificaciones desde Render Cron Job
    cron_secret: str = "halcones-cron-secret-cambiar"

    # URL pública (para enlaces en los correos). Se ajusta en producción.
    public_base_url: str = "http://localhost:8080"

    @property
    def smtp_configured(self) -> bool:
        return bool(self.smtp_host and self.smtp_user)


settings = Settings()
