from fastapi import FastAPI
from app.api.v1 import auth as auth_router
from app.core.logging import configure_logging
from app.core.config import Settings
from app.middleware.auth import AuthMiddleware

settings = Settings()
configure_logging(settings)

app = FastAPI(title="FastAPI Cognito Auth Service")

# Attach auth middleware to validate tokens and populate `request.state.user` when present
app.add_middleware(AuthMiddleware, settings=settings)

app.include_router(auth_router.router, prefix="/api/v1/auth")


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.ENV}