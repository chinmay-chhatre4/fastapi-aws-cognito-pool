from fastapi import Request, HTTPException
from fastapi.security.utils import get_authorization_scheme_param
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.core.config import Settings
from app.utils.jwks import JWKSClient


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: Settings):
        super().__init__(app)
        self.settings = settings
        self.jwks = JWKSClient(settings)

    async def dispatch(self, request: Request, call_next):
        # Skip health
        if request.url.path.startswith("/health"):
            return await call_next(request)

        auth = request.headers.get("authorization")
        if not auth:
            return await call_next(request)

        scheme, token = get_authorization_scheme_param(auth)
        if not token or scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth header")

        # Validate token signature and claims; raise if invalid
        claims = self.jwks.verify_jwt(token)
        request.state.user = claims
        return await call_next(request)
