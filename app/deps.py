from functools import lru_cache
from app.core.config import Settings
from app.services.cognito import CognitoService


@lru_cache()
def get_settings() -> Settings:
    return Settings()


@lru_cache()
def get_cognito_service() -> CognitoService:
    settings = get_settings()
    return CognitoService(settings)
