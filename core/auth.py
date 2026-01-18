from rest_framework.authentication import BaseAuthentication

from core.public_url import PUBLIC_URL


class AuthenticatedUser:
    def __init__(self, user_id, role, user, is_authenticated=True):
        self.id = user_id
        self.role = role
        self.pk = user_id
        self.is_authenticated = is_authenticated
        self.tenant = user.tenant
        self.is_staff = user.is_staff

    def __str__(self):
        return f"User(id={self.id}, role={self.role})"


class AuthenticationService(BaseAuthentication):
    def __init__(self):
        self.auth_strategy = None

    def get_auth_strategy(self):
        if self.auth_strategy is None:
            from core.jwt_auth import JwtAuthenticationStrategy
            self.auth_strategy = JwtAuthenticationStrategy()
        return self.auth_strategy

    def authenticate(self, request):
        if any(request.path.startswith(path) for path in PUBLIC_URL):
            return None
        from core.exception import CustomAuthenticationFailed
        try:
            return self.get_auth_strategy().authenticate(request)
        except CustomAuthenticationFailed as custom_auth:
            raise custom_auth
