from django.urls import path, include
from rest_framework.routers import DefaultRouter
from airport.views import AircraftViewSet, StateChangeLogViewSet

router = DefaultRouter()
router.register('', AircraftViewSet)
router.register('state_logs', StateChangeLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
