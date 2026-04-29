import os
import secrets
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("clfms")

_WEAK_SECRETS = {"dev-secret-change-me", "secret", "changeme", "supersecret", "test-secret-key", ""}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = os.getenv("APP_NAME", "CLFMS")
    debug: bool = os.getenv("DEBUG", "true").lower() in ("1", "true", "yes")
    environment: str = os.getenv("ENVIRONMENT", "development").lower().strip()
    seed_default_admin: bool = os.getenv("SEED_DEFAULT_ADMIN", "false").lower() in ("1", "true", "yes")

    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    jwt_algorithm: str = os.getenv("ALGORITHM", "HS256")
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./clfms.db")

    company_state: str = os.getenv("COMPANY_STATE", "KA")  # Karnataka (default)
    default_admin_email: str = os.getenv("ADMIN_EMAIL", "admin@clfms.local")
    default_admin_password: str = os.getenv("ADMIN_PASSWORD", "admin123")
    default_admin_role: str = os.getenv("ADMIN_ROLE", "admin")

    gst_cgst_rate: float = float(os.getenv("GST_CGST_RATE", "0.09"))
    gst_sgst_rate: float = float(os.getenv("GST_SGST_RATE", "0.09"))
    gst_igst_rate: float = float(os.getenv("GST_IGST_RATE", "0.18"))

    cors_origins_raw: str = os.getenv("CORS_ORIGINS", "")

    # SMTP email settings (for OTP verification emails)
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.hostinger.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "465"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from: str = os.getenv("SMTP_FROM", "admin@magnetarai.online")
    app_base_url: str = os.getenv("APP_BASE_URL", "https://magnetarai.online")

    def __init__(self, **values):
        super().__init__(**values)
        is_prod = self.environment in {"production", "prod"}
        cors_origins = self.cors_origins
        if self.secret_key in _WEAK_SECRETS or len(self.secret_key) < 32:
            if not self.debug:
                raise RuntimeError(
                    "SECRET_KEY is insecure. Set a strong SECRET_KEY (>=32 chars) in your .env before running in production."
                )
            else:
                logger.warning(
                    "WARNING: SECRET_KEY is weak or default. Set a strong SECRET_KEY in .env. "
                    "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
                )
        if self.default_admin_password in ("admin123", "password", "admin", ""):
            logger.warning(
                "WARNING: Default admin password 'admin123' is in use. "
                "Change ADMIN_PASSWORD in .env before deploying."
            )
        if is_prod and not cors_origins:
            raise RuntimeError(
                "CORS_ORIGINS is not configured for production. "
                "Set CORS_ORIGINS in .env to your trusted frontend origin(s)."
            )

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins_raw.split(",")
            if origin.strip()
        ]


settings = Settings()
