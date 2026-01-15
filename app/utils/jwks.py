import time
import requests
from authlib.jose import JsonWebKey, jwt
from typing import Dict, Optional
from fastapi import HTTPException, status
from app.core.config import Settings
import base64
import json


class JWKSClient:
    """JWKS client with caching and strict claim validation for Cognito tokens.

    It validates signature, `exp`/`nbf`, and enforces `iss`, `aud` and `token_use` claims.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.jwks = None
        self.jwks_fetched_at = 0
        self.ttl = 3600
        self.jwks_url = (
            settings.JWKS_URL
            or f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
        )

    def _fetch(self) -> None:
        resp = requests.get(self.jwks_url, timeout=5)
        resp.raise_for_status()
        self.jwks = resp.json()
        self.jwks_fetched_at = time.time()

    def _ensure(self) -> None:
        if not self.jwks or (time.time() - self.jwks_fetched_at) > self.ttl:
            self._fetch()

    def _get_unverified_header(self, token: str) -> Dict:
        """Minimal manual JWT header extraction (base64url decode).

        This avoids depending on a library helper that may not exist on the imported
        `jwt` object from Authlib.
        """
        try:
            header_b64 = token.split(".")[0]
            # Add padding if necessary
            padding = "=" * (-len(header_b64) % 4)
            header_bytes = base64.urlsafe_b64decode(header_b64 + padding)
            return json.loads(header_bytes)
        except Exception as exc:  # pragma: no cover - defensive
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token header: {exc}")

    def verify_jwt(
        self, token: str, expected_audience: Optional[str] = None, expected_token_use: Optional[str] = None
    ) -> Dict:
        """Verify a JWT and enforce issuer, audience and token_use.

        Raises HTTPException(401) on failures.
        """
        try:
            self._ensure()
            header = self._get_unverified_header(token)
            kid = header.get("kid")
            keys = {k["kid"]: k for k in self.jwks.get("keys", [])}
            key = keys.get(kid)
            if not key:
                # refresh and retry once
                self._fetch()
                keys = {k["kid"]: k for k in self.jwks.get("keys", [])}
                key = keys.get(kid)
                if not key:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: unknown kid")

            jwk = JsonWebKey.import_key(key)
            claims = jwt.decode(token, jwk)
            # validate exp/nbf etc.
            claims.validate()

            # Validate issuer
            issuer = f"https://cognito-idp.{self.settings.AWS_REGION}.amazonaws.com/{self.settings.COGNITO_USER_POOL_ID}"
            if claims.get("iss") != issuer:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token issuer")

            # Validate audience (client id) if provided or default to configured client id
            aud = claims.get("aud") or claims.get("client_id")
            expected_aud = expected_audience or self.settings.COGNITO_CLIENT_ID
            if expected_aud and aud != expected_aud:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token audience")

            # Validate token_use
            token_use = claims.get("token_use")
            if expected_token_use:
                if token_use != expected_token_use:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token use")
            else:
                # Ensure token_use exists and is one of allowed values
                if token_use not in ("id", "access"):
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token use")

            return dict(claims)

        except HTTPException:
            raise
        except Exception as exc:  # pylint: disable=broad-except
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token verification failed: {str(exc)}")
