from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken

from accounts.Interface.AuthenticationInterface import AuthenticationInterface


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
        refresh_token = RefreshToken.for_user(user)
        refresh_token['role'] = user.role
        token_dict = {
            'access_token': str(refresh_token.access_token),
            'refresh_token': str(refresh_token),
            'user_id': user.id,
            'role': user.role
        }

        return token_dict

    def authenticate(self, token):
        """
        Validate the provided JWT token.

        This method attempts to validate the incoming token.
        - If the token is valid, it returns the validated token object (which can be further decoded/inspected).
        - If the token is invalid, it raises a ValueError exception.

        Args:
            token (str): The JWT token (usually provided by the client in Authorization header).

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
        try:
            validated_token = UntypedToken(token)
            return validated_token
        except Exception as e:
            raise ValueError(f"Invalid token: {str(e)}") from e
