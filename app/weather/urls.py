
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from weather.views import WeatherViewSet

router = DefaultRouter()
router.register('', WeatherViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
