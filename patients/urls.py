from django.urls import path, include
from rest_framework.routers import DefaultRouter

from patients.views import PatientViewSet, TestViewSet, SampleViewSet

router = DefaultRouter()
router.register(r'patient', PatientViewSet, basename='patient')
router.register(r'tests', TestViewSet, basename='tests')
router.register(r'sample', SampleViewSet, basename='sample')

urlpatterns = [
    path('', include(router.urls)),
]