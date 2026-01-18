from abc import ABC, abstractmethod


class AuthenticationInterface(ABC):
    """
    AuthenticationInterface - Abstract base class for authentication strategies.

    Purpose:
    --------
    - Defines a standard interface for implementing different authentication mechanisms.
    - Allows the system to support multiple authentication strategies (e.g. JWT, OAuth2, LDAP, SAML, etc.)
      without changing business logic.
    - Enables the use of the Strategy Pattern to decouple authentication logic from application services.

    Usage:
    ------
    - Any new authentication strategy (JwtAuthenticationStrategy, OAuth2AuthenticationStrategy, etc.)
      must implement this interface.
    - Application services should depend on AuthenticationInterface rather than concrete implementations.
    - Enables flexibility to swap authentication strategies at runtime if needed.

    Methods:
    --------
    - process_authentication(credentials): Authenticate based on credentials.
    - authenticate(user): Generate an authentication artifact for a successfully authenticated user.

    Notes for Developers:
    ---------------------
    - process_authentication can support various input types:
        - username/password
        - API key
        - OAuth token exchange
    - authenticate can issue different forms of identity representation:
        - JWT token
        - OAuth2 access token
        - LDAP session ticket
        - SAML assertion
    - This is intentionally generic to avoid coupling the system to token-based auth only.
    """

    @abstractmethod
    def process_authentication(self, credentials: dict) -> bool:
        """
        Authenticate a user with the provided credentials.

        This method is responsible for validating incoming credentials
        and determining whether authentication is successful.

        Examples of 'credentials':
        - For username/password authentication:
            { "username": "johndoe", "password": "secret" }
        - For API key authentication:
            { "api_key": "abcdef123456" }
        - For OAuth token exchange:
            { "authorization_code": "xyz123", "redirect_uri": "https://app.example.com/callback" }

        Args:
            credentials (dict): A dictionary containing user credentials.

        Returns:
            bool: True if authentication is successful, False otherwise.

        Raises:
            Implementing classes may raise exceptions for invalid or malformed input.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")

    @abstractmethod
    def authenticate(self, user):
        """
        Authenticate a user object and return an identity artifact (token, ticket, assertion, etc.).

        This method is responsible for generating the identity representation for
        the authenticated user, which can then be used by clients for accessing protected resources.

        The format of the artifact depends on the concrete strategy:
        - For JWT-based auth → returns JWT token
        - For OAuth2 → returns access token
        - For LDAP → returns session ticket
        - For SAML → returns SAML assertion
        - For non-token systems → may return None or raise NotImplementedError

        Args:
            user: The authenticated user object (typically a User model instance).

        Returns:
            Any: An authentication artifact (such as a token or ticket) or None if not applicable.

        Raises:
            Implementing classes may raise exceptions if user is invalid or artifact generation fails.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")
