from dataclasses import dataclass

import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed


@dataclass
class ServiceUser:
    id: int

    @property
    def is_authenticated(self):
        return True


class ServiceJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth:
            return None
        if auth[0].lower() != b"bearer" or len(auth) != 2:
            raise AuthenticationFailed("Invalid authorization header.")

        try:
            payload = jwt.decode(auth[1], settings.JWT_SIGNING_KEY, algorithms=["HS256"])
        except jwt.PyJWTError as exc:
            raise AuthenticationFailed("Invalid or expired token.") from exc

        if payload.get("token_type") != "access":
            raise AuthenticationFailed("Access token required.")

        user_id = payload.get("user_id")
        if user_id is None:
            raise AuthenticationFailed("Token missing user_id.")

        return ServiceUser(id=int(user_id)), payload
