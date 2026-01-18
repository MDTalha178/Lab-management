from jwt import ExpiredSignatureError, InvalidTokenError
from requests import Request
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError, AuthenticationFailed
from rest_framework_simplejwt.tokens import UntypedToken

from accounts.Interface.AuthenticationInterface import AuthenticationInterface
from accounts.models import User
from core.exception import CustomAuthenticationFailed


class JwtAuthenticationStrategy(AuthenticationInterface):
    """
    JwtAuthenticationStrategy - An implementation of AuthenticationInterface using JWT (JSON Web Token).

    Purpose:
    --------
    - Provides authentication mechanisms based on JWT.
    - Responsible for generating JWT tokens for authenticated users.
    - Responsible for validating provided JWT tokens.

    Usage Scenario:
    ---------------
    - This strategy is intended to be used when the system is configured to use JWT-based authentication.
    - Other authentication strategies (such as LDAP, OAuth2, SAML) can implement AuthenticationInterface differently.

    Key Methods:
    ------------
    - process_authentication(user): Generates a JWT token for a given user.
    - authenticate(token): Validates an incoming JWT token.

    Notes for Developers:
    ---------------------
    - The design follows the Strategy Pattern, enabling flexible authentication mechanisms.
    - This implementation relies on Django REST Framework SimpleJWT package for token generation/validation.
    - The interface is designed to allow future replacement with other authentication mechanisms without breaking business logic.
    """

    def __init__(self):
        super().__init__()

    def process_authentication(self, user):
        """
        Generate a JWT token for the authenticated user.

        This method is responsible for creating access and refresh tokens
        that can be used by the client for subsequent authenticated requests.

        Args:
            user: The authenticated user object (must be a valid Django User instance).

        Returns:
            dict: A dictionary containing:
                - 'access_token': A short-lived token for accessing protected resources.
                - 'refresh_token': A long-lived token for obtaining new access tokens.
                - 'user_id': The ID of the authenticated user.

        Example Response:
        -----------------
        {
            'access_token': 'eyJ0eXAiOiJKV1QiLCJh...',
            'refresh_token': 'eyJ0eXAiOiJKV1QiLCJh...',
            'user_id': 123
        }
        """
        pass

    def authenticate(self, request: Request):
        """
        Validate the provided JWT token.

        This method attempts to validate the incoming token.
        - If the token is valid, it returns the validated token object (which can be further decoded/inspected).
        - If the token is invalid, it raises a ValueError exception.

        Args:
            request (str): The JWT token (usually provided by the client in Authorization header).

        Returns:
            UntypedToken: The validated token object if valid.

        Raises:
            ValueError: If the token is invalid or expired.

        Example Usage:
        --------------
        try:
            validated_token = jwt_strategy.authenticate(token)
            # Proceed with request processing...
        except ValueError as e:
            # Handle invalid token scenario...
        """
        auth_header = request.headers.get("Authorization")

        # Fallback for older Django/DRF
        if not auth_header:
            auth_header = request.META.get("HTTP_AUTHORIZATION")

        if not auth_header or not auth_header.startswith('Bearer '):
            raise CustomAuthenticationFailed("Authorization Details is missing or invalid")

        token = auth_header.split(' ')[1]
        payload = self.token_validation(token)

        if not payload:
            raise CustomAuthenticationFailed("Token expired or Invalid")

        user_id = payload.get('user_id')
        if user_id is None:
            raise CustomAuthenticationFailed("Token expired or Invalid")

        try:
            request.user_id = user_id
            request.role = payload.get('role')
        except Exception:
            raise CustomAuthenticationFailed("User not found")
        current_user = self.get_user(user_id)
        from core.auth import AuthenticatedUser
        user = AuthenticatedUser(user_id, payload.get("role"), current_user)
        return user, token

    def token_validation(self, token):
        try:
            return UntypedToken(token)
        except (InvalidToken, TokenError, ExpiredSignatureError, InvalidTokenError):
            raise CustomAuthenticationFailed("Token expired or Invalid")

    def get_user(self, user_id):
        return User.objects.get(id=user_id)
