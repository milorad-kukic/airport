from django.urls import path, include
from rest_framework.routers import DefaultRouter
from airport.views import AircraftViewSet

router = DefaultRouter()
router.register('', AircraftViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
