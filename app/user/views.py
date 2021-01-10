from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Creat a new auth token for user"""
    serializer_class = AuthTokenSerializer
    # Set the renderer so we can see the api in the browser
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
