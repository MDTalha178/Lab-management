from accounts.views import LoginViewSet


from django.urls import path, include
from rest_framework import routers

router = routers.DefaultRouter()

router.register('login', LoginViewSet, basename='login')

urlpatterns = [
    path(r'', include(router.urls)),
]