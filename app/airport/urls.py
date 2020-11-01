from django.urls import path, include
from rest_framework.routers import DefaultRouter
from airport.views import AircraftViewSet, StateChangeLogViewSet, StartSimulationViewSet

router = DefaultRouter()
router.register('', AircraftViewSet)
router.register('state_logs', StateChangeLogViewSet)
router.register('simulation', StartSimulationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
