import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = os.getenv("APP_NAME", "CLFMS")
    debug: bool = os.getenv("DEBUG", "true").lower() in ("1", "true", "yes")

    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    jwt_algorithm: str = os.getenv("ALGORITHM", "HS256")
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./clfms.db")

    company_state: str = os.getenv("COMPANY_STATE", "KA")  # Karnataka (default)
    default_admin_email: str = os.getenv("ADMIN_EMAIL", "admin@local")
    default_admin_password: str = os.getenv("ADMIN_PASSWORD", "admin123")
    default_admin_role: str = os.getenv("ADMIN_ROLE", "admin")

    gst_cgst_rate: float = float(os.getenv("GST_CGST_RATE", "0.09"))
    gst_sgst_rate: float = float(os.getenv("GST_SGST_RATE", "0.09"))
    gst_igst_rate: float = float(os.getenv("GST_IGST_RATE", "0.18"))

    cors_origins: list[str] = []


settings = Settings()
