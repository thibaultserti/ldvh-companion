"""Configuration de l'application LDVH Companion."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration de l'application avec validation Pydantic."""

    # Informations de base
    app_name: str = "LDVH Companion"
    app_version: str = "0.1.0"
    debug: bool = False

    # Configuration de la base de données
    database_url: str = "sqlite:///./ldvh_companion.db"

    # Configuration du serveur
    host: str = "0.0.0.0"
    port: int = 8000

    # Sécurité
    secret_key: str | None = None
    environment: str = "development"

    class Config:
        """Configuration Pydantic."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Instance globale des paramètres
settings = Settings()


def get_database_url() -> str:
    """Retourne l'URL de la base de données."""
    return settings.database_url


def is_development() -> bool:
    """Retourne True si l'application est en mode développement."""
    return settings.environment.lower() == "development"


def is_production() -> bool:
    """Retourne True si l'application est en mode production."""
    return settings.environment.lower() == "production"
