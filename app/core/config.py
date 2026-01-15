import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    AWS_REGION: str = Field(..., env="AWS_REGION")
    AWS_ACCESS_KEY_ID: str | None = Field(None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str | None = Field(None, env="AWS_SECRET_ACCESS_KEY")
    COGNITO_USER_POOL_ID: str = Field(..., env="COGNITO_USER_POOL_ID")
    COGNITO_CLIENT_ID: str = Field(..., env="COGNITO_CLIENT_ID")
    COGNITO_CLIENT_SECRET: str | None = Field(None, env="COGNITO_CLIENT_SECRET")
    JWKS_URL: str | None = Field(None, env="JWKS_URL")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    ENV: str = Field("development", env="ENV")
    PORT: int = Field(8000, env="PORT")

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.getcwd(), ".env"),
        extra="ignore"   # 👈 THIS IS THE FIX
    )
    