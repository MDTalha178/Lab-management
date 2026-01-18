from rest_framework.permissions import AllowAny

from accounts.AuthStrategy.JwtAuthStrategy import JwtAuthenticationStrategy
from accounts.Interface.AuthenticationInterface import AuthenticationInterface
from accounts.serializer import LoginSerializer, UserSerializer
from core.utils import CustomModelView


class LoginViewSet(CustomModelView):
    """
    ViewSet responsible for handling user login requests.

    This view accepts login credentials and performs the following:
    - Validates login data via serializer.
    - Uses role-based validation strategy internally.
    - Authenticates the user via an authentication strategy (e.g., JWT).
    - Returns a token and user details upon successful authentication.

    HTTP Method Supported:
        - POST: Authenticate user and return auth token.
    """

    http_method_names = ('post',)
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        """
        Initialize the LoginViewSet with the desired authentication strategy.

        This allows support for different token generation mechanisms (e.g., JWT, OAuth).
        """
        super().__init__(**kwargs)
        self.auth_strategy: AuthenticationInterface = JwtAuthenticationStrategy()

    def create(self, request, *args, **kwargs):
        """
        Handle POST request for user login.

        Steps:
        1. Deserialize and validate the input data.
        2. Retrieve the validated user.
        3. Generate a token using the authentication strategy.
        4. Serialize the user and return a success response with token.

        Args:
            request (Request): The HTTP request object containing login credentials.

        Returns:
            Response: Success or failure response with appropriate status and message.
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            # Get the validated user instance
            user = serializer.validated_data.get('user')

            # Generate authentication token (e.g., JWT)
            token_response = self.auth_strategy.process_authentication(user)

            # Serialize user data
            serialized_data = UserSerializer(instance=user, many=False)

            # Merge user data and token into the response
            return self.success_response(
                data={**serialized_data.data, **token_response}
            )

        # If serializer is not valid, return error details
        return self.failure_response(data=serializer.errors)