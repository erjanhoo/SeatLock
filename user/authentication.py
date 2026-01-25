from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone

from .models import AccessToken


class TokenAuthentication(BaseAuthentication):
    keyword = "Token"

    def authenticate(self, request):
        header = request.headers.get("Authorization", "")
        if not header:
            return None

        parts = header.split()
        if len(parts) != 2:
            raise AuthenticationFailed("Invalid authorization header")

        scheme, token_key = parts
        if scheme.lower() not in {"token", "bearer"}:
            return None

        try:
            token = AccessToken.objects.select_related("user").get(key=token_key)
        except AccessToken.DoesNotExist:
            raise AuthenticationFailed("Invalid token")

        if token.revoked_at is not None:
            raise AuthenticationFailed("Token revoked")

        if token.expires_at <= timezone.now():
            raise AuthenticationFailed("Token expired")

        if not token.user.is_active:
            raise AuthenticationFailed("User inactive")

        return token.user, token
