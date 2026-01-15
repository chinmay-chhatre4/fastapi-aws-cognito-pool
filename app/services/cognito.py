import base64
import hashlib
import hmac
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from app.core.config import Settings


class CognitoService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = boto3.client("cognito-idp", region_name=settings.AWS_REGION)

    def _secret_hash(self, username: str) -> Optional[str]:
        if not self.settings.COGNITO_CLIENT_SECRET:
            return None
        msg = username + self.settings.COGNITO_CLIENT_ID
        dig = hmac.new(self.settings.COGNITO_CLIENT_SECRET.encode("utf-8"), msg.encode("utf-8"), hashlib.sha256).digest()
        return base64.b64encode(dig).decode()

    def sign_up(self, username: str, password: str, email: str):
        params = dict(
            ClientId=self.settings.COGNITO_CLIENT_ID,
            Username=username,
            Password=password,
            UserAttributes=[{"Name": "email", "Value": email}],
        )
        secret = self._secret_hash(username)
        if secret:
            params["SecretHash"] = secret
        return self.client.sign_up(**params)

    def confirm_sign_up(self, username: str, confirmation_code: str):
        params = dict(
            ClientId=self.settings.COGNITO_CLIENT_ID,
            Username=username,
            ConfirmationCode=confirmation_code,
        )
        secret = self._secret_hash(username)
        if secret:
            params["SecretHash"] = secret
        return self.client.confirm_sign_up(**params)

    def resend_confirmation(self, username: str):
        params = dict(ClientId=self.settings.COGNITO_CLIENT_ID, Username=username)
        secret = self._secret_hash(username)
        if secret:
            params["SecretHash"] = secret
        return self.client.resend_confirmation_code(**params)

    def initiate_auth(self, username: str, password: str):
        secret = self._secret_hash(username)
        auth_params = {"USERNAME": username, "PASSWORD": password}
        if secret:
            auth_params["SECRET_HASH"] = secret
        return self.client.initiate_auth(
            ClientId=self.settings.COGNITO_CLIENT_ID,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters=auth_params,
        )

    def forgot_password(self, username: str):
        params = dict(ClientId=self.settings.COGNITO_CLIENT_ID, Username=username)
        secret = self._secret_hash(username)
        if secret:
            params["SecretHash"] = secret
        return self.client.forgot_password(**params)

    def confirm_forgot_password(self, username: str, confirmation_code: str, new_password: str):
        params = dict(
            ClientId=self.settings.COGNITO_CLIENT_ID,
            Username=username,
            ConfirmationCode=confirmation_code,
            Password=new_password,
        )
        secret = self._secret_hash(username)
        if secret:
            params["SecretHash"] = secret
        return self.client.confirm_forgot_password(**params)

    def change_password(self, access_token: str, previous_password: str, proposed_password: str):
        return self.client.change_password(
            PreviousPassword=previous_password, ProposedPassword=proposed_password, AccessToken=access_token
        )

    def global_sign_out(self, access_token: str):
        return self.client.global_sign_out(AccessToken=access_token)
